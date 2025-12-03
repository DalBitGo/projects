# YouTube Intelligence - POC 가이드

## 📚 생성된 문서 목록

### 1. 핵심 문서

#### **DESIGN_VALIDATION.md** ⭐ 가장 중요
- 전체 설계 검증 문서
- YouTube API 비교 (Data vs Analytics)
- 로컬 실행 환경 설명
- OAuth 인증 구현 방법
- 데이터베이스 스키마 (최종)
- 리스크 분석 및 완화 방안
- 구현 로드맵

#### **GCP_SETUP_GUIDE.md**
- Google Cloud Console 설정 단계별 가이드
- OAuth 클라이언트 생성 방법
- client_secrets.json 다운로드
- 문제 해결 (FAQ)

#### **DASHBOARD_DESIGN_GUIDE.md**
- 대시보드 성공 사례 분석
- UI/UX 베스트 프랙티스
- 기술 스택 비교 (Streamlit 추천)
- 대시보드 A 설계 (우리 채널 성과)
- 레이아웃 패턴

### 2. 이전 문서 (참고)

#### **API_RESEARCH.md**
- YouTube Data API v3 기본 조사
- 할당량 분석
- 배치 처리 방법

#### **ANALYSIS_JensBender_ETL.md**
- 프로덕션급 ETL 파이프라인 분석
- 재사용 가능한 패턴

#### **PROJECT_ARCHITECTURE_DESIGN.md**
- 초기 아키텍처 설계 (일부 수정됨)

---

## 🚀 빠른 시작 (POC 실행)

### Step 1: 환경 준비

```bash
# 프로젝트 디렉토리로 이동
cd /home/junhyun/youtube-project/channel-monitor

# 가상환경 생성 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install google-auth google-auth-oauthlib google-api-python-client
```

### Step 2: GCP 설정 (10분)

**GCP_SETUP_GUIDE.md** 문서를 따라 진행:

1. https://console.cloud.google.com 접속
2. 프로젝트 생성: "YouTube Intelligence"
3. API 활성화:
   - YouTube Data API v3
   - YouTube Analytics API
4. OAuth 동의 화면 구성
5. OAuth 클라이언트 ID 생성 (데스크톱 앱)
6. `client_secrets.json` 다운로드
7. 프로젝트 루트에 저장

### Step 3: POC 실행

```bash
# POC 스크립트 디렉토리로 이동
cd poc_scripts

# 1. 설정 확인
python poc_setup.py

# 2. OAuth 인증 (각 계정마다)
python poc_authenticate.py account1
# → 브라우저 열림 → 로그인 → 권한 승인

# 3. API 테스트
python poc_test_api.py account1

# 4. 다른 계정도 반복
python poc_authenticate.py account2
python poc_test_api.py account2

python poc_authenticate.py account3
python poc_test_api.py account3
```

### Step 4: 결과 확인

**확인할 핵심 사항:**
- [ ] OAuth 인증 성공
- [ ] Data API 채널 정보 조회 성공
- [ ] Analytics API 트래픽 소스 조회 성공
- [ ] 트래픽 소스에 'RELATED_VIDEO' (추천 알고리즘) 데이터 있음

**성공하면:**
→ 설계 확정!
→ Phase 1 (데이터 수집) 구현 시작

**실패하면:**
→ DESIGN_VALIDATION.md 의 "문제 해결" 섹션 참고
→ GCP_SETUP_GUIDE.md 의 FAQ 확인

---

## 📁 프로젝트 구조

```
channel-monitor/
├── README_POC.md                      # 👈 이 파일
├── DESIGN_VALIDATION.md               # 설계 검증 (핵심)
├── GCP_SETUP_GUIDE.md                 # GCP 설정 가이드
├── DASHBOARD_DESIGN_GUIDE.md          # 대시보드 설계
│
├── API_RESEARCH.md                    # API 조사 (참고)
├── ANALYSIS_JensBender_ETL.md         # 분석 (참고)
├── PROJECT_ARCHITECTURE_DESIGN.md     # 아키텍처 (참고)
│
├── poc_scripts/                       # POC 스크립트
│   ├── poc_setup.py                   # 설정 확인
│   ├── poc_authenticate.py            # OAuth 인증
│   └── poc_test_api.py                # API 테스트
│
├── client_secrets.json                # GCP에서 다운로드 (생성 예정)
└── tokens/                            # OAuth 토큰 (생성 예정)
    ├── account1_token.json
    ├── account2_token.json
    └── account3_token.json
```

---

## 🎯 핵심 결정 사항

### ✅ 확정된 설계

1. **채널 소유**: 우리가 소유한 3개 계정의 채널들
2. **API 전략**: Data API + Analytics API 하이브리드
3. **실행 환경**: 로컬 PC (GCP 서버 불필요)
4. **데이터베이스**: SQLite (파일 기반)
5. **대시보드**: Streamlit (Python)
6. **자동화**: Cron/작업 스케줄러

### 🔑 핵심 발견

**YouTube Analytics API 사용 가능!**
- 트래픽 소스 분석 (알고리즘 선택 패턴)
- 시청 유지율, 평균 시청 시간
- 인구통계, 수익 정보
- 이게 진짜 "인사이트"를 줍니다!

**로컬 실행으로 충분!**
- GCP Console은 설정용 (10분)
- 모든 코드는 로컬 PC에서 실행
- 비용 0원

---

## 📖 읽는 순서 (추천)

### 처음 보는 사람
1. **이 파일 (README_POC.md)** - 전체 개요
2. **DESIGN_VALIDATION.md** - 상세 설계 (필독!)
3. **GCP_SETUP_GUIDE.md** - GCP 설정 (실습)
4. POC 실행

### 대시보드에 관심 있는 사람
1. **DASHBOARD_DESIGN_GUIDE.md** - 대시보드 설계
2. **DESIGN_VALIDATION.md** 의 데이터베이스 스키마

### JensBender 코드 참고하고 싶은 사람
1. **ANALYSIS_JensBender_ETL.md** - 패턴 분석
2. **DESIGN_VALIDATION.md** 의 데이터 수집 아키텍처

---

## 🔍 주요 질문 & 답변

### Q: GCP 서버가 필요한가요?
**A:** 아니요!
- GCP Console (웹 페이지)에서 설정만 함
- 코드는 로컬 PC에서 실행
- 비용 0원

### Q: YouTube Analytics API로 뭘 할 수 있나요?
**A:** 엄청 많습니다!
- 트래픽 소스 (YouTube 검색, 추천 알고리즘, 외부)
- 시청 유지율 (어느 시점에서 이탈하는지)
- 평균 시청 시간
- 인구통계 (연령, 성별, 지역)
- 예상 수익

### Q: OAuth 인증이 복잡한가요?
**A:** 처음만 복잡합니다
- 계정당 1회만 인증 (브라우저 로그인)
- 토큰 저장 후 자동 재사용
- 만료 시 자동 갱신

### Q: 할당량이 충분한가요?
**A:** 충분합니다!
- Data API: 일일 10,000 units
- 10개 채널 1시간마다 확인: 720 units/일
- 여유: 9,280 units (92%)

### Q: POC는 왜 하나요?
**A:** "안되는 걸 구현"하지 않기 위해!
- Analytics API가 실제 작동하는지 확인
- 트래픽 소스 데이터를 받을 수 있는지 확인
- 할당량 실측
- 설계 최종 검증

---

## 🛠️ 다음 단계

### POC 성공 후

#### Phase 1: 데이터 수집 (3-4일)
```
□ 데이터베이스 스키마 구현 (SQLite)
□ YouTube API Wrapper 작성
□ 토큰 관리 시스템
□ 수집 스크립트
□ 스케줄러 설정
□ 테스트
```

#### Phase 2: 대시보드 (3-4일)
```
□ Streamlit 레이아웃
□ 사이드바 네비게이션
□ 전체 현황 페이지
□ 채널 상세 페이지
□ 트래픽 소스 차트
□ 필터 및 날짜 선택
```

#### Phase 3: 고도화 (1주)
```
□ 인사이트 자동 생성
□ 알림 기능
□ 성능 최적화
□ 에러 처리 강화
□ 문서화
```

---

## 💡 팁

### 개발 순서 (추천)
1. POC로 검증 (지금!)
2. 1개 채널로 프로토타입
3. 10개 채널로 확장
4. 대시보드 추가
5. 자동화 및 알림
6. 고도화

### 막히면?
1. DESIGN_VALIDATION.md 의 문제 해결
2. GCP_SETUP_GUIDE.md 의 FAQ
3. Google API 공식 문서
4. Stack Overflow

### 잘 모르겠으면?
설계 문서를 다시 읽어보세요. 거의 모든 답이 있습니다!

---

## 📝 변경 이력

| 날짜 | 내용 |
|------|------|
| 2024-01-15 | 초안 작성, POC 스크립트 생성 |

---

**준비됐나요? POC 시작! 🚀**

```bash
cd poc_scripts
python poc_setup.py
```
