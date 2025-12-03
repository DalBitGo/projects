# 오픈소스 프로젝트 코드 분석 방법론

## 목적
다른 세션이나 프로젝트에서도 일관되게 사용할 수 있는 체계적인 코드 분석 프로세스 정립

---

## Phase 1: 프로젝트 구조 파악

### 1.1 파일 시스템 트리 생성
```bash
tree -L 3 -I 'node_modules|__pycache__|.git'
```
- 전체 폴더 구조 시각화
- 불필요한 폴더 제외 (node_modules, 캐시 등)

### 1.2 주요 파일 식별
다음 우선순위로 파일 식별:

**필수 확인 파일**:
1. `README.md` - 프로젝트 개요
2. `requirements.txt` / `package.json` - 의존성
3. `.gitignore` - 무시되는 파일 (민감 정보 힌트)
4. `Dockerfile` / `docker-compose.yaml` - 배포 환경
5. 설정 파일 - `.env.example`, `config.py`, `settings.py`

**코어 로직 파일**:
- 엔트리포인트: `main.py`, `app.py`, `index.js`
- 핵심 모듈: `src/`, `lib/`, `core/`
- API 호출: `api.py`, `client.py`, `services/`
- 데이터 모델: `models.py`, `schema.py`, `database.py`

### 1.3 파일 크기 및 복잡도 확인
```bash
wc -l **/*.py | sort -n
```
- 파일별 라인 수 확인
- 큰 파일 = 중요하거나 복잡한 로직

---

## Phase 2: 의존성 분석

### 2.1 외부 라이브러리 파악
`requirements.txt` 또는 `package.json` 분석:

**각 라이브러리에 대해 기록**:
- 이름
- 용도 (웹 프레임워크, DB, API 클라이언트 등)
- 왜 이 라이브러리를 선택했을까? (대안은?)

**예시 템플릿**:
```markdown
| 라이브러리 | 버전 | 용도 | 선택 이유 추측 | 대안 |
|-----------|------|------|--------------|------|
| Flask | 2.0 | 웹 프레임워크 | 간단, 빠른 프로토타이핑 | Django, FastAPI |
```

### 2.2 라이브러리 간 관계 파악
- 어떤 라이브러리가 함께 사용되는가?
- 아키텍처 패턴 힌트 (예: Flask + SQLAlchemy = MVC)

---

## Phase 3: 엔트리포인트 분석

### 3.1 실행 흐름 파악
메인 파일 (`app.py`, `main.py`)에서:

**체크리스트**:
- [ ] 환경 변수 로드 방식
- [ ] 설정 파일 읽기
- [ ] 데이터베이스 연결
- [ ] 라우트/엔드포인트 정의
- [ ] 초기화 순서

**기록 형식**:
```markdown
## app.py 실행 흐름
1. 환경 변수 로드 (.env)
2. Flask 앱 초기화
3. 데이터베이스 연결 (SQLAlchemy)
4. 라우트 등록 (/compare, /analyze)
5. 서버 시작 (port 5000)
```

### 3.2 설정 관리 방식
- 하드코딩 vs 환경 변수 vs 설정 파일
- 민감 정보 처리 (API 키 등)

---

## Phase 4: 핵심 로직 분석

### 4.1 기능별 코드 매핑

**템플릿**:
```markdown
## 기능: 채널 데이터 수집

### 관련 파일
- `src/youtube_api.py` - API 호출
- `src/data_processor.py` - 데이터 변환
- `models/channel.py` - 데이터 모델

### 처리 흐름
1. 사용자가 채널 ID 입력
2. `get_channel_info(channel_id)` 호출
3. YouTube API 쿼리 (channels.list)
4. JSON 응답 파싱
5. Pandas DataFrame 변환
6. 데이터베이스 저장
```

### 4.2 API 호출 패턴 분석

**각 API 호출마다 기록**:
```markdown
### YouTube API: channels.list

**위치**: `src/youtube_api.py:45`

**파라미터**:
- `part`: snippet, statistics
- `id`: 채널 ID

**응답 필드 사용**:
- `items[0].statistics.subscriberCount`
- `items[0].statistics.viewCount`

**에러 처리**:
- API 할당량 초과: HTTPError 403 처리
- 네트워크 오류: retry 3회
```

### 4.3 데이터 흐름 추적

**Data Flow Diagram 작성**:
```
사용자 입력
  ↓
채널 ID 검증
  ↓
YouTube API 호출
  ↓
JSON 응답
  ↓
Pandas DataFrame
  ↓
데이터 정제/변환
  ↓
시각화 or 저장
```

---

## Phase 5: 데이터 구조 분석

### 5.1 데이터베이스 스키마
SQL 파일 또는 ORM 모델 분석:

**템플릿**:
```markdown
### Table: channels

| 컬럼명 | 타입 | Null | 설명 |
|--------|------|------|------|
| id | INT | NO | Primary Key |
| channel_id | VARCHAR(50) | NO | YouTube 채널 ID |
| title | VARCHAR(255) | YES | 채널 이름 |
| subscriber_count | INT | YES | 구독자 수 |
| created_at | TIMESTAMP | NO | 레코드 생성 시간 |

**인덱스**:
- PRIMARY KEY (id)
- UNIQUE (channel_id)

**관계**:
- videos 테이블과 1:N 관계
```

### 5.2 데이터 모델 클래스
Python 클래스나 TypeScript 인터페이스 분석:

```markdown
### Channel 클래스

**파일**: `models/channel.py`

**필드**:
- `id`: str - YouTube 채널 ID
- `title`: str - 채널 이름
- `statistics`: dict - 통계 정보

**메서드**:
- `fetch_videos()`: 채널의 영상 목록 가져오기
- `calculate_avg_views()`: 평균 조회수 계산
```

---

## Phase 6: 알고리즘 및 비즈니스 로직

### 6.1 복잡한 함수 분석

**템플릿**:
```markdown
### 함수: calculate_engagement_rate()

**위치**: `src/analytics.py:120`

**목적**: 참여율 계산

**입력**:
- `video_stats`: dict - 영상 통계

**출력**:
- `float` - 참여율 (%)

**알고리즘**:
1. 좋아요, 댓글, 공유 수 합산
2. 조회수로 나누기
3. 100 곱해서 퍼센트 변환

**엣지 케이스**:
- 조회수 0인 경우 → 0.0 반환
- None 값 처리 → 0으로 간주

**개선 가능 영역**:
- 가중치 적용 (좋아요 vs 댓글 중요도)
```

### 6.2 최적화 및 성능 고려사항
- 루프 내 API 호출 (N+1 문제)
- 캐싱 전략
- 병렬 처리 (멀티스레딩/비동기)

---

## Phase 7: 에러 처리 및 예외 상황

### 7.1 에러 처리 패턴
```markdown
### API 할당량 초과 처리

**위치**: `src/youtube_api.py:78`

**방식**:
- try-except로 HTTPError 잡기
- 403 에러 코드 확인
- 사용자에게 알림 메시지 표시
- 로그 파일에 기록

**개선점**:
- 사전 할당량 체크 없음
- 자동 재시도 메커니즘 부재
```

### 7.2 입력 검증
- 사용자 입력 sanitization
- 채널 ID 형식 검증
- SQL Injection 방지

---

## Phase 8: UI/UX 분석 (웹 앱의 경우)

### 8.1 라우트 구조
```markdown
| 경로 | 메서드 | 기능 | 템플릿 |
|------|--------|------|--------|
| `/` | GET | 홈페이지 | `index.html` |
| `/compare` | POST | 채널 비교 | `compare.html` |
| `/analyze/<video_id>` | GET | 영상 분석 | `analyze.html` |
```

### 8.2 템플릿 분석
- 템플릿 엔진 (Jinja2, EJS 등)
- 데이터 전달 방식
- 정적 파일 처리 (CSS, JS)

---

## Phase 9: 배포 및 인프라

### 9.1 Docker 분석
`Dockerfile`:
```markdown
**베이스 이미지**: python:3.9
**설치 과정**:
1. requirements.txt 복사
2. pip install
3. 소스 코드 복사
**포트**: 5000
**엔트리포인트**: `python app.py`
```

`docker-compose.yaml`:
```markdown
**서비스**:
- web: Flask 앱
- db: MySQL 컨테이너
**볼륨**: 데이터 영속성
**네트워크**: 서비스 간 통신
```

### 9.2 환경 변수 관리
`.env.example`:
```markdown
| 변수명 | 설명 | 예시 |
|--------|------|------|
| YOUTUBE_API_KEY | YouTube API 키 | AIza... |
| DB_HOST | 데이터베이스 호스트 | localhost |
```

---

## Phase 10: 문서화 및 종합

### 10.1 최종 분석 문서 구조

```markdown
# [프로젝트명] 코드 분석 리포트

## 1. 프로젝트 개요
- 목적
- 기술 스택
- 아키텍처 다이어그램

## 2. 폴더 및 파일 구조
- 트리 구조
- 주요 파일 설명

## 3. 의존성 분석
- 라이브러리 목록 및 용도

## 4. 실행 흐름
- 엔트리포인트 분석
- 초기화 과정

## 5. 핵심 기능 분석
- 기능별 코드 매핑
- 처리 흐름도

## 6. API 사용 패턴
- YouTube API 호출 상세
- 쿼리 최적화

## 7. 데이터 구조
- 데이터베이스 스키마
- 데이터 모델

## 8. 주요 알고리즘
- 복잡한 함수 설명
- 최적화 포인트

## 9. 에러 처리
- 예외 처리 패턴
- 알려진 이슈

## 10. 배포 및 실행
- Docker 설정
- 환경 변수

## 11. 개선 가능 영역
- 성능 최적화
- 코드 품질
- 기능 확장

## 12. 학습 포인트
- 좋은 패턴
- 피해야 할 안티패턴
```

### 10.2 코드 스니펫 포함 규칙
- 중요한 로직만 발췌
- 주석으로 설명 추가
- 라인 번호 참조로 원본 위치 명시

---

## 분석 시 주의사항

### 체크리스트
- [ ] 코드를 실제로 실행해보지 않고 추측만 하지 않기
- [ ] 주석과 docstring 꼼꼼히 읽기
- [ ] Git 커밋 히스토리 확인 (중요 변경사항)
- [ ] 이슈/PR에서 개발자 의도 파악
- [ ] 라이선스 확인 (재사용 가능 여부)

### 도구 활용
- `grep -r "pattern" .` - 코드 검색
- `git log --oneline` - 커밋 이력
- `git blame filename` - 라인별 수정자
- IDE의 "Find Usages" - 함수/클래스 사용처 추적

---

## 템플릿 사용 예시

새 프로젝트 분석 시:
1. 이 문서를 복사
2. Phase별로 순차 진행
3. 각 Phase의 템플릿 채우기
4. 최종 분석 문서 작성

이 방법론을 따르면 일관성 있고 누락 없는 코드 분석 가능.
