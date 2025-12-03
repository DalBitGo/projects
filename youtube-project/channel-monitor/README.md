# YouTube Intelligence Dashboard

YouTube 채널 성장 최적화를 위한 데이터 분석 대시보드

> **📖 빠른 시작**: 이 문서 | **📊 프로젝트 요약**: `SUMMARY.md` | **🚀 향후 계획**: `ROADMAP.md` | **📝 개발 과정**: `DEVELOPMENT_LOG.md`

## 📋 주요 기능

### ✅ 구현 완료 (v1.1 - 2025-10-22)

#### 데이터 수집
- YouTube Data API v3: 채널/영상 정보
- YouTube Analytics API: 상세 성과 지표
- 트래픽 소스 분석 (알고리즘 선택 파악)
- 자동 데이터 저장 (SQLite)
- OAuth 2.0 인증 (여러 계정 지원)

#### 메인 대시보드 (app/dashboard.py)
- **핵심 지표 카드**: 구독자, 총 영상, 총 조회수, 알고리즘 선택률
- **🎯 액션 필요**: 긴급/주의/성공 자동 분류
  - 긴급: 조회수 급락 영상 자동 감지
  - 주의: 좋아요율 저조 영상 경고
  - 성공: 성과 우수 영상 하이라이트
- **트래픽 소스 분석**: 파이 차트 + 상세 테이블 + 자동 인사이트
- **🏆 성공 패턴 분석**:
  - 성공 영상(상위 20%) vs 일반 영상 비교
  - 최적 업로드 타이밍 분석 (요일별, 시간대별)
  - 자동 추천 시간 생성
- **영상 목록**: 최근 영상 / 전체 영상 탭 분리
- **일별 성과 추이**: 조회수 그래프 + 통계 요약

#### 영상별 상세 분석 페이지 (app/pages/video_analysis.py)
- 특정 영상 선택 → 상세 트래픽 소스 분석
- 채널 평균 대비 성과 비교
- YouTube 바로가기 링크

### 🚧 향후 구현 예정

- 알림 시스템 (Slack/Email/Discord)
- 주간/월간 자동 리포트
- 경쟁 채널 비교 분석
- 머신러닝 기반 예측 (다음 영상 조회수 예측)
- 댓글 감성 분석
- 썸네일 A/B 테스트 분석
- 실시간 데이터 수집 (Webhook)

---

## 🚀 빠른 시작

### 1. 환경 준비

```bash
# 가상환경 생성 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 데이터베이스 초기화

```bash
python database/schema.py
```

출력: `✅ 데이터베이스 초기화 완료: data/youtube.db`

### 3. 데이터 수집

```bash
python collectors/collect_all.py
```

**참고:**
- OAuth 인증이 먼저 필요합니다 (`tokens/account1_token.json` 등)
- `collectors/collect_all.py` 파일의 `accounts_to_collect` 리스트에 계정 이름 추가

**예상 소요 시간:**
- 계정당 약 2-3분
- 영상 수에 따라 달라질 수 있음

### 4. 대시보드 실행

```bash
streamlit run app/dashboard.py
```

브라우저가 자동으로 열리고 `http://localhost:8501`에서 대시보드를 볼 수 있습니다.

---

## 📁 프로젝트 구조

```
channel-monitor/
├── app/                          # Streamlit 대시보드
│   ├── dashboard.py             # 메인 대시보드
│   └── pages/                   # 추가 페이지 (향후)
│
├── collectors/                   # 데이터 수집
│   ├── youtube_api.py           # YouTube API Wrapper
│   └── collect_all.py           # 전체 수집 스크립트
│
├── database/                     # 데이터베이스
│   ├── schema.py                # 스키마 정의
│   └── operations.py            # CRUD 함수
│
├── utils/                        # 유틸리티
│   └── auth.py                  # OAuth 인증 관리
│
├── data/                         # 데이터 저장소
│   └── youtube.db               # SQLite 데이터베이스
│
├── tokens/                       # OAuth 토큰
│   ├── account1_token.json
│   └── account2_token.json
│
├── poc_scripts/                  # POC 테스트 스크립트
│   ├── poc_setup.py
│   ├── poc_authenticate.py
│   └── poc_test_api.py
│
├── config.py                     # 설정 (향후)
├── requirements.txt              # Python 패키지
└── README.md                     # 이 파일
```

---

## 🔧 상세 사용 가이드

### OAuth 인증 (처음 1회만)

계정마다 OAuth 인증이 필요합니다.

```bash
cd poc_scripts
python poc_authenticate.py account1
```

1. 브라우저에 URL이 출력됨
2. URL을 복사해서 브라우저에 붙여넣기
3. YouTube 채널 계정으로 로그인
4. 권한 승인
5. `tokens/account1_token.json` 파일 생성됨

**다른 계정도 동일하게:**
```bash
python poc_authenticate.py account2
python poc_authenticate.py account3
```

**참고:**
- GCP Console에서 OAuth 설정이 먼저 필요합니다
- 자세한 내용: `GCP_SETUP_GUIDE.md` 참고

---

### 데이터 수집 스케줄링

#### Windows (작업 스케줄러)

1. 작업 스케줄러 열기
2. 기본 작업 만들기
3. 이름: "YouTube Intelligence 데이터 수집"
4. 트리거: 매일 오전 9시
5. 동작: 프로그램 시작
   - 프로그램: `python`
   - 인수: `collectors/collect_all.py`
   - 시작 위치: 프로젝트 폴더 경로

#### Linux/Mac (Cron)

```bash
crontab -e
```

다음 줄 추가:
```
0 9 * * * cd /path/to/channel-monitor && python collectors/collect_all.py
```

---

### 데이터 수집 주기 권장

```yaml
일일 수집 (기본):
  시간: 오전 9시
  대상: 모든 채널
  내용: 채널 정보 + 최근 영상 + Analytics

수동 수집 (필요시):
  # 특정 계정만 수집
  python collectors/collect_all.py
```

---

## 📊 데이터베이스 스키마

### 주요 테이블

```sql
accounts                   -- OAuth 계정 정보
channels                   -- 채널 정보
videos                     -- 영상 정보
video_snapshots            -- 영상 통계 스냅샷 (시계열)
video_analytics_daily      -- 영상별 일일 Analytics
channel_analytics_daily    -- 채널별 일일 Analytics
traffic_sources            -- 트래픽 소스 (핵심!)
```

### 데이터베이스 초기화 (주의!)

모든 데이터를 삭제하고 처음부터:

```bash
python database/schema.py --reset
```

---

## 🎯 사용 시나리오

### 시나리오 1: 매일 아침 체크

1. 대시보드 열기: `streamlit run app/dashboard.py`
2. 채널 선택 (사이드바)
3. 핵심 지표 확인
   - 알고리즘 선택률이 얼마나 되는지?
   - 어떤 소스에서 조회수가 오는지?
4. 최근 영상 성과 확인
   - 어제 올린 영상은 잘되고 있나?

### 시나리오 2: 주간 회의

1. 기간을 "최근 7일"로 설정
2. 트래픽 소스 분석
   - 추천 영상 비율이 증가했나?
   - 검색 vs 추천 비율 변화
3. 일별 추이 그래프
   - 전주 대비 성장 확인
4. Top 3 영상 분석
   - 무엇이 잘됐는지 패턴 파악

### 시나리오 3: 영상 업로드 전

1. 과거 데이터에서 패턴 찾기
2. 어떤 영상이 알고리즘에 선택됐는지 확인
3. 다음 영상 전략 수립

---

## 🔍 트러블슈팅

### 데이터가 안 보여요

**확인 사항:**

1. 데이터 수집을 했나요?
   ```bash
   python collectors/collect_all.py
   ```

2. OAuth 인증이 됐나요?
   ```bash
   ls tokens/
   # account1_token.json 등이 보여야 함
   ```

3. 데이터베이스가 있나요?
   ```bash
   ls data/
   # youtube.db 파일이 보여야 함
   ```

### "채널 데이터가 없습니다" 오류

데이터 수집이 필요합니다:

```bash
python collectors/collect_all.py
```

### API 할당량 초과

**증상:** "quota exceeded" 에러

**해결:**
- 내일까지 기다리기 (일일 할당량 10,000 units)
- 또는 GCP Console에서 할당량 증가 요청

**예방:**
- 수집 빈도를 줄이기 (하루 1-2회)
- 영상 개수를 제한 (현재 100개)

### Analytics 데이터가 0으로 나와요

**원인:**
- Analytics API는 48시간 지연됨
- 최근 2일 데이터는 부정확

**해결:**
- 2일 전까지 데이터만 확인
- 코드에서 자동으로 처리됨 (`end_date - timedelta(days=2)`)

---

## 📈 향후 개선 계획

### Phase 2: 핵심 기능 (2주)

- [ ] 액션 필요 섹션
  - 긴급/주의/성공 자동 분류
  - 조회수 급락 감지
  - 알고리즘 선택 영상 하이라이트

- [ ] 영상 상세 분석 페이지
  - 영상별 트래픽 소스
  - 시청 유지율 그래프 (가능한 경우)
  - 성과 지표 비교

- [ ] 알고리즘 최적화 인사이트
  - 알고리즘 선택 영상 vs 일반 영상 비교
  - 성공 패턴 자동 추출

### Phase 3: 고도화 (2주)

- [ ] 최적 업로드 타이밍 분석
- [ ] 주간/월간 리포트 자동 생성
- [ ] 예측 분석 (머신러닝)
- [ ] 알림 시스템 (Slack/Email)
- [ ] 채널 간 비교 대시보드

---

## 📚 관련 문서

### 설정 및 가이드
- `GCP_SETUP_GUIDE.md` - Google Cloud Platform 설정
- `YOUTUBE_API_DATA_GUIDE.md` - API 데이터 가이드

### 설계 및 철학
- `DESIGN_VALIDATION.md` - 설계 검증
- `GROWTH_OPTIMIZED_DASHBOARD.md` - 대시보드 설계 철학
- `DASHBOARD_DESIGN_GUIDE.md` - UI/UX 베스트 프랙티스

### 개발 및 로드맵
- **`DEVELOPMENT_LOG.md`** - 개발 과정 및 기술 문서 (상세 타임라인, 에러 해결 과정)
- **`ROADMAP.md`** - 향후 개발 계획 (Phase 2-5, 우선순위별 기능)

---

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

---

## 📝 변경 이력

### v1.1 - 2025-10-22

- ✅ **액션 필요 섹션**: 긴급/주의/성공 자동 분류
- ✅ **성공 패턴 분석**: 상위 20% vs 일반 영상 비교, 최적 업로드 타이밍
- ✅ **영상별 상세 분석**: 새 페이지 추가 (app/pages/video_analysis.py)
- ✅ **영상 목록 개선**: 탭으로 "최근" / "전체" 분리
- ✅ **자동 인사이트**: 데이터 기반 실행 가능한 조언 생성

### v1.0 (MVP) - 2025-10-22

- ✅ 기본 데이터 수집 (Data API + Analytics API)
- ✅ 트래픽 소스 분석
- ✅ SQLite 데이터베이스
- ✅ Streamlit 대시보드 (홈 화면)
- ✅ 일별 추이 그래프
- ✅ OAuth 2.0 인증 시스템

---

**Made with ❤️ for YouTube Growth**
