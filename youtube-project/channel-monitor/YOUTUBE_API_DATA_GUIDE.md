# YouTube API 데이터 가이드

## 📋 목차
1. [개요](#개요)
2. [YouTube Data API v3](#youtube-data-api-v3)
3. [YouTube Analytics API](#youtube-analytics-api)
4. [실제 데이터 예시](#실제-데이터-예시)
5. [활용 시나리오](#활용-시나리오)
6. [제약사항](#제약사항)

---

## 개요

### API 비교 요약

| 구분 | Data API v3 | Analytics API |
|------|-------------|---------------|
| **용도** | 공개 정보 조회, 관리 | 소유 채널 상세 분석 |
| **권한** | 누구나 사용 가능 | 채널 소유자만 |
| **할당량** | 일 10,000 units | 관대 (비공개) |
| **핵심 기능** | 채널/영상/댓글 정보 | 트래픽 소스, 시청 패턴 |

---

## YouTube Data API v3

### 1. 채널 정보 (`channels.list`)

**조회 가능 데이터:**

```yaml
기본 정보 (snippet):
  - 채널명
  - 설명
  - 개설일
  - 프로필 이미지 URL
  - 배너 이미지 URL
  - 국가

통계 (statistics):
  - 구독자 수 ⭐
  - 총 조회수
  - 영상 개수
  - 숨겨진 구독자 수 여부

콘텐츠 (contentDetails):
  - 업로드 플레이리스트 ID
  - 관련 플레이리스트들

브랜딩 (brandingSettings):
  - 채널 키워드
  - 기본 탭 설정
```

**할당량:** 1 unit

**실제 예시 (세상발견 World Discovery):**
```json
{
  "채널 ID": "UCmGKhWPtsKf-6pgso7PvDhQ",
  "채널명": "세상발견 World Discovery",
  "구독자": 2760,
  "총 조회수": 9913394,
  "영상 수": 73
}
```

---

### 2. 영상 정보 (`videos.list`)

**조회 가능 데이터:**

```yaml
기본 정보 (snippet):
  - 제목 ⭐
  - 설명
  - 업로드 시간 ⭐
  - 썸네일 URL (여러 해상도)
  - 채널 ID/이름
  - 태그
  - 카테고리 ID
  - 라이브 방송 여부

통계 (statistics):
  - 조회수 ⭐
  - 좋아요 수 ⭐
  - 댓글 수 ⭐
  - (싫어요는 2021년부터 비공개)

콘텐츠 상세 (contentDetails):
  - 영상 길이 (duration) ⭐
  - 해상도 (HD/SD)
  - 자막 여부
  - 라이선스 타입

상태 (status):
  - 공개 상태 (공개/비공개/일부공개)
  - 업로드 상태
  - 저작권 이슈 여부
```

**할당량:** 1 unit

**활용:**
- 최신 영상 추적
- 조회수 변화 모니터링
- 인기 영상 식별

---

### 3. 영상 목록 조회 (`playlistItems.list`)

**업로드 영상 목록 가져오기:**

```yaml
조회 데이터:
  - 영상 ID 목록
  - 업로드 순서
  - 제목/썸네일 (snippet 포함 시)

정렬:
  - 최신순 (기본)
  - 오래된 순

페이징:
  - maxResults: 최대 50개/요청
  - nextPageToken으로 다음 페이지
```

**할당량:** 1 unit

**활용:**
- 채널의 모든 영상 수집
- 최신 업로드 영상 감지

---

### 4. 댓글 조회 (`commentThreads.list`)

**조회 가능 데이터:**

```yaml
댓글:
  - 작성자 이름/프로필
  - 댓글 내용 ⭐
  - 작성 시간
  - 좋아요 수
  - 답글 수

대댓글 (replies):
  - 작성자
  - 내용
  - 작성 시간

정렬 옵션:
  - 인기순 (relevance)
  - 최신순 (time)
```

**할당량:** 1 unit

**활용:**
- 시청자 반응 분석
- 감정 분석 (긍정/부정)
- 주요 키워드 추출

**제약:**
- 댓글 비활성화 시 조회 불가
- 일부 댓글 숨김 처리 시 누락 가능

---

### 5. 검색 (`search.list`)

**기능:**
- 채널 내 영상 검색
- 키워드로 영상 찾기

**할당량:** 100 units ⚠️ (매우 비쌈!)

**권장:**
- 가급적 사용 자제
- playlistItems.list 사용 권장

---

## YouTube Analytics API

### 1. 기본 시청 메트릭 (`reports.query`)

**조회 가능 메트릭:**

```yaml
조회 관련:
  - views: 조회수 ⭐
  - redViews: YouTube Red 조회수
  - averageViewPercentage: 평균 시청률

시청 시간:
  - estimatedMinutesWatched: 총 시청 시간 (분) ⭐
  - averageViewDuration: 평균 시청 시간 (초) ⭐

참여도:
  - likes: 좋아요 수 ⭐
  - dislikes: 싫어요 수 (2021년 이후 0)
  - comments: 댓글 수 ⭐
  - shares: 공유 수 ⭐
  - subscribersGained: 구독자 증가 ⭐
  - subscribersLost: 구독자 감소

클릭률:
  - cardClicks: 카드 클릭
  - cardImpressions: 카드 노출
  - cardClickRate: 카드 클릭률
```

**Dimensions (세분화 기준):**
```yaml
시간:
  - day: 일별 ⭐
  - month: 월별

콘텐츠:
  - video: 영상별 ⭐
  - playlist: 재생목록별

지역:
  - country: 국가별
  - province: 지역별 (미국만)
```

**실제 예시:**
```
날짜별 조회수 (2025-10-17 ~ 2025-10-19):
  - 2025-10-17: 750회, 399분 시청, 평균 45초
  - 2025-10-18: 1,027회, 525분 시청, 평균 43초
  - 2025-10-19: 1,005회, 488분 시청, 평균 44초
```

---

### 2. 트래픽 소스 분석 ⭐⭐⭐ (핵심!)

**Dimension: `insightTrafficSourceType`**

**조회 가능 소스:**

```yaml
YouTube 내부:
  - YT_SEARCH: YouTube 검색 ⭐
    → SEO 성과 측정

  - RELATED_VIDEO: 추천 영상 (알고리즘!) ⭐⭐⭐
    → 알고리즘이 선택한 영상!
    → 이게 높으면 "떴다"는 의미

  - SUBSCRIBER: 구독 피드 ⭐
    → 충성 시청자

  - BROWSE: 탐색/홈 피드
    → YouTube 홈 화면 노출

  - NOTIFICATION: 알림
    → 구독자 알림 클릭

  - PLAYLIST: 재생목록

  - CHANNEL: 채널 페이지
    → 채널 직접 방문

  - SHORTS: YouTube Shorts 피드
    → Shorts 알고리즘

외부:
  - EXT_URL: 외부 링크 ⭐
    → SNS, 블로그, 웹사이트

  - NO_LINK_EMBEDDED: 임베드 재생
    → 외부 사이트 삽입

기타:
  - END_SCREEN: 최종 화면
  - CAMPAIGN_CARD: 캠페인 카드
  - ANNOTATION: 주석 (구버전)
```

**실제 예시 (세상발견 World Discovery, 최근 7일):**
```
총 조회수: 4,787회

1. YouTube 검색:   1,965회 (41.0%) ← SEO 최적화 잘됨!
2. 구독 피드:       1,647회 (34.4%) ← 충성 팬층
3. 추천 영상:         618회 (12.9%) ← 알고리즘 선택! ⭐
4. SHORTS:          436회 (9.1%)
5. YT_CHANNEL:       76회 (1.6%)
6. 외부 링크:          8회 (0.2%)
7. 재생목록:           5회 (0.1%)
```

**인사이트:**
- **추천 영상 비율이 높음** = 알고리즘이 영상을 선택
- **검색 비율이 높음** = 제목/태그 SEO가 좋음
- **구독 피드 비율이 높음** = 충성 시청자 많음
- **외부 링크 증가** = SNS 홍보 성공

---

### 3. 세부 트래픽 소스 (`insightTrafficSourceDetail`)

**더 상세한 분석 (⚠️ 제한적):**

```yaml
검색 키워드:
  - 어떤 검색어로 유입됐는지
  - ⚠️ 일부만 제공 (프라이버시)

외부 URL:
  - 정확히 어떤 사이트에서 왔는지
  - 예: facebook.com, twitter.com

추천 영상 ID:
  - 어떤 영상에서 추천됐는지
  - ⚠️ 제한적
```

---

### 4. 인구통계 분석

**Dimension: `ageGroup`, `gender`**

```yaml
연령대 (ageGroup):
  - age13-17: 13-17세
  - age18-24: 18-24세 ⭐
  - age25-34: 25-34세 ⭐
  - age35-44: 35-44세
  - age45-54: 45-54세
  - age55-64: 55-64세
  - age65-: 65세 이상

성별 (gender):
  - male: 남성
  - female: 여성
  - user_specified: 기타

지역 (country):
  - 국가 코드 (KR, US, JP 등)
```

**활용:**
- 타겟 시청자 파악
- 콘텐츠 방향 결정
- 광고 타겟팅 최적화

---

### 5. 시청 유지율 (Audience Retention)

**메트릭: `audienceWatchRatio`, `relativeRetentionPerformance`**

```yaml
데이터:
  - 영상의 어느 시점에서 시청자가 이탈하는지
  - 구간별 시청 유지율
  - 평균 대비 성과

활용:
  - 어느 부분이 지루한지 파악
  - 인트로 길이 최적화
  - 하이라이트 구간 식별
```

**⚠️ 제약:**
- 영상별로만 조회 가능
- 일정 조회수 이상 필요 (정확한 수치 비공개)

---

### 6. 재생 위치 (Playback Location)

**Dimension: `insightPlaybackLocationType`**

```yaml
위치:
  - WATCH: YouTube 시청 페이지 ⭐
  - EMBEDDED: 외부 사이트 삽입 재생
  - CHANNEL: 채널 페이지
  - MOBILE: 모바일 앱
  - CREATOR_STUDIO: 크리에이터 스튜디오
```

---

### 7. 디바이스 유형

**Dimension: `deviceType`, `operatingSystem`**

```yaml
디바이스:
  - DESKTOP: PC ⭐
  - MOBILE: 모바일 ⭐
  - TABLET: 태블릿
  - TV: TV/게임 콘솔

운영체제:
  - Android
  - iOS
  - Windows
  - Mac
  - PlayStation
  - Xbox
  등등
```

---

### 8. 구독 상태별 시청

**Dimension: `subscribedStatus`**

```yaml
상태:
  - SUBSCRIBED: 구독자 시청
  - UNSUBSCRIBED: 비구독자 시청

활용:
  - 신규 유입 vs 기존 팬 비율
  - 구독 전환율 분석
```

---

### 9. 카드 & 최종 화면 성과

```yaml
메트릭:
  - cardClicks: 카드 클릭 수
  - cardClickRate: 클릭률
  - cardTeaserClicks: 티저 클릭

  - annotationClicks: 주석 클릭 (구버전)
  - annotationClickThroughRate: 주석 클릭률
```

---

## 실제 데이터 예시

### POC 테스트 결과 (세상발견 World Discovery)

#### 채널 개요
```
채널명: 세상발견 World Discovery
구독자: 2,760명
총 조회수: 9,913,394회
영상 수: 73개
```

#### 최근 7일 성과 (2025-10-13 ~ 2025-10-20)
```
총 조회수: 4,787회
총 시청시간: 2,587분 (43시간)
평균 시청시간: 43초
일 평균 조회수: 684회
```

#### 트래픽 소스 분석
```
1위: YouTube 검색 (41.0%)
     → 키워드 SEO가 효과적

2위: 구독 피드 (34.4%)
     → 충성 팬 비율 높음

3위: 추천 영상 (12.9%)
     → 알고리즘이 일부 선택
     → 더 높이려면 시청 유지율 개선 필요

4위: Shorts (9.1%)
     → Shorts 콘텐츠 효과
```

#### 최신 영상 성과
```
영상: "인류 역사상 가장 낭만적인 여행..."
업로드: 2025-08-06
7일간 성과:
  - 조회수: 172회
  - 좋아요: 1
  - 시청시간: 402분
  - 평균 시청: 140초
```

---

## 활용 시나리오

### 시나리오 1: 알고리즘 선택 모니터링 ⭐

**목적:** 어떤 영상이 알고리즘에 선택됐는지 파악

**필요 데이터:**
```python
# Analytics API
dimensions: ['video', 'insightTrafficSourceType']
metrics: ['views', 'estimatedMinutesWatched']
filters: insightTrafficSourceType == 'RELATED_VIDEO'
sort: '-views'
```

**인사이트:**
- 추천 영상 조회수 Top 5 식별
- 공통 패턴 분석 (길이, 주제, 썸네일 등)
- 성공 요인 재현

---

### 시나리오 2: 일일 성과 대시보드

**표시 정보:**
```yaml
채널 전체:
  - 어제 총 조회수
  - 어제 시청시간
  - 전일 대비 증감률
  - 구독자 증감

최신 영상 (최근 7일):
  - 영상별 조회수
  - 트래픽 소스 분포
  - 평균 시청시간
  - 좋아요/댓글 수

알림:
  - 조회수 급증 영상 (전일 대비 +50%)
  - 알고리즘 선택된 영상 (추천 비율 >30%)
```

---

### 시나리오 3: 경쟁 채널 비교 (제한적)

**가능:**
```yaml
Data API로 조회:
  - 구독자 수 변화
  - 영상 업로드 빈도
  - 조회수 패턴
  - 인기 영상 제목/태그

⚠️ Analytics API는 불가:
  - 타인 채널의 트래픽 소스 조회 불가
  - 자신의 채널만 상세 분석 가능
```

---

### 시나리오 4: SEO 최적화

**분석 데이터:**
```yaml
트래픽 소스:
  - YT_SEARCH 비율

검색 유입 영상:
  - 제목 패턴
  - 태그 분석
  - 설명 키워드

개선:
  - 검색 친화적 제목 작성
  - 관련 태그 추가
  - 썸네일 A/B 테스트
```

---

### 시나리오 5: 콘텐츠 전략 개선

**데이터 기반 의사결정:**
```yaml
시청 유지율 분석:
  - 인트로가 너무 긴가? (처음 30초 이탈률)
  - 어느 구간이 지루한가?

인구통계:
  - 실제 시청자 연령대
  - 성별 분포
  → 타겟 조정

트래픽 소스:
  - 외부 유입이 적다면 SNS 홍보 강화
  - 추천 영상이 많다면 현재 전략 유지
  - 검색이 많다면 SEO 집중
```

---

## 제약사항

### 1. 데이터 지연

```yaml
Data API:
  - 거의 실시간 (몇 분 지연)
  - 조회수는 48시간 이내 최종 확정

Analytics API:
  - 24-48시간 지연 ⚠️
  - 최근 2일 데이터는 부정확
  - 주말/공휴일 더 느림
```

**권장:**
- 최소 2일 전까지 데이터만 분석
- 일일 리포트는 "어제" 데이터 기준

---

### 2. 할당량 제한

```yaml
Data API:
  - 일일 10,000 units
  - channels.list: 1 unit
  - videos.list: 1 unit
  - playlistItems.list: 1 unit
  - search.list: 100 units ⚠️

예상 사용량 (10개 채널):
  - 1시간마다 수집 시: 720 units/일
  - 여유: 9,280 units (92%)
  - 충분함! ✅
```

**최적화 팁:**
- search 대신 playlistItems 사용
- 배치 요청 활용 (최대 50개)
- 변하지 않는 데이터는 캐싱

---

### 3. 비공개 데이터

```yaml
조회 불가:
  - 싫어요 수 (2021년부터 비공개)
  - 일부 검색 키워드 (프라이버시)
  - 정확한 추천 영상 ID (제한적)
  - 수익 정보 (일부만 제공)

제한적 제공:
  - 시청 유지율 (일정 조회수 필요)
  - 세부 트래픽 소스 (샘플링)
```

---

### 4. 최소 조회수 요구

```yaml
일부 메트릭은 최소 조회수 필요:
  - 시청 유지율
  - 세부 인구통계
  - 정확한 수치 비공개

작은 채널:
  - 데이터가 "0" 또는 누락될 수 있음
  - 집계 데이터만 제공
```

---

### 5. 계정 권한

```yaml
필수:
  - 채널 소유자 계정으로 OAuth 인증
  - 테스트 사용자로 추가 (개발 단계)

불가:
  - 타인 채널의 Analytics 데이터
  - 권한 없는 비공개 영상
```

---

## 다음 단계

### POC 완료 후

```yaml
✅ 확인된 것:
  - Data API 작동
  - Analytics API 작동
  - 트래픽 소스 조회 가능
  - 실제 데이터 검증

⬜ 다음 작업:
  1. 필요한 메트릭 확정
  2. 데이터베이스 스키마 설계
  3. 수집 스크립트 개발
  4. 대시보드 설계
```

---

## 참고 자료

### 공식 문서
- [YouTube Data API v3 Reference](https://developers.google.com/youtube/v3/docs)
- [YouTube Analytics API Reference](https://developers.google.com/youtube/analytics/reference)
- [Metrics & Dimensions](https://developers.google.com/youtube/analytics/dimensions)

### 프로젝트 문서
- `DESIGN_VALIDATION.md` - 전체 설계 검증
- `README_POC.md` - POC 가이드
- `GCP_SETUP_GUIDE.md` - OAuth 설정

---

**작성일:** 2025-10-22
**POC 테스트 완료:** account1 (박준현), account2 (세상발견 World Discovery)
