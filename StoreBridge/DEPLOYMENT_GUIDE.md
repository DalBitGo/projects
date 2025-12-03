# 배포 가이드 (Deployment Guide)

> StoreBridge CI/CD 파이프라인 및 인프라 구성

**작성일**: 2025-10-16
**Target**: AWS EKS / Docker Compose (로컬)
**버전**: 1.0

---

## 목차

1. [배포 전략](#배포-전략)
2. [환경 구성](#환경-구성)
3. [Docker 구성](#docker-구성)
4. [CI/CD 파이프라인](#cicd-파이프라인)
5. [Kubernetes 구성](#kubernetes-구성)
6. [모니터링 & 로깅](#모니터링--로깅)
7. [배포 체크리스트](#배포-체크리스트)

---

## 배포 전략

### 환경별 전략

| 환경 | 용도 | 배포 방식 | 승인 |
|------|------|-----------|------|
| **dev** | 개발 테스트 | 자동 (main push) | 불필요 |
| **staging** | QA/통합 테스트 | 자동 (release/* push) | 불필요 |
| **production** | 실서비스 | 수동 (태그 생성 시) | 필수 |

### 롤링 배포 (Rolling Update)

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # 최대 1개 추가 Pod
    maxUnavailable: 0  # 무중단 배포
```

### 카나리 배포 (Canary Deployment)

```
1. 신규 버전 1개 Pod 배포 (10% 트래픽)
2. 5분 모니터링 (에러율, 응답시간)
3. 문제 없으면 점진적 확대 (20% → 50% → 100%)
4. 문제 발생 시 즉시 롤백
```

### 블루-그린 배포 (Blue-Green Deployment)

```
Production (Blue)
  ↓
New Version (Green) 배포
  ↓
Health Check 통과
  ↓
트래픽 전환 (Blue → Green)
  ↓
Blue 유지 (롤백 대비, 10분)
  ↓
Blue 종료
```

---

## 환경 구성

### 환경 변수 관리

#### .env 파일 (로컬 개발)

```.env
# .env.example
ENVIRONMENT=development

# 도매꾹 API
DOMEGGOOK_API_KEY=your_api_key_here

# 네이버 커머스 API
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/storebridge
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis
REDIS_URL=redis://localhost:6379
REDIS_MAX_CONNECTIONS=50

# S3 / MinIO
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=admin
S3_SECRET_KEY=password
S3_BUCKET=storebridge-images
S3_REGION=us-east-1

# JWT
JWT_SECRET_KEY=super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Sentry
SENTRY_DSN=https://...@sentry.io/...
SENTRY_ENVIRONMENT=development

# 로그 레벨
LOG_LEVEL=INFO
LOG_FORMAT=json

# Rate Limit 설정
DOMEGGOOK_MAX_TPS=3
NAVER_MAX_TPS=2

# 재시도 설정
MAX_RETRIES=3
RETRY_BACKOFF_BASE=300

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_WORKER_CONCURRENCY=4
```

#### Kubernetes Secrets

```bash
# Secret 생성
kubectl create secret generic storebridge-secrets \
  --from-literal=domeggook-api-key='...' \
  --from-literal=naver-client-id='...' \
  --from-literal=naver-client-secret='...' \
  --from-literal=database-url='postgresql://...' \
  --from-literal=jwt-secret-key='...' \
  --from-literal=sentry-dsn='...' \
  --namespace=storebridge

# ConfigMap 생성 (비밀 아닌 설정)
kubectl create configmap storebridge-config \
  --from-literal=environment='production' \
  --from-literal=log-level='INFO' \
  --from-literal=domeggook-max-tps='3' \
  --from-literal=naver-max-tps='2' \
  --namespace=storebridge
```

---

## Docker 구성

### Dockerfile

```dockerfile
# Dockerfile

# Multi-stage build
FROM python:3.11-slim AS builder

WORKDIR /app

# 의존성 설치 (캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 런타임 이미지
FROM python:3.11-slim

WORKDIR /app

# 비root 사용자 생성
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# 빌더에서 의존성 복사
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# 애플리케이션 코드 복사
COPY --chown=appuser:appuser . .

# 사용자 전환
USER appuser

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 포트 노출
EXPOSE 8000

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml (로컬 개발)

```yaml
# docker-compose.yml
version: '3.9'

services:
  # Web API
  web:
    build:
      context: .
      dockerfile: Dockerfile
    image: storebridge-web:latest
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/storebridge
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=development
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./app:/app/app  # 핫 리로드용
    networks:
      - storebridge

  # Celery Worker (Normal Queue)
  worker-normal:
    build:
      context: .
      dockerfile: Dockerfile
    image: storebridge-worker:latest
    command: celery -A app.workers worker -Q normal -c 4 --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/storebridge
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    networks:
      - storebridge
    deploy:
      replicas: 2

  # Celery Worker (Batch Queue)
  worker-batch:
    build:
      context: .
      dockerfile: Dockerfile
    image: storebridge-worker:latest
    command: celery -A app.workers worker -Q batch -c 2 --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/storebridge
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    networks:
      - storebridge

  # Celery Beat (Scheduler)
  beat:
    build:
      context: .
      dockerfile: Dockerfile
    image: storebridge-beat:latest
    command: celery -A app.workers beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/storebridge
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    networks:
      - storebridge

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: storebridge
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - storebridge
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d storebridge"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - storebridge
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # MinIO (S3 호환)
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: password
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    networks:
      - storebridge
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/alerting_rules.yml:/etc/prometheus/alerting_rules.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - storebridge

  # Grafana
  grafana:
    image: grafana/grafana:latest
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_INSTALL_PLUGINS: grafana-piechart-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    networks:
      - storebridge

  # Loki (로그 수집)
  loki:
    image: grafana/loki:latest
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./monitoring/loki-config.yaml:/etc/loki/local-config.yaml
      - loki_data:/loki
    ports:
      - "3100:3100"
    networks:
      - storebridge

volumes:
  postgres_data:
  redis_data:
  minio_data:
  prometheus_data:
  grafana_data:
  loki_data:

networks:
  storebridge:
    driver: bridge
```

### .dockerignore

```
# .dockerignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.git/
.gitignore
.dockerignore
Dockerfile
docker-compose*.yml
.env
.env.*
*.md
tests/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/
*.log
```

---

## CI/CD 파이프라인

### GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop, 'release/**']
    tags: ['v*']
  pull_request:
    branches: [main, develop]

env:
  DOCKER_REGISTRY: ghcr.io
  IMAGE_NAME: storebridge

jobs:
  # 1. 린트 & 테스트
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint with Ruff
        run: ruff check app/

      - name: Type check with Mypy
        run: mypy app/ --strict

      - name: Run tests
        run: |
          pytest tests/ \
            --cov=app \
            --cov-report=xml \
            --cov-report=html \
            -v

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  # 2. 보안 스캔
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Bandit (Security)
        run: |
          pip install bandit
          bandit -r app/ -f json -o bandit-report.json

      - name: Run Trivy (Container Scan)
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # 3. Docker 빌드 & 푸시
  build-and-push:
    needs: [lint-and-test, security-scan]
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.DOCKER_REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.DOCKER_REGISTRY }}/${{ github.repository }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # 4. 배포 (dev/staging)
  deploy-dev:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: dev
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig \
            --name storebridge-dev-cluster \
            --region us-east-1

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/storebridge-web \
            web=${{ env.DOCKER_REGISTRY }}/${{ github.repository }}/${{ env.IMAGE_NAME }}:develop \
            -n storebridge-dev

          kubectl rollout status deployment/storebridge-web \
            -n storebridge-dev \
            --timeout=5m

      - name: Run smoke tests
        run: |
          sleep 30
          curl -f https://dev-api.storebridge.com/health || exit 1

  # 5. 배포 (production) - 수동 승인 필요
  deploy-production:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    environment:
      name: production
      url: https://api.storebridge.com
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig \
            --name storebridge-prod-cluster \
            --region us-east-1

      - name: Deploy to Kubernetes (Rolling Update)
        run: |
          kubectl set image deployment/storebridge-web \
            web=${{ env.DOCKER_REGISTRY }}/${{ github.repository }}/${{ env.IMAGE_NAME }}:${GITHUB_REF#refs/tags/} \
            -n storebridge-prod

          kubectl rollout status deployment/storebridge-web \
            -n storebridge-prod \
            --timeout=10m

      - name: Run smoke tests
        run: |
          sleep 60
          curl -f https://api.storebridge.com/health || exit 1

      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: |
            배포 완료: ${{ github.ref }}
            결과: ${{ job.status }}
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Kubernetes 구성

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: storebridge-prod
  labels:
    name: storebridge
    environment: production
```

### Deployment (Web)

```yaml
# k8s/deployment-web.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: storebridge-web
  namespace: storebridge-prod
  labels:
    app: storebridge
    component: web
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: storebridge
      component: web
  template:
    metadata:
      labels:
        app: storebridge
        component: web
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: storebridge-sa
      containers:
      - name: web
        image: ghcr.io/yourorg/storebridge:v1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: storebridge-config
              key: environment
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: storebridge-secrets
              key: database-url
        - name: REDIS_URL
          value: redis://storebridge-redis:6379
        envFrom:
        - configMapRef:
            name: storebridge-config
        - secretRef:
            name: storebridge-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 10"]  # Graceful shutdown
      terminationGracePeriodSeconds: 30
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: component
                  operator: In
                  values:
                  - web
              topologyKey: kubernetes.io/hostname
```

### Deployment (Worker)

```yaml
# k8s/deployment-worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: storebridge-worker-normal
  namespace: storebridge-prod
spec:
  replicas: 4
  selector:
    matchLabels:
      app: storebridge
      component: worker
      queue: normal
  template:
    metadata:
      labels:
        app: storebridge
        component: worker
        queue: normal
    spec:
      containers:
      - name: worker
        image: ghcr.io/yourorg/storebridge:v1.0.0
        command: ["celery", "-A", "app.workers", "worker", "-Q", "normal", "-c", "4"]
        envFrom:
        - configMapRef:
            name: storebridge-config
        - secretRef:
            name: storebridge-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "1000m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: storebridge-worker-batch
  namespace: storebridge-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: storebridge
      component: worker
      queue: batch
  template:
    metadata:
      labels:
        app: storebridge
        component: worker
        queue: batch
    spec:
      containers:
      - name: worker
        image: ghcr.io/yourorg/storebridge:v1.0.0
        command: ["celery", "-A", "app.workers", "worker", "-Q", "batch", "-c", "2"]
        envFrom:
        - configMapRef:
            name: storebridge-config
        - secretRef:
            name: storebridge-secrets
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

### Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: storebridge-web
  namespace: storebridge-prod
  labels:
    app: storebridge
    component: web
spec:
  type: ClusterIP
  ports:
  - name: http
    port: 80
    targetPort: 8000
    protocol: TCP
  selector:
    app: storebridge
    component: web
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: storebridge-ingress
  namespace: storebridge-prod
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.storebridge.com
    secretName: storebridge-tls
  rules:
  - host: api.storebridge.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: storebridge-web
            port:
              number: 80
```

### HorizontalPodAutoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: storebridge-web-hpa
  namespace: storebridge-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: storebridge-web
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 2
        periodSeconds: 15
      selectPolicy: Max
```

---

## 모니터링 & 로깅

### Prometheus 설정

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093

rule_files:
  - /etc/prometheus/alerting_rules.yml

scrape_configs:
  # FastAPI 메트릭
  - job_name: 'storebridge-web'
    kubernetes_sd_configs:
    - role: pod
      namespaces:
        names:
        - storebridge-prod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
    - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\d+)?;(\d+)
      replacement: $1:$2
      target_label: __address__

  # PostgreSQL 메트릭
  - job_name: 'postgres'
    static_configs:
    - targets: ['postgres-exporter:9187']

  # Redis 메트릭
  - job_name: 'redis'
    static_configs:
    - targets: ['redis-exporter:9121']
```

### Grafana 대시보드

```json
{
  "dashboard": {
    "title": "StoreBridge Overview",
    "panels": [
      {
        "title": "API Requests per Second",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Registration Success Rate",
        "targets": [
          {
            "expr": "storebridge_registration_success_rate"
          }
        ]
      },
      {
        "title": "Queue Depth",
        "targets": [
          {
            "expr": "storebridge_queue_depth"
          }
        ]
      },
      {
        "title": "Rate Limit Remaining",
        "targets": [
          {
            "expr": "storebridge_rate_limit_remaining"
          }
        ]
      }
    ]
  }
}
```

---

## 배포 체크리스트

### 배포 전

- [ ] 코드 리뷰 완료
- [ ] 모든 테스트 통과 (Unit, Integration, E2E)
- [ ] Lint 및 타입 체크 통과
- [ ] 보안 스캔 통과 (Bandit, Trivy)
- [ ] 데이터베이스 마이그레이션 검증
- [ ] 환경 변수 확인 (Secrets, ConfigMap)
- [ ] 롤백 계획 수립

### 배포 중

- [ ] Docker 이미지 빌드 성공
- [ ] Container Registry 푸시 성공
- [ ] Kubernetes Deployment 업데이트
- [ ] Rolling Update 진행 모니터링
- [ ] Health Check 통과
- [ ] Smoke Test 통과

### 배포 후

- [ ] 로그 확인 (에러 없음)
- [ ] 메트릭 확인 (CPU, Memory, API 응답 시간)
- [ ] 알림 테스트 (Slack, Email)
- [ ] 실제 기능 테스트 (1개 상품 등록)
- [ ] 10분간 모니터링
- [ ] 구버전 Pod 종료 (Blue-Green의 경우)

### 롤백 절차

```bash
# 1. 이전 버전으로 롤백
kubectl rollout undo deployment/storebridge-web \
  -n storebridge-prod

# 2. 롤백 상태 확인
kubectl rollout status deployment/storebridge-web \
  -n storebridge-prod

# 3. 특정 리비전으로 롤백
kubectl rollout undo deployment/storebridge-web \
  --to-revision=3 \
  -n storebridge-prod

# 4. 롤백 히스토리 확인
kubectl rollout history deployment/storebridge-web \
  -n storebridge-prod
```

---

**작성자**: StoreBridge Team
**최종 수정**: 2025-10-16
**버전**: 1.0
