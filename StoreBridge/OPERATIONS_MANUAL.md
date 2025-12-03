# 운영 매뉴얼 (Operations Manual)

> StoreBridge 일일 운영 가이드 및 장애 대응 절차

**작성일**: 2025-10-16
**대상**: 운영 담당자, DevOps 엔지니어
**버전**: 1.0

---

## 목차

1. [일일 운영 체크리스트](#일일-운영-체크리스트)
2. [주간/월간 작업](#주간월간-작업)
3. [모니터링 대시보드](#모니터링-대시보드)
4. [알림 설정](#알림-설정)
5. [장애 대응 Runbook](#장애-대응-runbook)
6. [성능 튜닝 가이드](#성능-튜닝-가이드)
7. [백업 & 복구](#백업--복구)
8. [FAQ](#faq)

---

## 일일 운영 체크리스트

### 매일 오전 (09:00)

#### 1. 시스템 헬스 체크

```bash
# Kubernetes Pod 상태 확인
kubectl get pods -n storebridge-prod

# 모든 Pod가 Running 상태여야 함
# CrashLoopBackOff, Error 상태는 즉시 조사 필요
```

**정상 예시:**
```
NAME                                READY   STATUS    RESTARTS   AGE
storebridge-web-7d9f8b5c4d-abc12    1/1     Running   0          2d
storebridge-web-7d9f8b5c4d-def34    1/1     Running   0          2d
storebridge-worker-normal-xxx       1/1     Running   0          1d
```

**비정상 예시:**
```
NAME                                READY   STATUS             RESTARTS   AGE
storebridge-web-7d9f8b5c4d-abc12    0/1     CrashLoopBackOff   5          10m
```
→ **[Runbook](#pod-crashloopbackoff) 참고**

---

#### 2. Grafana 대시보드 확인

**확인 항목:**
- [ ] **API 응답 시간** (p95 < 2초)
- [ ] **에러율** (< 1%)
- [ ] **등록 성공률** (> 85%)
- [ ] **큐 깊이** (< 1000)
- [ ] **Rate Limit 잔여** (> 20%)
- [ ] **CPU/Memory 사용률** (< 80%)

**대시보드 URL:** `https://grafana.storebridge.com/d/overview`

---

#### 3. 일일 작업 실행 통계 확인

```bash
# 어제 생성된 작업 통계
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.storebridge.com/v1/jobs?created_after=$(date -d yesterday +%Y-%m-%d)&status=COMPLETED" \
  | jq '.pagination.total'

# 어제 등록 성공/실패 카운트
psql -h postgres -U user -d storebridge <<EOF
SELECT
  DATE(created_at) AS date,
  COUNT(*) FILTER (WHERE state = 'COMPLETED') AS success,
  COUNT(*) FILTER (WHERE state = 'FAILED') AS failed,
  ROUND(COUNT(*) FILTER (WHERE state = 'COMPLETED')::NUMERIC / COUNT(*) * 100, 2) AS success_rate
FROM product_registrations
WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
  AND created_at < CURRENT_DATE
GROUP BY DATE(created_at);
EOF
```

**정상 기준:**
- 성공률 > 85%
- 실패 건수 < 100개

---

#### 4. 수동 검토 큐 확인

```bash
# 수동 검토 대기 건수
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.storebridge.com/v1/manual-review?page_size=1" \
  | jq '.pagination.total'
```

**대기 건수 > 50개**: 우선 순위 높은 건부터 처리 시작

---

#### 5. 에러 로그 확인

```bash
# 최근 1시간 에러 로그 (Loki)
curl -G -s "http://loki:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={job="storebridge-web"} |= "ERROR"' \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)" \
  --data-urlencode "end=$(date +%s)" \
  | jq '.data.result[] | .values[]'
```

**주의 대상:**
- `Database connection failed`
- `Redis connection timeout`
- `Rate limit exceeded` (반복 발생)
- `Naver API 5xx`

---

### 매일 오후 (17:00)

#### 1. API 쿼터 사용량 확인

```bash
# 도매꾹 API 사용량 (일일 15,000 제한)
redis-cli GET "domeggook:daily_calls:$(date +%Y-%m-%d)"

# 네이버 API 사용량 추정 (초당 2회)
redis-cli KEYS "naver:ratelimit:*" | wc -l
```

**도매꾹 사용량 > 14,000**: 오늘 추가 작업 자제

---

#### 2. 디스크 용량 확인

```bash
# PostgreSQL 데이터 크기
psql -h postgres -U user -d storebridge -c "
  SELECT
    pg_size_pretty(pg_database_size('storebridge')) AS db_size;
"

# MinIO 사용량
mc du myminio/storebridge-images
```

**DB 크기 > 80GB**: 오래된 로그/Job 데이터 정리 고려
**S3 사용량 > 500GB**: 이미지 정리 또는 라이프사이클 정책 설정

---

### 매일 저녁 (22:00)

#### 1. 배치 작업 스케줄 확인

```bash
# Celery Beat 스케줄 확인
kubectl logs -n storebridge-prod deployment/storebridge-beat --tail=50

# 예정된 배치 작업
# - 00:00 ~ 06:00: 대량 등록
# - 06:00 ~ 09:00: 재고 동기화
```

---

## 주간/월간 작업

### 주간 작업 (매주 월요일)

#### 1. 반려 사유 분석

```bash
# 지난 주 반려 사유 TOP 10
psql -h postgres -U user -d storebridge <<EOF
SELECT
  error_code,
  COUNT(*) AS count,
  ROUND(COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER () * 100, 2) AS percentage
FROM product_registrations
WHERE state = 'MANUAL_REVIEW'
  AND created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY error_code
ORDER BY count DESC
LIMIT 10;
EOF
```

**조치:**
- `CATEGORY_MISMATCH` 많으면 → 카테고리 매핑 추가
- `FORBIDDEN_WORD` 많으면 → 금지어 자동 치환 룰 보강
- `ATTRIBUTE_MISSING` 많으면 → 기본값 설정 추가

---

#### 2. 성능 트렌드 분석

- Grafana에서 주간 리포트 확인
- API 응답 시간 추이
- 등록 성공률 추이
- 에러율 추이

**악화 추세 발견 시**: 원인 조사 및 최적화

---

### 월간 작업 (매월 1일)

#### 1. 데이터베이스 VACUUM

```sql
-- PostgreSQL 데이터 정리 (Dead tuple 제거)
VACUUM ANALYZE products;
VACUUM ANALYZE product_registrations;
VACUUM ANALYZE jobs;
VACUUM ANALYZE job_items;
```

#### 2. 인덱스 재구축

```sql
-- 사용률 낮은 인덱스 확인
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND idx_scan = 0
ORDER BY indexname;

-- 사용 안 하는 인덱스 삭제 고려

-- Fragmentation 심한 인덱스 재구축
REINDEX INDEX CONCURRENTLY idx_products_created_at;
```

#### 3. 오래된 데이터 아카이빙

```sql
-- 3개월 이상 오래된 완료 작업 아카이빙
WITH archived_jobs AS (
  DELETE FROM jobs
  WHERE status = 'COMPLETED'
    AND completed_at < CURRENT_DATE - INTERVAL '90 days'
  RETURNING *
)
INSERT INTO jobs_archive SELECT * FROM archived_jobs;

-- 6개월 이상 오래된 audit_logs 삭제
DELETE FROM audit_logs
WHERE created_at < CURRENT_DATE - INTERVAL '180 days';
```

#### 4. 백업 검증

```bash
# 최신 백업 복구 테스트 (스테이징 환경)
aws s3 cp s3://storebridge-backups/latest.sql.gz /tmp/
gunzip /tmp/latest.sql.gz
psql -h staging-postgres -U user -d storebridge_test < /tmp/latest.sql

# 데이터 무결성 확인
psql -h staging-postgres -U user -d storebridge_test -c "
  SELECT COUNT(*) FROM products;
  SELECT COUNT(*) FROM product_registrations;
"
```

---

## 모니터링 대시보드

### Grafana 대시보드 구성

#### Overview Dashboard

**패널 구성:**
1. **API 요청 수** (line chart)
   - 메트릭: `rate(http_requests_total[5m])`
   - 알림: > 500 req/s

2. **API 응답 시간** (histogram)
   - 메트릭: `http_request_duration_seconds`
   - p50, p95, p99
   - 알림: p95 > 3초

3. **에러율** (gauge)
   - 메트릭: `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])`
   - 알림: > 1%

4. **등록 성공률** (gauge)
   - 메트릭: `storebridge_registration_success_rate`
   - 알림: < 80%

5. **큐 깊이** (line chart)
   - 메트릭: `storebridge_queue_depth`
   - 알림: > 2000

6. **Rate Limit 잔여** (bar chart)
   - 메트릭: `storebridge_rate_limit_remaining{api_name="naver"}`
   - 알림: < 10

#### Infrastructure Dashboard

**패널 구성:**
1. **CPU 사용률** (per pod)
2. **Memory 사용률** (per pod)
3. **Network I/O**
4. **PostgreSQL 연결 수**
5. **Redis 메모리 사용량**

---

## 알림 설정

### 알림 채널

| 채널 | 용도 | 대상 |
|------|------|------|
| **Slack #storebridge-alerts** | 모든 알림 | 전체 팀 |
| **PagerDuty** | 긴급 알림 (P0) | On-call 담당자 |
| **Email** | 주간 리포트 | 매니저 |

### 알림 우선순위

#### P0 (긴급) - 즉시 대응 필요

- [ ] **서비스 다운** (Health Check 실패)
- [ ] **데이터베이스 연결 실패**
- [ ] **API 에러율 > 5%**
- [ ] **디스크 용량 > 90%**

**알림 방법:** Slack + PagerDuty + SMS

---

#### P1 (높음) - 30분 내 대응

- [ ] **등록 성공률 < 70%**
- [ ] **API 응답 시간 p95 > 5초**
- [ ] **큐 깊이 > 5000**
- [ ] **Pod Restart 빈번** (5회/10분)

**알림 방법:** Slack + PagerDuty

---

#### P2 (중간) - 업무 시간 내 대응

- [ ] **등록 성공률 < 85%**
- [ ] **API 응답 시간 p95 > 3초**
- [ ] **Rate Limit 90% 도달**
- [ ] **메모리 사용률 > 85%**

**알림 방법:** Slack

---

## 장애 대응 Runbook

### 1. Pod CrashLoopBackOff

**증상:**
```bash
kubectl get pods -n storebridge-prod
# storebridge-web-xxx  0/1  CrashLoopBackOff  5  10m
```

**원인 분석:**
```bash
# 로그 확인
kubectl logs -n storebridge-prod storebridge-web-xxx --previous

# 일반적인 원인:
# - Database 연결 실패
# - 환경 변수 누락/오타
# - 이미지 버전 문제
# - OOM (Out of Memory)
```

**대응 절차:**

1. **로그 분석**
   ```bash
   kubectl logs -n storebridge-prod storebridge-web-xxx --previous | grep -i error
   ```

2. **환경 변수 확인**
   ```bash
   kubectl get secret storebridge-secrets -n storebridge-prod -o yaml
   kubectl get configmap storebridge-config -n storebridge-prod -o yaml
   ```

3. **Database 연결 테스트**
   ```bash
   kubectl exec -it -n storebridge-prod storebridge-web-xxx -- \
     python -c "import asyncpg; asyncpg.connect('$DATABASE_URL')"
   ```

4. **이미지 버전 롤백**
   ```bash
   kubectl rollout undo deployment/storebridge-web -n storebridge-prod
   ```

5. **스케일 다운 후 재시작**
   ```bash
   kubectl scale deployment/storebridge-web --replicas=0 -n storebridge-prod
   sleep 10
   kubectl scale deployment/storebridge-web --replicas=3 -n storebridge-prod
   ```

---

### 2. 네이버 API Rate Limit 429 연속 발생

**증상:**
- 로그에 `429 Too Many Requests` 다수
- 등록 실패율 급증

**원인:**
- Rate Limiter 버그
- 동시 작업 과다
- 네이버 측 제한 강화

**대응 절차:**

1. **즉시 조치: Worker 일시 중지**
   ```bash
   kubectl scale deployment/storebridge-worker-normal --replicas=0 -n storebridge-prod
   kubectl scale deployment/storebridge-worker-batch --replicas=0 -n storebridge-prod
   ```

2. **Rate Limiter 상태 확인**
   ```bash
   redis-cli KEYS "naver:ratelimit:*"
   redis-cli GET "naver:ratelimit:$(date +%s)"
   ```

3. **수동으로 1개 등록 테스트**
   ```bash
   curl -X POST https://api.storebridge.com/v1/products/product-uuid-123/retry \
     -H "Authorization: Bearer $TOKEN"
   ```

4. **Worker 재시작 (단계적)**
   ```bash
   # 1개만 먼저 시작
   kubectl scale deployment/storebridge-worker-normal --replicas=1 -n storebridge-prod

   # 10분 모니터링 후 정상이면 증가
   kubectl scale deployment/storebridge-worker-normal --replicas=4 -n storebridge-prod
   ```

5. **근본 원인 분석**
   - Rate Limiter 로직 검토
   - 동시성 테스트
   - 네이버 GitHub Discussions 확인

---

### 3. 등록 성공률 급락 (< 70%)

**증상:**
- Grafana 알림: Registration success rate < 70%

**원인:**
- 네이버 API 정책 변경
- 카테고리 매핑 오류
- 금지어 추가

**대응 절차:**

1. **최근 반려 사유 분석**
   ```sql
   SELECT
     error_code,
     error_message,
     COUNT(*) AS count
   FROM product_registrations
   WHERE state = 'MANUAL_REVIEW'
     AND created_at >= NOW() - INTERVAL '1 hour'
   GROUP BY error_code, error_message
   ORDER BY count DESC
   LIMIT 10;
   ```

2. **특정 에러 코드 집중 발생 시**
   - `CATEGORY_MISMATCH`: 카테고리 매핑 확인
   - `FORBIDDEN_WORD`: 금지어 목록 확인
   - `ATTRIBUTE_MISSING`: 필수 속성 변경 여부 확인 (네이버 공지 확인)

3. **네이버 API 공지 확인**
   - GitHub: https://github.com/commerce-api-naver/commerce-api/discussions
   - 릴리즈 노트 확인

4. **임시 조치: 해당 카테고리 작업 중단**
   ```bash
   # 문제 카테고리만 필터링하여 재시도 중지
   ```

5. **영구 조치: 매핑/룰 업데이트**
   - 카테고리 매핑 추가/수정
   - 금지어 목록 업데이트
   - 속성 기본값 설정

---

### 4. PostgreSQL 연결 풀 고갈

**증상:**
- 로그: `FATAL: remaining connection slots are reserved`
- API 응답 느림

**원인:**
- Connection Pool 설정 부족
- Connection Leak (닫지 않은 연결)

**대응 절차:**

1. **현재 연결 수 확인**
   ```sql
   SELECT COUNT(*) FROM pg_stat_activity;
   SELECT max_connections FROM pg_settings WHERE name = 'max_connections';
   ```

2. **유휴 연결 종료**
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

3. **Connection Pool 설정 증가** (임시)
   ```python
   # app/models/database.py
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=20,        # 기본 10 → 20
       max_overflow=40      # 기본 20 → 40
   )
   ```

4. **근본 원인: Connection Leak 찾기**
   ```python
   # 모든 DB 세션이 제대로 닫히는지 확인
   # with 문 또는 try-finally 사용 검증
   ```

---

### 5. 디스크 용량 부족 (> 90%)

**증상:**
- 알림: Disk usage > 90%
- Pod 쓰기 실패

**대응 절차:**

1. **용량 분석**
   ```bash
   # Pod 내부
   kubectl exec -it -n storebridge-prod postgres-xxx -- df -h

   # 큰 파일/디렉토리 찾기
   kubectl exec -it -n storebridge-prod postgres-xxx -- \
     du -sh /var/lib/postgresql/data/* | sort -hr | head -20
   ```

2. **PostgreSQL 로그 정리**
   ```bash
   kubectl exec -it -n storebridge-prod postgres-xxx -- \
     bash -c "find /var/lib/postgresql/data/log -name '*.log' -mtime +7 -delete"
   ```

3. **오래된 데이터 아카이빙** (DB)
   ```sql
   -- 위 "월간 작업" 참고
   ```

4. **볼륨 확장** (영구 조치)
   ```bash
   # AWS EBS 볼륨 확장
   aws ec2 modify-volume --volume-id vol-xxx --size 200

   # Kubernetes PVC 업데이트
   kubectl patch pvc postgres-pvc -n storebridge-prod \
     -p '{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}'
   ```

---

## 성능 튜닝 가이드

### API 응답 시간 최적화

#### 1. Database 쿼리 최적화

```sql
-- 느린 쿼리 찾기
SELECT
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- N+1 쿼리 확인
-- SQLAlchemy에서 joinedload() 사용 확인
```

#### 2. Redis 캐시 히트율 확인

```bash
redis-cli INFO stats | grep keyspace_hits
redis-cli INFO stats | grep keyspace_misses

# 히트율 = hits / (hits + misses)
# 목표: > 80%
```

**히트율 < 80%**: TTL 증가 또는 캐시 대상 확대

---

#### 3. Connection Pool 튜닝

```python
# 적정 pool_size 계산
# pool_size = (코어 수 × 2) + 예비
# 예: 4 코어 → (4 × 2) + 2 = 10

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 연결 체크
    pool_recycle=3600    # 1시간마다 재생성
)
```

---

### Worker 동시성 조정

```python
# Celery Worker 동시성
# CPU-bound 작업: worker 수 = 코어 수
# I/O-bound 작업: worker 수 = 코어 수 × 2~4

# 현재 설정
# normal queue: -c 4 (I/O 많음)
# batch queue: -c 2 (CPU 많음)
```

**조정 기준:**
- CPU 사용률 < 50% & 큐 쌓임 → 동시성 증가
- CPU 사용률 > 90% → 동시성 감소 또는 Pod 증가

---

## 백업 & 복구

### 백업 전략

#### 1. Database 백업 (자동, 매일 02:00)

```bash
# CronJob 설정
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: storebridge-prod
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h postgres -U user -d storebridge | gzip > /backup/storebridge-$(date +%Y%m%d).sql.gz
              aws s3 cp /backup/storebridge-$(date +%Y%m%d).sql.gz s3://storebridge-backups/
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: storebridge-secrets
                  key: database-password
          restartPolicy: OnFailure
EOF
```

#### 2. 설정 백업 (수동)

```bash
# Kubernetes 리소스 백업
kubectl get all,secret,configmap -n storebridge-prod -o yaml \
  > k8s-backup-$(date +%Y%m%d).yaml

# Git에 커밋
git add k8s-backup-*.yaml
git commit -m "Backup K8s resources $(date +%Y-%m-%d)"
git push
```

---

### 복구 절차

#### 전체 시스템 복구

```bash
# 1. Database 복구
aws s3 cp s3://storebridge-backups/storebridge-20251015.sql.gz /tmp/
gunzip /tmp/storebridge-20251015.sql.gz
psql -h postgres -U user -d storebridge < /tmp/storebridge-20251015.sql

# 2. Kubernetes 리소스 복구
kubectl apply -f k8s-backup-20251015.yaml

# 3. Pod 재시작
kubectl rollout restart deployment/storebridge-web -n storebridge-prod
kubectl rollout restart deployment/storebridge-worker-normal -n storebridge-prod

# 4. Health Check
curl https://api.storebridge.com/health
```

---

## FAQ

### Q1. 상품 등록이 멈춘 것 같아요

**A:**
```bash
# 큐 깊이 확인
redis-cli LLEN celery:normal

# Worker 로그 확인
kubectl logs -n storebridge-prod deployment/storebridge-worker-normal --tail=100

# Worker 재시작
kubectl rollout restart deployment/storebridge-worker-normal -n storebridge-prod
```

---

### Q2. 특정 상품만 계속 실패합니다

**A:**
```bash
# 상품 상세 조회
curl -H "Authorization: Bearer $TOKEN" \
  https://api.storebridge.com/v1/products/product-uuid-123

# 사전 검증
curl -X POST -H "Authorization: Bearer $TOKEN" \
  https://api.storebridge.com/v1/products/validate \
  -d '{"domeggook_item_id": "DG123456"}'

# 반려 사유 확인 후 수동 검토 큐에서 수정
```

---

### Q3. Grafana 대시보드가 안 보여요

**A:**
```bash
# Prometheus/Grafana Pod 상태 확인
kubectl get pods -n storebridge-prod | grep -E "prometheus|grafana"

# Prometheus 타겟 확인
curl http://prometheus:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'

# Grafana 재시작
kubectl rollout restart deployment/grafana -n storebridge-prod
```

---

**작성자**: StoreBridge Team
**최종 수정**: 2025-10-16
**버전**: 1.0

**긴급 연락처:**
- On-call: PagerDuty
- Slack: #storebridge-alerts
- Email: ops@storebridge.com
