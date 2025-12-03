# YouTube Data API v3 완전 가이드

**작성일**: 2025-10-20
**목적**: 채널 모니터링 프로젝트를 위한 YouTube Data API v3 심층 분석
**공식 문서**: https://developers.google.com/youtube/v3

---

## 목차
1. [API 개요](#1-api-개요)
2. [인증 및 설정](#2-인증-및-설정)
3. [할당량 시스템](#3-할당량-시스템)
4. [핵심 리소스 타입](#4-핵심-리소스-타입)
5. [채널 모니터링 필수 엔드포인트](#5-채널-모니터링-필수-엔드포인트)
6. [데이터 구조 상세](#6-데이터-구조-상세)
7. [최적화 전략](#7-최적화-전략)
8. [에러 처리](#8-에러-처리)
9. [실전 사용 패턴](#9-실전-사용-패턴)
10. [할당량 계산 예시](#10-할당량-계산-예시)

---

## 1. API 개요

### 1.1 YouTube Data API v3란?

**정의**: YouTube의 데이터(채널, 영상, 재생목록, 댓글 등)에 접근하고 관리할 수 있는 RESTful API

**주요 기능**:
- ✅ 채널 정보 조회 (구독자, 조회수, 영상 목록)
- ✅ 영상 메타데이터 및 통계
- ✅ 댓글 및 대댓글 수집
- ✅ 재생목록 관리
- ✅ 검색 (채널, 영상, 재생목록)
- ✅ 구독 관리 (OAuth 필요)

**특징**:
- HTTP 기반 (GET, POST, PUT, DELETE)
- JSON 데이터 형식
- 페이지네이션 지원 (nextPageToken)
- 부분 리소스 조회 (fields 파라미터)
- ETag를 통한 캐싱

**최신 업데이트**: 2025년 10월 (공식 문서 최근 업데이트 날짜)

---

## 2. 인증 및 설정

### 2.1 사전 요구사항

**필수**:
1. Google 계정
2. Google Developers Console 프로젝트
3. YouTube Data API v3 활성화
4. 인증 크레덴셜 (API 키 또는 OAuth 2.0)

### 2.2 인증 방식

| 방식 | 용도 | 장점 | 단점 |
|------|------|------|------|
| **API Key** | 공개 데이터 읽기 | 간단, 서버 간 통신 용이 | 쓰기 불가, 사용자 특정 불가 |
| **OAuth 2.0** | 사용자 데이터 읽기/쓰기 | 전체 기능 사용 가능 | 복잡, 사용자 승인 필요 |

### 2.3 API 키 발급 및 설정

#### Step 1: Google Cloud Console에서 프로젝트 생성
1. https://console.cloud.google.com 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택

#### Step 2: YouTube Data API v3 활성화
1. "API 및 서비스" > "라이브러리" 메뉴
2. "YouTube Data API v3" 검색
3. "사용 설정" 클릭

#### Step 3: API 키 생성
1. "API 및 서비스" > "사용자 인증 정보"
2. "+ 사용자 인증 정보 만들기" > "API 키"
3. 생성된 키 복사 및 저장

#### Step 4: API 키 제한 (보안 강화)

**애플리케이션 제한**:
```
IP 주소 제한:
- 서버 IP 주소 추가
- 개발용 로컬 IP 추가
```

**API 제한**:
```
YouTube Data API v3만 선택
→ 다른 API에 오용 방지
```

### 2.4 환경 변수 관리

**Linux/Mac (.bashrc or .zshrc)**:
```bash
export YOUTUBE_API_KEY="AIzaSy..."
```

**Windows (PowerShell)**:
```powershell
$env:YOUTUBE_API_KEY="AIzaSy..."
```

**Python (.env 파일 + python-dotenv)**:
```env
YOUTUBE_API_KEY=AIzaSy...
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')
```

---

## 3. 할당량 시스템

### 3.1 기본 할당량

**기본 제공**: **10,000 units/day**
- 매일 자정 (Pacific Time) 초기화
- 프로젝트당 할당량 (앱당 아님)
- 무료로 사용 가능

**확장 요청**:
- Quota extension request form 제출
- Compliance Audit 통과 필요
- 승인 시 무료로 확장 (금전적 비용 없음)

### 3.2 할당량 계산 원리

**기본 원칙**:
1. 모든 요청은 **최소 1 unit** 소모
2. 잘못된 요청도 비용 청구
3. 읽기 < 쓰기 < 검색 < 업로드 순으로 비용 증가

**할당량 공식**:
```
총 비용 = Σ (API 메서드 비용 + part 파라미터 비용)
```

### 3.3 주요 작업별 할당량 비용

#### 기본 메서드 비용

| 리소스 | 메서드 | 비용 (units) | 비고 |
|--------|--------|--------------|------|
| **channels** | list | 1 | 채널 정보 조회 |
| **channels** | update | 50 | 채널 정보 수정 |
| **videos** | list | 1 | 영상 정보 조회 |
| **videos** | insert | 1,600 | 영상 업로드 (최고 비용) |
| **videos** | update | 50 | 영상 정보 수정 |
| **videos** | delete | 50 | 영상 삭제 |
| **videos** | rate | 50 | 좋아요/싫어요 |
| **search** | list | 100 | 검색 (높은 비용) |
| **commentThreads** | list | 1 | 댓글 스레드 조회 |
| **commentThreads** | insert | 50 | 댓글 작성 |
| **comments** | list | 1 | 대댓글 조회 |
| **comments** | insert | 50 | 대댓글 작성 |
| **playlists** | list | 1 | 재생목록 조회 |
| **playlistItems** | list | 1 | 재생목록 항목 조회 |
| **subscriptions** | list | 1 | 구독 목록 조회 |
| **subscriptions** | insert | 50 | 구독 |

#### part 파라미터 비용

**중요**: `part` 파라미터는 추가 비용 없음! (DannyIbo 코드 분석에서 오해한 부분)

```python
# 모두 1 unit
videos().list(part="snippet")
videos().list(part="snippet,statistics")
videos().list(part="snippet,statistics,contentDetails")
```

**예외**: `fileDetails`, `processingDetails`, `suggestions`는 높은 비용

### 3.4 할당량 모니터링

**Google Cloud Console**:
1. "API 및 서비스" > "할당량"
2. YouTube Data API v3 선택
3. 일일 사용량 그래프 확인

**프로그래매틱 모니터링**:
```python
# API 응답 헤더에서 확인 (공식 지원 안 함)
# 로그로 비용 수동 계산 필요
```

### 3.5 할당량 초과 시 에러

**에러 코드**: `403 Forbidden`

**에러 메시지**:
```json
{
  "error": {
    "code": 403,
    "message": "The request cannot be completed because you have exceeded your quota.",
    "errors": [{
      "domain": "youtube.quota",
      "reason": "quotaExceeded"
    }]
  }
}
```

**대응 방법**:
1. 요청 최적화 (배치 처리, 캐싱)
2. 할당량 확장 요청
3. 다음 날까지 대기

---

## 4. 핵심 리소스 타입

### 4.1 리소스 개요

**리소스(Resource)**: YouTube의 데이터 객체 (채널, 영상, 댓글 등)

**주요 리소스**:
1. **channel** - YouTube 채널
2. **video** - 영상
3. **playlist** - 재생목록
4. **playlistItem** - 재생목록 항목
5. **commentThread** - 댓글 스레드 (top-level 댓글 + 대댓글)
6. **comment** - 개별 댓글
7. **subscription** - 구독 정보
8. **search** - 검색 결과 (가상 리소스)

### 4.2 리소스 공통 구조

**parts 구조**:
모든 리소스는 여러 "part"로 구성됨

```json
{
  "kind": "youtube#video",
  "etag": "...",
  "id": "video_id",
  "snippet": { /* 기본 정보 */ },
  "contentDetails": { /* 콘텐츠 상세 */ },
  "statistics": { /* 통계 */ },
  "status": { /* 상태 */ }
}
```

**주요 parts**:

| Part | 설명 | 포함 정보 | 비용 |
|------|------|----------|------|
| **id** | 리소스 ID | 고유 식별자 | 0 |
| **snippet** | 기본 정보 | 제목, 설명, 썸네일, 게시일 | 2 |
| **contentDetails** | 콘텐츠 상세 | 영상 길이, 화질, 자막 여부 | 2 |
| **statistics** | 통계 | 조회수, 좋아요, 댓글 수 | 2 |
| **status** | 상태 | 공개 여부, 업로드 상태 | 2 |
| **topicDetails** | 주제 | 카테고리, 태그 | 2 |
| **player** | 플레이어 | 임베드 HTML | 0 |
| **recordingDetails** | 녹화 정보 | 녹화 위치, 날짜 | 2 |
| **fileDetails** | 파일 상세 | 파일 크기, 비트레이트 (업로더만) | 1 |
| **processingDetails** | 처리 상태 | 인코딩 진행 상황 (업로더만) | 1 |
| **suggestions** | 제안 | 개선 제안 (업로더만) | 1 |

**note**: DannyIbo 코드 분석에서 본 주석 "snippet 2, statistics 2"는 **과거 비용 체계**. 현재는 part별 비용 없음 (메서드 기본 비용만).

---

## 5. 채널 모니터링 필수 엔드포인트

### 5.1 channels.list

**용도**: 채널 기본 정보 및 통계 조회

**HTTP 요청**:
```
GET https://www.googleapis.com/youtube/v3/channels
```

**필수 파라미터**:
- `part` (string): 조회할 리소스 parts (콤마 구분)
- `id` OR `forUsername` OR `mine`: 채널 식별자

**주요 파라미터**:

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `part` | string | ✅ | snippet, contentDetails, statistics 등 |
| `id` | string | 택1 | 채널 ID (콤마 구분, 최대 50개) |
| `forUsername` | string | 택1 | 사용자명 (레거시, 비추천) |
| `mine` | boolean | 택1 | 인증된 사용자의 채널 (OAuth 필요) |
| `maxResults` | integer | - | 결과 수 (기본 5, 최대 50) |

**응답 예시**:
```json
{
  "kind": "youtube#channelListResponse",
  "etag": "...",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 1
  },
  "items": [{
    "kind": "youtube#channel",
    "etag": "...",
    "id": "UCqC_GY2ZiENFz2pwL0cSfAw",
    "snippet": {
      "title": "채널 이름",
      "description": "채널 설명",
      "customUrl": "@channelname",
      "publishedAt": "2010-05-19T00:44:27Z",
      "thumbnails": {
        "default": { "url": "...", "width": 88, "height": 88 },
        "medium": { "url": "...", "width": 240, "height": 240 },
        "high": { "url": "...", "width": 800, "height": 800 }
      },
      "localized": {
        "title": "...",
        "description": "..."
      },
      "country": "US"
    },
    "contentDetails": {
      "relatedPlaylists": {
        "likes": "playlist_id",
        "uploads": "UUqC_GY2ZiENFz2pwL0cSfAw"  // 업로드 재생목록 ID (중요!)
      }
    },
    "statistics": {
      "viewCount": "1234567890",
      "subscriberCount": "1000000",  // 3 significant figures로 반올림됨
      "hiddenSubscriberCount": false,
      "videoCount": "500"
    }
  }]
}
```

**중요 포인트**:
1. **subscriberCount 반올림**: 예를 들어 1,234,567명 → "1230000"
2. **uploads 재생목록 ID**: `contentDetails.relatedPlaylists.uploads`에서 채널의 모든 영상 목록 가져올 수 있음
3. **배치 조회**: `id` 파라미터에 최대 50개 채널 ID를 콤마로 연결하여 한 번에 조회 가능

**할당량**: 1 unit

### 5.2 playlistItems.list

**용도**: 채널의 모든 영상 ID 목록 가져오기

**HTTP 요청**:
```
GET https://www.googleapis.com/youtube/v3/playlistItems
```

**필수 파라미터**:
- `part` (string): 조회할 parts
- `playlistId` (string): 재생목록 ID (channels.list의 uploads ID 사용)

**주요 파라미터**:

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `part` | string | ✅ | snippet, contentDetails 등 |
| `playlistId` | string | ✅ | 재생목록 ID |
| `maxResults` | integer | - | 결과 수 (기본 5, 최대 50) |
| `pageToken` | string | - | 다음 페이지 토큰 |

**응답 예시**:
```json
{
  "kind": "youtube#playlistItemListResponse",
  "nextPageToken": "CAUQAA",  // 다음 페이지 토큰 (페이지네이션)
  "pageInfo": {
    "totalResults": 500,
    "resultsPerPage": 50
  },
  "items": [{
    "kind": "youtube#playlistItem",
    "id": "...",
    "snippet": {
      "publishedAt": "2023-01-01T00:00:00Z",
      "channelId": "UCqC_GY2ZiENFz2pwL0cSfAw",
      "title": "영상 제목",
      "description": "영상 설명",
      "resourceId": {
        "kind": "youtube#video",
        "videoId": "dQw4w9WgXcQ"  // 실제 영상 ID
      }
    }
  }]
}
```

**페이지네이션 처리**:
```python
def get_all_video_ids(youtube, playlist_id):
    video_ids = []
    next_page_token = None

    while True:
        response = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in response['items']:
            video_ids.append(item['snippet']['resourceId']['videoId'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids
```

**할당량**: 1 unit per page (채널 500개 영상 = 10페이지 = 10 units)

### 5.3 videos.list

**용도**: 영상 상세 정보 및 통계 조회

**HTTP 요청**:
```
GET https://www.googleapis.com/youtube/v3/videos
```

**필수 파라미터**:
- `part` (string): 조회할 parts
- `id` (string): 영상 ID (콤마 구분, 최대 50개)

**주요 parts 상세**:

#### snippet
```json
{
  "snippet": {
    "publishedAt": "2023-01-01T00:00:00Z",
    "channelId": "UCqC_GY2ZiENFz2pwL0cSfAw",
    "title": "영상 제목",
    "description": "영상 설명 (최대 5000자)",
    "thumbnails": { /* 썸네일 URL */ },
    "channelTitle": "채널 이름",
    "tags": ["tag1", "tag2"],  // 비디오 태그 배열
    "categoryId": "10",  // Music, Gaming 등
    "liveBroadcastContent": "none",  // none, upcoming, live
    "defaultLanguage": "ko",
    "localized": { /* 지역화 정보 */ },
    "defaultAudioLanguage": "ko"
  }
}
```

#### contentDetails
```json
{
  "contentDetails": {
    "duration": "PT1H23M45S",  // ISO 8601 형식 (1시간 23분 45초)
    "dimension": "2d",  // 2d or 3d
    "definition": "hd",  // hd or sd
    "caption": "true",  // 자막 있음
    "licensedContent": true,  // 라이선스 콘텐츠 여부
    "regionRestriction": {
      "allowed": ["US", "CA"],  // 허용 국가
      "blocked": ["KP"]  // 차단 국가
    },
    "contentRating": {
      "ytRating": "ytAgeRestricted"  // 연령 제한
    },
    "projection": "rectangular"  // rectangular or 360
  }
}
```

#### statistics
```json
{
  "statistics": {
    "viewCount": "1234567",
    "likeCount": "50000",
    "dislikeCount": "1000",  // deprecated (더 이상 제공 안 함)
    "favoriteCount": "0",  // deprecated
    "commentCount": "3000"
  }
}
```

#### status
```json
{
  "status": {
    "uploadStatus": "processed",  // deleted, failed, processed, rejected, uploaded
    "privacyStatus": "public",  // private, public, unlisted
    "license": "youtube",  // creativeCommon or youtube
    "embeddable": true,
    "publicStatsViewable": true,
    "madeForKids": false
  }
}
```

**배치 조회 예시**:
```python
# 최대 50개 영상 한 번에 조회
video_ids = ['id1', 'id2', ..., 'id50']
response = youtube.videos().list(
    part="snippet,contentDetails,statistics",
    id=','.join(video_ids)
).execute()
```

**할당량**: 1 unit (영상 개수 무관, 최대 50개)

### 5.4 commentThreads.list

**용도**: 영상 또는 채널의 댓글 스레드 조회 (top-level 댓글 + 최대 5개 대댓글)

**HTTP 요청**:
```
GET https://www.googleapis.com/youtube/v3/commentThreads
```

**필수 파라미터**:
- `part` (string): snippet, replies
- `videoId` OR `channelId` OR `id`: 필터 (택1)

**주요 파라미터**:

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `part` | string | ✅ | snippet, replies |
| `videoId` | string | 택1 | 영상 ID |
| `channelId` | string | 택1 | 채널 ID |
| `id` | string | 택1 | 댓글 스레드 ID |
| `maxResults` | integer | - | 결과 수 (기본 20, 최대 100) |
| `order` | string | - | time, relevance (기본) |
| `searchTerms` | string | - | 검색어 (채널 댓글만 가능) |
| `textFormat` | string | - | html (기본), plainText |

**응답 구조**:
```json
{
  "kind": "youtube#commentThreadListResponse",
  "nextPageToken": "...",
  "pageInfo": {
    "totalResults": 3000,
    "resultsPerPage": 100
  },
  "items": [{
    "kind": "youtube#commentThread",
    "id": "comment_thread_id",
    "snippet": {
      "channelId": "UCqC_GY2ZiENFz2pwL0cSfAw",
      "videoId": "dQw4w9WgXcQ",
      "topLevelComment": {
        "kind": "youtube#comment",
        "id": "top_comment_id",
        "snippet": {
          "authorDisplayName": "사용자 이름",
          "authorProfileImageUrl": "https://...",
          "authorChannelUrl": "https://www.youtube.com/channel/...",
          "authorChannelId": { "value": "UC..." },
          "textDisplay": "댓글 내용 (HTML)",
          "textOriginal": "댓글 내용 (Plain)",
          "canRate": true,
          "viewerRating": "none",  // none, like, dislike
          "likeCount": 42,
          "publishedAt": "2023-01-01T00:00:00Z",
          "updatedAt": "2023-01-01T00:00:00Z"
        }
      },
      "canReply": true,
      "totalReplyCount": 10,
      "isPublic": true
    },
    "replies": {
      "comments": [
        /* 최대 5개 대댓글 (comment 리소스 배열) */
      ]
    }
  }]
}
```

**중요 제약**:
- `replies` part를 요청해도 **최대 5개 대댓글**만 반환
- 5개 초과 시 `comments.list`로 추가 조회 필요 (DannyIbo 코드에서 본 복잡한 로직)

**할당량**: 1 unit per page

### 5.5 comments.list

**용도**: 특정 댓글 스레드의 모든 대댓글 조회

**HTTP 요청**:
```
GET https://www.googleapis.com/youtube/v3/comments
```

**필수 파라미터**:
- `part` (string): snippet
- `parentId` OR `id`: 필터 (택1)

**파라미터**:

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `part` | string | ✅ | snippet |
| `parentId` | string | 택1 | 부모 댓글 ID (대댓글 조회) |
| `id` | string | 택1 | 댓글 ID (최대 50개) |
| `maxResults` | integer | - | 결과 수 (기본 20, 최대 100) |

**응답 구조**:
```json
{
  "kind": "youtube#commentListResponse",
  "items": [{
    "kind": "youtube#comment",
    "id": "reply_comment_id",
    "snippet": {
      "authorDisplayName": "대댓글 작성자",
      "textOriginal": "대댓글 내용",
      "parentId": "top_comment_id",
      "likeCount": 5,
      "publishedAt": "2023-01-01T00:00:00Z",
      /* 나머지 필드는 commentThreads와 동일 */
    }
  }]
}
```

**할당량**: 1 unit per page

### 5.6 search.list

**용도**: 채널, 영상, 재생목록 검색

**HTTP 요청**:
```
GET https://www.googleapis.com/youtube/v3/search
```

**필수 파라미터**:
- `part` (string): snippet (id는 자동 포함)
- `q` OR `relatedToVideoId` OR `forMine` OR `forContentOwner`: 검색 조건 (택1)

**주요 파라미터**:

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `part` | string | snippet (필수) |
| `q` | string | 검색 키워드 |
| `channelId` | string | 특정 채널 내 검색 |
| `type` | string | video, channel, playlist (콤마 구분) |
| `order` | string | date, rating, relevance (기본), title, videoCount, viewCount |
| `publishedAfter` | datetime | 게시일 필터 (ISO 8601) |
| `publishedBefore` | datetime | 게시일 필터 |
| `maxResults` | integer | 결과 수 (기본 5, 최대 50) |

**응답 예시**:
```json
{
  "kind": "youtube#searchListResponse",
  "items": [{
    "kind": "youtube#searchResult",
    "id": {
      "kind": "youtube#video",
      "videoId": "dQw4w9WgXcQ"
    },
    "snippet": {
      "publishedAt": "2023-01-01T00:00:00Z",
      "channelId": "UC...",
      "title": "영상 제목",
      "description": "영상 설명",
      "thumbnails": { /* ... */ },
      "channelTitle": "채널 이름"
    }
  }]
}
```

**주의사항**:
- 검색은 **snippet만** 반환 (통계 없음)
- 통계 필요 시 `videos.list`로 추가 조회
- **높은 할당량 비용** (100 units)

**할당량**: 100 units per page (비싸다!)

---

## 6. 데이터 구조 상세

### 6.1 영상 duration 파싱

**ISO 8601 형식**: `PT#H#M#S` (Period of Time)

**예시**:
- `PT1H23M45S` → 1시간 23분 45초
- `PT15M30S` → 15분 30초
- `PT45S` → 45초
- `P1DT12H` → 1일 12시간 (드물게 사용)

**Python 파싱 코드** (DannyIbo에서 본 패턴):
```python
import re

def parse_duration(duration_str):
    """PT1H23M45S → 초 단위로 변환"""
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration_str)

    if not match:
        return 0

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds

# 예시
parse_duration("PT1H23M45S")  # 5025초
parse_duration("PT15M")        # 900초
parse_duration("PT45S")        # 45초
```

**Python isodate 라이브러리** (권장):
```python
import isodate

duration_seconds = isodate.parse_duration("PT1H23M45S").total_seconds()
# 5025.0
```

### 6.2 카테고리 ID 매핑

**주요 카테고리**:

| ID | 카테고리 | 설명 |
|----|---------|------|
| 1 | Film & Animation | 영화 및 애니메이션 |
| 2 | Autos & Vehicles | 자동차 |
| 10 | Music | 음악 |
| 15 | Pets & Animals | 반려동물 |
| 17 | Sports | 스포츠 |
| 19 | Travel & Events | 여행 및 이벤트 |
| 20 | Gaming | 게임 |
| 22 | People & Blogs | 사람 및 블로그 |
| 23 | Comedy | 코미디 |
| 24 | Entertainment | 엔터테인먼트 |
| 25 | News & Politics | 뉴스 및 정치 |
| 26 | Howto & Style | 노하우 및 스타일 |
| 27 | Education | 교육 |
| 28 | Science & Technology | 과학 및 기술 |

**전체 카테고리 조회**:
```python
response = youtube.videoCategories().list(
    part="snippet",
    regionCode="US"
).execute()
```

### 6.3 thumbnails 구조

**4가지 크기**:
```json
{
  "thumbnails": {
    "default": {
      "url": "https://i.ytimg.com/vi/VIDEO_ID/default.jpg",
      "width": 120,
      "height": 90
    },
    "medium": {
      "url": "https://i.ytimg.com/vi/VIDEO_ID/mqdefault.jpg",
      "width": 320,
      "height": 180
    },
    "high": {
      "url": "https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg",
      "width": 480,
      "height": 360
    },
    "standard": {  // 일부 영상만 제공
      "url": "https://i.ytimg.com/vi/VIDEO_ID/sddefault.jpg",
      "width": 640,
      "height": 480
    },
    "maxres": {  // 일부 영상만 제공
      "url": "https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg",
      "width": 1280,
      "height": 720
    }
  }
}
```

**직접 URL 생성** (API 호출 없이):
```python
def get_thumbnail_url(video_id, quality='high'):
    """
    quality: default, medium, high, standard, maxres
    """
    quality_map = {
        'default': 'default',
        'medium': 'mqdefault',
        'high': 'hqdefault',
        'standard': 'sddefault',
        'maxres': 'maxresdefault'
    }
    filename = quality_map.get(quality, 'hqdefault')
    return f"https://i.ytimg.com/vi/{video_id}/{filename}.jpg"
```

---

## 7. 최적화 전략

### 7.1 배치 처리

**원칙**: 여러 리소스를 한 번에 조회하여 할당량 절약

**예시 - 50개 영상 조회**:
```python
# ❌ 나쁜 방법 (50 units)
for video_id in video_ids:  # 50개
    response = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    ).execute()  # 1 unit × 50 = 50 units

# ✅ 좋은 방법 (1 unit)
response = youtube.videos().list(
    part="snippet,statistics",
    id=','.join(video_ids[:50])  # 최대 50개
).execute()  # 1 unit only!
```

**배치 처리 헬퍼 함수**:
```python
def batch_list(items, batch_size=50):
    """리스트를 batch_size씩 나누기"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

def get_videos_batch(youtube, video_ids):
    """비디오 정보 배치 조회"""
    all_videos = []

    for batch in batch_list(video_ids, 50):
        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=','.join(batch)
        ).execute()
        all_videos.extend(response['items'])

    return all_videos
```

### 7.2 부분 응답 (fields 파라미터)

**원칙**: 필요한 필드만 요청하여 대역폭 절약 (할당량 절약 아님)

**예시**:
```python
# 전체 응답
response = youtube.channels().list(
    part="snippet,statistics",
    id="UCqC_GY2ZiENFz2pwL0cSfAw"
).execute()

# 부분 응답 (제목과 구독자만)
response = youtube.channels().list(
    part="snippet,statistics",
    id="UCqC_GY2ZiENFz2pwL0cSfAw",
    fields="items(snippet/title,statistics/subscriberCount)"
).execute()
```

**응답 크기 비교**:
- 전체: ~2KB
- 부분: ~200B (10배 절약)

**fields 문법**:
```
items(snippet/title,snippet/description,statistics/*)
```
- `/`: 중첩 필드 접근
- `*`: 와일드카드 (모든 하위 필드)
- `,`: 여러 필드 선택

### 7.3 캐싱 전략

**ETag 활용**:
```python
import requests

etag_cache = {}

def get_channel_with_cache(youtube, channel_id):
    """ETag 기반 캐싱"""
    headers = {}
    if channel_id in etag_cache:
        headers['If-None-Match'] = etag_cache[channel_id]

    try:
        response = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id,
            headers=headers
        ).execute()

        # 새 ETag 저장
        etag_cache[channel_id] = response['etag']
        return response

    except HttpError as e:
        if e.resp.status == 304:  # Not Modified
            print("캐시 히트! 할당량 절약")
            return None  # 캐시된 데이터 사용
        raise
```

**타임 기반 캐싱**:
```python
import time
from functools import wraps

def cache_with_ttl(ttl_seconds=3600):
    """TTL 기반 캐싱 데코레이터"""
    cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(kwargs.items()))
            now = time.time()

            if key in cache:
                value, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    return value

            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result

        return wrapper
    return decorator

@cache_with_ttl(ttl_seconds=3600)  # 1시간 캐시
def get_channel_stats(youtube, channel_id):
    response = youtube.channels().list(
        part="statistics",
        id=channel_id
    ).execute()
    return response['items'][0]['statistics']
```

### 7.4 증분 업데이트

**원칙**: 전체 데이터가 아닌 변경분만 조회

**예시 - 신규 영상만 조회**:
```python
from datetime import datetime, timedelta

def get_new_videos_only(youtube, channel_id, last_check_time):
    """마지막 체크 이후 업로드된 영상만 조회"""

    # 1. 채널의 uploads 재생목록 ID 가져오기
    channel_response = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()
    uploads_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # 2. 신규 영상만 조회
    new_video_ids = []
    next_page_token = None

    while True:
        response = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in response['items']:
            published_at = datetime.fromisoformat(
                item['snippet']['publishedAt'].replace('Z', '+00:00')
            )

            # 마지막 체크 이전 영상이면 중단
            if published_at < last_check_time:
                return new_video_ids

            new_video_ids.append(item['snippet']['resourceId']['videoId'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return new_video_ids
```

### 7.5 압축 (gzip)

**원칙**: HTTP 압축으로 대역폭 절약

**Python 구현**:
```python
import httplib2

# google-api-python-client는 기본적으로 gzip 지원
# httplib2 사용 시 자동 처리됨

http = httplib2.Http()
http.follow_redirects = False  # 선택사항
# gzip은 자동으로 활성화됨
```

---

## 8. 에러 처리

### 8.1 주요 에러 코드

| 코드 | 이유 | 설명 | 해결 방법 |
|------|------|------|----------|
| 400 | badRequest | 잘못된 요청 | 파라미터 확인 |
| 401 | authError | 인증 실패 | API 키/OAuth 토큰 확인 |
| 403 | quotaExceeded | 할당량 초과 | 다음 날까지 대기 또는 확장 요청 |
| 403 | forbidden | 권한 없음 | OAuth 스코프 확인 |
| 404 | notFound | 리소스 없음 | ID 확인 (삭제되었을 수도) |
| 429 | rateLimitExceeded | 요청 속도 제한 | 재시도 (exponential backoff) |
| 500 | backendError | 서버 오류 | 재시도 |
| 503 | serviceUnavailable | 서비스 중단 | 재시도 |

### 8.2 에러 응답 구조

```json
{
  "error": {
    "code": 403,
    "message": "The request cannot be completed because you have exceeded your quota.",
    "errors": [{
      "domain": "youtube.quota",
      "reason": "quotaExceeded",
      "message": "The request cannot be completed because you have exceeded your quota."
    }]
  }
}
```

### 8.3 재시도 로직

**Exponential Backoff**:
```python
import time
from googleapiclient.errors import HttpError

def execute_with_retry(request, max_retries=5):
    """Exponential backoff으로 재시도"""
    for attempt in range(max_retries):
        try:
            return request.execute()

        except HttpError as e:
            error_reason = e.resp.get('reason', '')

            # 할당량 초과는 재시도 안 함
            if e.resp.status == 403 and 'quota' in error_reason.lower():
                raise

            # 재시도 가능한 에러
            if e.resp.status in [429, 500, 503]:
                wait_time = (2 ** attempt) + (random.random())  # 1, 2, 4, 8, 16초 + jitter
                print(f"재시도 대기: {wait_time:.2f}초 (시도 {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise

    raise Exception(f"{max_retries}회 재시도 실패")

# 사용
response = execute_with_retry(
    youtube.videos().list(part="snippet", id="dQw4w9WgXcQ")
)
```

### 8.4 포괄적 에러 처리

```python
from googleapiclient.errors import HttpError

def safe_api_call(api_func, **kwargs):
    """안전한 API 호출 래퍼"""
    try:
        response = api_func(**kwargs).execute()
        return {'success': True, 'data': response}

    except HttpError as e:
        error_code = e.resp.status
        error_content = e.content.decode('utf-8')

        # 할당량 초과
        if error_code == 403 and 'quotaExceeded' in error_content:
            return {
                'success': False,
                'error': 'QUOTA_EXCEEDED',
                'message': '일일 할당량 초과. 내일 다시 시도하세요.'
            }

        # 리소스 없음
        elif error_code == 404:
            return {
                'success': False,
                'error': 'NOT_FOUND',
                'message': '요청한 리소스를 찾을 수 없습니다.'
            }

        # 기타 에러
        else:
            return {
                'success': False,
                'error': 'API_ERROR',
                'message': str(e),
                'status_code': error_code
            }

    except Exception as e:
        return {
            'success': False,
            'error': 'UNKNOWN_ERROR',
            'message': str(e)
        }

# 사용
result = safe_api_call(
    youtube.channels().list,
    part="statistics",
    id="UCqC_GY2ZiENFz2pwL0cSfAw"
)

if result['success']:
    stats = result['data']['items'][0]['statistics']
else:
    print(f"에러: {result['error']} - {result['message']}")
```

---

## 9. 실전 사용 패턴

### 9.1 채널 기본 정보 수집

```python
def get_channel_info(youtube, channel_id):
    """채널 기본 정보 및 통계"""
    response = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        id=channel_id
    ).execute()

    if not response['items']:
        return None

    channel = response['items'][0]
    return {
        'id': channel['id'],
        'title': channel['snippet']['title'],
        'description': channel['snippet']['description'],
        'custom_url': channel['snippet'].get('customUrl'),
        'published_at': channel['snippet']['publishedAt'],
        'thumbnail': channel['snippet']['thumbnails']['high']['url'],
        'view_count': int(channel['statistics']['viewCount']),
        'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
        'video_count': int(channel['statistics']['videoCount']),
        'uploads_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads']
    }
```

### 9.2 채널의 모든 영상 수집

```python
def get_all_channel_videos(youtube, channel_id):
    """채널의 모든 영상 상세 정보"""

    # 1. 채널 정보에서 uploads 재생목록 ID 가져오기
    channel_response = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()
    uploads_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # 2. 모든 영상 ID 수집
    video_ids = []
    next_page_token = None

    while True:
        playlist_response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in playlist_response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    # 3. 영상 상세 정보 배치 조회 (50개씩)
    all_videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        videos_response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(batch)
        ).execute()
        all_videos.extend(videos_response['items'])

    return all_videos
```

**할당량 계산**:
- channels.list: 1 unit
- playlistItems.list: (영상 수 / 50) units (예: 500개 = 10 units)
- videos.list: (영상 수 / 50) units (예: 500개 = 10 units)
- **총**: 1 + 10 + 10 = **21 units** (500개 영상 채널)

### 9.3 영상 댓글 전체 수집

```python
def get_all_video_comments(youtube, video_id):
    """영상의 모든 댓글 + 대댓글 수집"""

    # 1. 댓글 스레드 수집 (top-level + 최대 5개 대댓글)
    all_comments = []
    threads_with_more_replies = []
    next_page_token = None

    while True:
        response = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token,
            textFormat="plainText"
        ).execute()

        for thread in response['items']:
            # Top-level 댓글
            top_comment = thread['snippet']['topLevelComment']
            all_comments.append(top_comment)

            # 대댓글
            total_replies = thread['snippet']['totalReplyCount']
            if 'replies' in thread:
                all_comments.extend(thread['replies']['comments'])

            # 5개 초과 대댓글 있으면 기록
            if total_replies > 5:
                threads_with_more_replies.append(thread['id'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    # 2. 5개 초과 대댓글 추가 수집
    for thread_id in threads_with_more_replies:
        next_page_token = None

        while True:
            replies_response = youtube.comments().list(
                part="snippet",
                parentId=thread_id,
                maxResults=100,
                pageToken=next_page_token
            ).execute()

            all_comments.extend(replies_response['items'])

            next_page_token = replies_response.get('nextPageToken')
            if not next_page_token:
                break

    return all_comments
```

**할당량 계산** (댓글 1000개, 대댓글 5개 초과 스레드 50개):
- commentThreads.list: 10 pages = 10 units
- comments.list: 50 threads × 1 = 50 units
- **총**: **60 units**

### 9.4 10개 채널 동시 모니터링

```python
def monitor_multiple_channels(youtube, channel_ids):
    """10개 채널 효율적 모니터링"""

    # 1. 모든 채널 정보 한 번에 조회 (1 unit)
    channels_response = youtube.channels().list(
        part="snippet,statistics",
        id=','.join(channel_ids[:50])  # 최대 50개
    ).execute()

    channels_data = {}
    for channel in channels_response['items']:
        channels_data[channel['id']] = {
            'title': channel['snippet']['title'],
            'subscribers': int(channel['statistics'].get('subscriberCount', 0)),
            'views': int(channel['statistics']['viewCount']),
            'video_count': int(channel['statistics']['videoCount'])
        }

    return channels_data

# 사용
channel_ids = ['UC1', 'UC2', ..., 'UC10']
data = monitor_multiple_channels(youtube, channel_ids)
# 할당량: 1 unit only!
```

---

## 10. 할당량 계산 예시

### 10.1 시나리오: 10개 채널 일일 모니터링

**요구사항**:
- 10개 채널 기본 정보 (구독자, 조회수)
- 각 채널 최근 50개 영상 통계
- 각 영상 댓글 수 (상세 댓글 수집 안 함)

**할당량 계산**:

| 작업 | API 호출 | 할당량 | 계산 |
|------|---------|--------|------|
| 채널 정보 조회 | channels.list (10개 배치) | 1 unit | 1 |
| uploads 재생목록 조회 | channels.list (contentDetails) | 1 unit | 1 |
| 최근 50개 영상 ID | playlistItems.list × 10채널 | 1 unit/채널 | 10 |
| 영상 상세 정보 | videos.list (50개 배치) × 10 | 1 unit/채널 | 10 |

**총 할당량**: 1 + 1 + 10 + 10 = **22 units/day**

**연간 가능**: 10,000 / 22 = **454일치 모니터링** (1일 1회)

### 10.2 시나리오: 신규 채널 전체 분석

**요구사항**:
- 채널 기본 정보
- 모든 영상 (500개) 상세 정보
- 모든 영상의 댓글 (평균 100개/영상)

**할당량 계산**:

| 작업 | API 호출 | 할당량 | 계산 |
|------|---------|--------|------|
| 채널 정보 | channels.list | 1 unit | 1 |
| 영상 ID 수집 | playlistItems.list (10 pages) | 1 unit/page | 10 |
| 영상 상세 정보 | videos.list (10 batches) | 1 unit/batch | 10 |
| 댓글 수집 | commentThreads.list (500영상 × 1page) | 1 unit/page | 500 |

**총 할당량**: 1 + 10 + 10 + 500 = **521 units**

**일일 한계**: 10,000 / 521 = **하루 19개 채널 분석 가능**

### 10.3 할당량 절약 팁

**❌ 비효율적 (3,000 units)**:
```python
for channel_id in channel_ids:  # 10개
    # 채널 정보 (1 unit × 10 = 10 units)
    channel_response = youtube.channels().list(...)

    # 영상 ID 수집 (1 unit × 10 × 10 pages = 100 units)
    for page in range(10):
        playlist_response = youtube.playlistItems().list(...)

    # 영상 상세 (1 unit × 10 × 500 videos = 5,000 units!)
    for video_id in video_ids:
        video_response = youtube.videos().list(id=video_id)
```

**✅ 효율적 (22 units)**:
```python
# 채널 정보 배치 조회 (1 unit)
channels_response = youtube.channels().list(
    part="snippet,statistics,contentDetails",
    id=','.join(channel_ids)
)

for channel in channels_response['items']:
    uploads_id = channel['contentDetails']['relatedPlaylists']['uploads']

    # 영상 ID 수집 (1 unit per channel = 10 units)
    video_ids = []
    next_page_token = None
    while next_page_token is not None:
        response = youtube.playlistItems().list(
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page_token
        )
        video_ids.extend(...)
        next_page_token = response.get('nextPageToken')

    # 영상 상세 배치 조회 (1 unit per 50 videos = 10 units for 500 videos)
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        response = youtube.videos().list(
            part="snippet,statistics",
            id=','.join(batch)
        )
```

**절약**: 5,110 units → 22 units (**232배 효율 향상**)

---

## 11. 요약 및 체크리스트

### 11.1 핵심 포인트

✅ **기본**:
- 하루 10,000 units 무료
- 읽기(1 unit) < 쓰기(50 units) < 검색(100 units) < 업로드(1,600 units)
- 배치 처리로 할당량 절약 (최대 50개)

✅ **채널 모니터링 필수 엔드포인트**:
1. `channels.list` - 채널 정보
2. `playlistItems.list` - 영상 ID 목록
3. `videos.list` - 영상 상세
4. `commentThreads.list` - 댓글 수집

✅ **최적화**:
- 배치 처리 (50개씩)
- 캐싱 (ETag, TTL)
- 증분 업데이트 (신규 데이터만)
- 부분 응답 (fields 파라미터)

✅ **에러 처리**:
- 403 quotaExceeded → 다음 날 대기
- 429 rateLimitExceeded → Exponential backoff
- 404 notFound → 리소스 삭제 처리

### 11.2 프로젝트 적용 체크리스트

**설정 단계**:
- [ ] Google Cloud 프로젝트 생성
- [ ] YouTube Data API v3 활성화
- [ ] API 키 발급 및 제한 설정
- [ ] 환경 변수 설정

**개발 단계**:
- [ ] google-api-python-client 설치
- [ ] 인증 모듈 구현
- [ ] 배치 처리 유틸리티 함수
- [ ] 에러 처리 및 재시도 로직
- [ ] 할당량 모니터링 로직

**최적화 단계**:
- [ ] 캐싱 구현
- [ ] 증분 업데이트 로직
- [ ] 할당량 계산기
- [ ] 로깅 및 모니터링

---

**다음 문서**: `google-api-python-client-guide.md` - Python 라이브러리 실전 사용법
