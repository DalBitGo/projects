# 📺 YouTube 구독 채널 피드

> 구독한 채널의 최신 영상을 한눈에 보고, 쇼츠/롱폼을 구분하며, 효율적으로 관리하는 대시보드

[![Status](https://img.shields.io/badge/status-beta-yellow)]()
[![API](https://img.shields.io/badge/YouTube_API-v3-red)]()
[![Cost](https://img.shields.io/badge/cost-free-brightgreen)]()

---

## 🚀 빠른 시작

### 1. 데이터 수집 (처음 1회)
```bash
python collectors/feed_collector.py
```

**결과:**
- ✅ 구독 채널 81개 수집
- ✅ 영상 2,198개 수집 (쇼츠 33% / 롱폼 67%)
- ✅ 소요 시간 82초
- ✅ API Quota 245 units (2.45%)

### 2. 대시보드 실행
```bash
streamlit run app/feed_dashboard.py --server.port=8504
```

**접속:** http://localhost:8504

---

## ✨ 주요 기능

### 📱 쇼츠 / 🎬 롱폼 구분
- 60초 기준 자동 분류
- 탭으로 분리해서 보기
- 각 포맷별 통계

### 🔍 필터 & 정렬
- **기간**: 오늘 / 어제 / 지난 7일 / 지난 30일 / 전체
- **정렬**: 최신순 / 조회수순 / 좋아요순 / 댓글수순
- **옵션**: 🆕 새 영상만 보기

### 📺 채널 관리
- 체크박스로 채널 선택
- 수집 대상 채널 관리
- 전체 선택/해제

### 🔄 새로고침
- 버튼 클릭으로 즉시 수집
- 증분 업데이트 (새 영상만)
- API quota 자동 표시

### 📊 실시간 통계
- 활성 채널 수
- 전체 영상 수
- 쇼츠 / 롱폼 비율
- 🆕 새 영상 수

---

## 📊 데이터 구조

```
구독 채널 (81개)
  └─ 최신 영상 (채널당 30개)
       ├─ 📱 쇼츠 (719개, 32.7%)
       └─ 🎬 롱폼 (1,479개, 67.3%)
```

**증분 업데이트:**
- 첫 수집: 2,198개 영상
- 이후 수집: 새 영상만 (예상 10-50개)
- API quota 8배 절약!

---

## 💰 비용

| 항목 | 값 |
|------|-----|
| 일일 무료 할당량 | 10,000 units |
| 현재 수집 시 사용량 | 245 units (2.45%) |
| 하루 최대 수집 가능 | 약 40회 |
| 총 비용 | **$0 (완전 무료)** |

**API quota 체크:**
```bash
python utils/quota_checker.py
```

---

## 🗄 데이터베이스

**테이블:**
- `subscribed_channels` - 구독 채널 정보
- `feed_videos` - 피드 영상 정보
- `feed_collection_history` - 수집 이력
- `feed_transcripts` - 자막 메타데이터 (선택)

**위치:** `data/youtube.db` (152KB)

---

## 🎯 사용 시나리오

### 아침 루틴 (5분)
```
1. 대시보드 열기
2. "어제" 필터 선택
3. 조회수순 정렬
4. 관심 영상 클릭 → YouTube에서 보기
```

### 주간 체크 (10분)
```
1. "지난 7일" 필터
2. 쇼츠 vs 롱폼 비교
3. 🆕 새 영상 확인
4. 트렌드 파악
```

### 채널 관리 (필요 시)
```
1. 사이드바 "채널 관리" 열기
2. 체크박스로 선택/해제
3. 불필요한 채널 비활성화
```

---

## 🛠 기술 스택

- **Backend**: Python 3.10, SQLite
- **Frontend**: Streamlit
- **API**: YouTube Data API v3
- **기타**: emoji, google-api-python-client

---

## 📂 프로젝트 구조

```
channel-monitor/
├── app/
│   └── feed_dashboard.py         # 메인 대시보드
│
├── collectors/
│   └── feed_collector.py         # 데이터 수집
│
├── database/
│   ├── feed_schema.py            # DB 스키마
│   └── feed_operations.py        # DB 작업
│
├── utils/
│   └── quota_checker.py          # API quota 체크
│
├── data/
│   └── youtube.db                # SQLite DB
│
├── FEED_DEVELOPMENT_LOG.md       # 개발 히스토리
└── FEED_README.md                # 이 문서!
```

---

## 🔧 고급 사용법

### 수집 채널 수 조절
```python
# collectors/feed_collector.py
collector.collect_feed_videos(max_videos_per_channel=50)  # 기본 30개
```

### 자동 수집 (크론)
```bash
# 매일 오전 9시
0 9 * * * cd /path/to/channel-monitor && python collectors/feed_collector.py
```

### 채널 수동 추가
```sql
-- data/youtube.db
INSERT INTO subscribed_channels (channel_id, channel_name, is_active)
VALUES ('UC_x5XG1OV2P6uZZ5FSM9Ttw', 'Google Developers', 1);
```

---

## 🐛 트러블슈팅

### Q1: "채널 데이터가 없습니다"
```bash
# 데이터 수집 먼저 실행
python collectors/feed_collector.py
```

### Q2: API quota 초과
```bash
# 사용량 체크
python utils/quota_checker.py

# 다음날까지 대기 또는
# GCP Console에서 할당량 증가 요청
```

### Q3: 중복 키 에러
```bash
# 페이지 새로고침
# 또는 브라우저 캐시 삭제
```

---

## 📈 성과 지표

### 개발
- **개발 기간**: 1일
- **코드 라인**: ~1,450줄
- **완성도**: 85% (자막 제외)

### 수집
- **구독 채널**: 81개
- **총 영상**: 2,198개
- **API Quota**: 2.45%
- **소요 시간**: 82초

### 비용
- **API**: $0
- **인프라**: $0
- **총**: **$0**

---

## 🎯 다음 단계 (선택)

### Phase 2: 인사이트 (2-3일)
- 핫 키워드 TOP 10
- 성공 영상 패턴 분석
- 쇼츠 vs 롱폼 비교
- 액션 아이템 자동 생성

### Phase 3: 자막 (1일)
- youtube-transcript-api 연동
- 다운로드 버튼 활성화
- TXT/JSON/SRT 포맷

### Phase 4: 카테고리 (1-2일)
- 카테고리 CRUD
- 채널 태그
- 카테고리별 필터

---

## 📚 관련 문서

- **FEED_DEVELOPMENT_LOG.md** - 개발 과정 상세 (800줄)
- **SUBSCRIPTION_FEED_DESIGN.md** - 기획서 (650줄)
- **README.md** - 전체 프로젝트 (기존)

---

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

---

## 📝 변경 이력

### v0.9-beta - 2025-10-24
- ✅ 구독 채널 수집
- ✅ 피드 영상 수집
- ✅ 쇼츠/롱폼 구분
- ✅ 대시보드 UI
- ✅ 필터 & 정렬
- ✅ 채널 관리
- ✅ 새로고침 버튼
- ⏳ 자막 다운로드 (예정)

---

**Made with ❤️ for Better YouTube Experience**

개발: 2025-10-24
버전: 0.9-beta
라이선스: MIT
