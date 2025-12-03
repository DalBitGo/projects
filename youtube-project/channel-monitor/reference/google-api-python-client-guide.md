# google-api-python-client 완전 가이드

**작성일**: 2025-10-20
**목적**: YouTube Data API v3 사용을 위한 Python 클라이언트 라이브러리 심층 분석
**공식 문서**: https://googleapis.github.io/google-api-python-client/

---

## 목차
1. [라이브러리 개요](#1-라이브러리-개요)
2. [설치 및 설정](#2-설치-및-설정)
3. [핵심 개념](#3-핵심-개념)
4. [build() 함수 심층 분석](#4-build-함수-심층-분석)
5. [Service 객체 사용법](#5-service-객체-사용법)
6. [HttpRequest와 실행](#6-httprequest와-실행)
7. [에러 처리](#7-에러-처리)
8. [고급 기능](#8-고급-기능)
9. [실전 패턴](#9-실전-패턴)
10. [DannyIbo 코드 패턴 분석](#10-dannyibo-코드-패턴-분석)

---

## 1. 라이브러리 개요

### 1.1 google-api-python-client란?

**공식 이름**: Google API Client Library for Python

**정의**: Google의 Discovery 기반 API를 Python에서 사용하기 위한 공식 클라이언트 라이브러리

**특징**:
- ✅ 모든 Google API를 하나의 라이브러리로 지원
- ✅ Discovery Document 기반 동적 API 호출
- ✅ Python 3.7 이상 지원
- ✅ 자동완성, 타입 힌트 제한적 지원
- ⚠️ 단일 패키지로 50MB 이상 크기

**버전 정보**:
- **v1.x**: 레거시 (deprecated)
- **v2.x**: 현재 권장 버전 (2.0+)
  - Discovery document 캐싱으로 신뢰성 향상
  - 정적 discovery 기본 활성화

**대안 (Google 권장)**:
- Cloud Client Libraries for Python
  - API별 전용 라이브러리
  - 더 작은 패키지 크기
  - 더 나은 타입 힌트
  - **단점**: YouTube Data API는 제공 안 함

**결론**: YouTube Data API 사용 시 google-api-python-client가 유일한 공식 선택지

---

## 2. 설치 및 설정

### 2.1 설치

**pip 설치**:
```bash
pip install google-api-python-client
```

**특정 버전 설치**:
```bash
pip install google-api-python-client==2.100.0
```

**의존성 함께 설치**:
```bash
# OAuth 사용 시
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# 전체 (권장)
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv
```

### 2.2 import 구조

**기본 import**:
```python
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
```

**OAuth 사용 시**:
```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
```

**주의**: `import googleapiclient` (X), `from googleapiclient` (O)

---

## 3. 핵심 개념

### 3.1 Discovery Document

**정의**: API의 메타데이터를 JSON 형식으로 정의한 문서

**포함 내용**:
- API 이름, 버전
- 리소스 타입 (channels, videos 등)
- 메서드 (list, insert, update, delete)
- 파라미터 (part, id, maxResults 등)
- 응답 스키마

**예시** (YouTube Data API v3):
```json
{
  "name": "youtube",
  "version": "v3",
  "baseUrl": "https://www.googleapis.com/youtube/v3/",
  "resources": {
    "channels": {
      "methods": {
        "list": {
          "httpMethod": "GET",
          "path": "channels",
          "parameters": {
            "part": { "type": "string", "required": true },
            "id": { "type": "string" }
          }
        }
      }
    }
  }
}
```

**v2.x 개선사항**:
- Discovery document를 라이브러리에 **정적으로 포함**
- 네트워크 없이 빠른 초기화
- 안정성 향상 (Google API 장애 시에도 작동)

### 3.2 Service 객체

**정의**: API와 상호작용하는 Python 객체

**생성**:
```python
service = build('youtube', 'v3', developerKey=API_KEY)
```

**구조**:
```
service
 ├─ channels()      → ChannelsResource
 ├─ videos()        → VideosResource
 ├─ playlists()     → PlaylistsResource
 └─ ...
```

**각 Resource는 메서드 제공**:
```
service.channels()
 ├─ list()          → HttpRequest
 ├─ update()        → HttpRequest
 └─ ...
```

### 3.3 HttpRequest 객체

**정의**: 실제 API 호출을 나타내는 객체

**특징**:
- `.execute()`로 실행
- 실행 전까지 네트워크 요청 없음 (Lazy)
- 재사용 가능 (같은 요청 반복 가능)

**예시**:
```python
request = service.channels().list(part="snippet", id="UC...")
# 아직 API 호출 안 됨

response = request.execute()  # 여기서 API 호출
# 응답은 Python dict
```

---

## 4. build() 함수 심층 분석

### 4.1 함수 시그니처

```python
from googleapiclient.discovery import build

service = build(
    serviceName,           # str: API 이름 (예: 'youtube')
    version,               # str: API 버전 (예: 'v3')
    http=None,             # httplib2.Http: HTTP 클라이언트 (선택)
    discoveryServiceUrl=None,  # str: Discovery 서비스 URL (선택)
    developerKey=None,     # str: API 키 (선택)
    model=None,            # Model: 응답 모델 (선택)
    requestBuilder=None,   # RequestBuilder: 요청 빌더 (선택)
    credentials=None,      # Credentials: OAuth 크레덴셜 (선택)
    cache_discovery=True,  # bool: Discovery 캐싱 여부 (deprecated in v2)
    cache=None,            # Cache: 캐시 객체 (선택)
    client_options=None,   # ClientOptions: 클라이언트 옵션 (선택)
    adc_cert_path=None,    # str: ADC 인증서 경로 (선택)
    adc_key_path=None,     # str: ADC 키 경로 (선택)
    num_retries=1,         # int: 재시도 횟수 (기본 1)
    static_discovery=True  # bool: 정적 discovery 사용 (v2 기본값)
)
```

### 4.2 필수 파라미터

**serviceName** (str):
```python
# YouTube Data API
service = build('youtube', 'v3', ...)

# Google Drive API
service = build('drive', 'v3', ...)

# Gmail API
service = build('gmail', 'v1', ...)
```

**version** (str):
```python
# 버전 명시 필수
service = build('youtube', 'v3', ...)  # 정확한 버전 지정
```

### 4.3 인증 파라미터

**방법 1: API 키 (공개 데이터)**:
```python
API_KEY = "AIzaSy..."
service = build('youtube', 'v3', developerKey=API_KEY)
```

**방법 2: OAuth 2.0 (사용자 데이터)**:
```python
from google.oauth2.credentials import Credentials

creds = Credentials(token='access_token', ...)
service = build('youtube', 'v3', credentials=creds)
```

**방법 3: Service Account (서버 간 인증)**:
```python
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    'service-account-key.json',
    scopes=['https://www.googleapis.com/auth/youtube.readonly']
)
service = build('youtube', 'v3', credentials=credentials)
```

### 4.4 중요 옵션 파라미터

**static_discovery** (bool, 기본 True):
```python
# v2.x 권장 (빠르고 안정적)
service = build('youtube', 'v3', developerKey=API_KEY, static_discovery=True)

# 동적 discovery (비권장)
service = build('youtube', 'v3', developerKey=API_KEY, static_discovery=False)
```

**num_retries** (int, 기본 1):
```python
# 네트워크 오류 시 자동 재시도
service = build('youtube', 'v3', developerKey=API_KEY, num_retries=3)
```

### 4.5 Context Manager 사용

**권장 패턴**:
```python
# 자동으로 close() 호출
with build('youtube', 'v3', developerKey=API_KEY) as service:
    response = service.channels().list(part="snippet", id="UC...").execute()
# 여기서 자동으로 소켓 닫힘
```

**수동 관리**:
```python
service = build('youtube', 'v3', developerKey=API_KEY)
try:
    response = service.channels().list(...).execute()
finally:
    service.close()  # 명시적으로 소켓 닫기
```

**주의**: DannyIbo 코드는 close() 호출 안 함 → 소켓 누수 가능성

---

## 5. Service 객체 사용법

### 5.1 리소스 접근

**패턴**: `service.{resource_name}()`

```python
# YouTube Data API v3 리소스
channels = service.channels()      # ChannelsResource
videos = service.videos()          # VideosResource
playlists = service.playlists()    # PlaylistsResource
playlistItems = service.playlistItems()
commentThreads = service.commentThreads()
comments = service.comments()
search = service.search()
subscriptions = service.subscriptions()
activities = service.activities()
```

**타입**:
```python
from googleapiclient.discovery import Resource

channels = service.channels()
print(type(channels))  # <class 'googleapiclient.discovery.Resource'>
```

### 5.2 메서드 호출

**패턴**: `resource.{method_name}(**params)`

```python
# channels 리소스의 list 메서드
request = service.channels().list(
    part="snippet,statistics",
    id="UCqC_GY2ZiENFz2pwL0cSfAw"
)

# videos 리소스의 list 메서드
request = service.videos().list(
    part="snippet,contentDetails,statistics",
    id="dQw4w9WgXcQ"
)
```

### 5.3 메서드 종류

**CRUD 매핑**:

| HTTP Method | API Method | 용도 |
|-------------|-----------|------|
| GET | list() | 리소스 조회 |
| POST | insert() | 리소스 생성 |
| PUT | update() | 리소스 수정 |
| DELETE | delete() | 리소스 삭제 |

**추가 메서드**:
- `rate()` - 좋아요/싫어요
- `getRating()` - 평가 조회
- `reportAbuse()` - 신고

### 5.4 파라미터 전달

**키워드 인자**:
```python
request = service.channels().list(
    part="snippet,statistics",
    id="UC...",
    maxResults=50
)
```

**딕셔너리 언패킹**:
```python
params = {
    'part': 'snippet,statistics',
    'id': 'UC...',
    'maxResults': 50
}
request = service.channels().list(**params)
```

**선택 파라미터 처리**:
```python
def get_channels(channel_ids, parts=['snippet', 'statistics'], max_results=None):
    params = {
        'part': ','.join(parts),
        'id': ','.join(channel_ids)
    }

    if max_results:
        params['maxResults'] = max_results

    return service.channels().list(**params).execute()
```

---

## 6. HttpRequest와 실행

### 6.1 HttpRequest 객체

**생성**:
```python
from googleapiclient.http import HttpRequest

request = service.channels().list(part="snippet", id="UC...")
print(type(request))  # <class 'googleapiclient.http.HttpRequest'>
```

**속성**:
```python
print(request.uri)           # 실제 HTTP URI
print(request.method)        # HTTP 메서드 (GET, POST 등)
print(request.headers)       # HTTP 헤더
print(request.body)          # 요청 본문 (POST/PUT 시)
print(request.resumable)     # 재개 가능 업로드 여부
```

### 6.2 execute() 메서드

**기본 실행**:
```python
response = request.execute()
```

**파라미터**:
```python
response = request.execute(
    http=None,          # httplib2.Http 객체 (선택)
    num_retries=0       # 재시도 횟수 (기본 0, build()에서 설정한 값 무시)
)
```

**반환값**:
- Python dict (JSON 응답 자동 파싱)
- 빈 응답 시 None

**예시**:
```python
response = service.channels().list(
    part="snippet,statistics",
    id="UCqC_GY2ZiENFz2pwL0cSfAw"
).execute()

# response는 dict
print(type(response))  # <class 'dict'>
print(response.keys())  # dict_keys(['kind', 'etag', 'pageInfo', 'items'])
```

### 6.3 execute() vs execute_async()

**동기 실행** (execute):
```python
# 블로킹 - 응답 올 때까지 대기
response = request.execute()
print(response)
```

**비동기 실행** (execute_async, 실험적):
```python
# 비블로킹 - Future 객체 반환
future = request.execute_async()
response = future.result()  # 결과 대기
```

**주의**: execute_async는 실험적 기능, 권장 안 함

### 6.4 재사용

**HttpRequest는 재사용 가능**:
```python
request = service.channels().list(part="snippet", id="UC...")

# 여러 번 실행 가능
response1 = request.execute()
time.sleep(60)
response2 = request.execute()  # 같은 요청 다시 실행
```

**활용 - 폴링**:
```python
def poll_until_condition(request, check_func, interval=60, max_attempts=10):
    """조건 만족할 때까지 폴링"""
    for attempt in range(max_attempts):
        response = request.execute()
        if check_func(response):
            return response
        time.sleep(interval)
    return None
```

---

## 7. 에러 처리

### 7.1 HttpError 예외

**import**:
```python
from googleapiclient.errors import HttpError
```

**구조**:
```python
try:
    response = service.channels().list(...).execute()
except HttpError as e:
    print(f"에러 코드: {e.resp.status}")
    print(f"에러 사유: {e.resp.reason}")
    print(f"에러 내용: {e.content}")
    print(f"에러 URI: {e.uri}")
```

**응답 구조**:
```python
e.resp = {
    'status': 403,  # HTTP 상태 코드
    'reason': 'Forbidden',  # 상태 메시지
    'content-type': 'application/json; charset=UTF-8',
    ...
}

e.content = b'{"error": {"code": 403, "message": "...", ...}}'
```

### 7.2 에러 파싱

**JSON 파싱**:
```python
import json

try:
    response = service.channels().list(...).execute()
except HttpError as e:
    error_details = json.loads(e.content.decode('utf-8'))
    error_code = error_details['error']['code']
    error_message = error_details['error']['message']
    error_reason = error_details['error']['errors'][0]['reason']

    print(f"에러 코드: {error_code}")
    print(f"에러 메시지: {error_message}")
    print(f"에러 사유: {error_reason}")
```

### 7.3 실전 에러 처리 패턴

**DannyIbo 스타일 개선**:
```python
def safe_api_call(request, logger=None):
    """안전한 API 호출 래퍼"""
    try:
        return {'success': True, 'data': request.execute()}

    except HttpError as e:
        error_data = json.loads(e.content.decode('utf-8'))['error']
        error_code = error_data['code']
        error_reason = error_data.get('errors', [{}])[0].get('reason', 'unknown')

        if logger:
            logger.error(f"API 에러: {error_code} - {error_reason}")

        # 할당량 초과
        if error_code == 403 and error_reason == 'quotaExceeded':
            return {
                'success': False,
                'error': 'QUOTA_EXCEEDED',
                'message': '일일 할당량 초과',
                'retry_after': 'tomorrow'
            }

        # 리소스 없음
        elif error_code == 404:
            return {
                'success': False,
                'error': 'NOT_FOUND',
                'message': '리소스를 찾을 수 없습니다'
            }

        # 속도 제한
        elif error_code == 429:
            return {
                'success': False,
                'error': 'RATE_LIMIT',
                'message': '요청 속도 제한',
                'retry_after': '60 seconds'
            }

        # 기타
        else:
            return {
                'success': False,
                'error': 'API_ERROR',
                'message': error_data.get('message', str(e)),
                'code': error_code
            }

    except Exception as e:
        if logger:
            logger.exception("예상치 못한 에러")
        return {
            'success': False,
            'error': 'UNKNOWN_ERROR',
            'message': str(e)
        }

# 사용
result = safe_api_call(
    service.channels().list(part="snippet", id="UC..."),
    logger=my_logger
)

if result['success']:
    channel_data = result['data']['items'][0]
else:
    print(f"에러: {result['error']} - {result['message']}")
```

---

## 8. 고급 기능

### 8.1 Media Upload

**큰 파일 업로드** (YouTube 영상):
```python
from googleapiclient.http import MediaFileUpload

# 재개 가능 업로드
media = MediaFileUpload(
    'video.mp4',
    mimetype='video/*',
    resumable=True,
    chunksize=1024*1024  # 1MB 청크
)

request = service.videos().insert(
    part="snippet,status",
    body={
        'snippet': {
            'title': '영상 제목',
            'description': '영상 설명',
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'private'
        }
    },
    media_body=media
)

# 진행률 표시
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"업로드: {int(status.progress() * 100)}%")

print("업로드 완료!")
print(f"영상 ID: {response['id']}")
```

### 8.2 Batch Requests

**여러 요청 묶어서 보내기** (실험적):
```python
from googleapiclient.http import BatchHttpRequest

def callback(request_id, response, exception):
    if exception:
        print(f"요청 {request_id} 실패: {exception}")
    else:
        print(f"요청 {request_id} 성공: {response}")

batch = service.new_batch_http_request(callback=callback)

batch.add(service.channels().list(part="snippet", id="UC1"))
batch.add(service.channels().list(part="snippet", id="UC2"))
batch.add(service.channels().list(part="snippet", id="UC3"))

batch.execute()  # 한 번의 HTTP 요청으로 3개 처리
```

**주의**:
- YouTube Data API는 배치 요청 지원 안 함
- Drive, Gmail 등 일부 API만 지원

### 8.3 Pagination Helper

**자동 페이지네이션**:
```python
def paginate(request):
    """모든 페이지 자동 수집"""
    while request is not None:
        response = request.execute()
        yield response

        # 다음 페이지 요청 생성
        request = service.channels().list_next(request, response)

# 사용
request = service.playlistItems().list(
    part="snippet",
    playlistId="UU...",
    maxResults=50
)

all_items = []
for response in paginate(request):
    all_items.extend(response['items'])
```

**주의**: `list_next()` 메서드는 일부 리소스만 지원

---

## 9. 실전 패턴

### 9.1 Service 객체 싱글톤

**문제**: build()를 매번 호출하면 비효율

**해결**:
```python
class YouTubeService:
    _instance = None
    _service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._service is None:
            import os
            API_KEY = os.getenv('YOUTUBE_API_KEY')
            self._service = build('youtube', 'v3', developerKey=API_KEY)

    @property
    def service(self):
        return self._service

    def close(self):
        if self._service:
            self._service.close()
            self._service = None

# 사용
yt = YouTubeService()
response = yt.service.channels().list(...).execute()
```

### 9.2 Fluent Interface 래퍼

**목표**: 더 읽기 쉬운 API

```python
class YouTubeAPI:
    def __init__(self, api_key):
        self.service = build('youtube', 'v3', developerKey=api_key)

    def get_channel(self, channel_id, parts=None):
        """채널 정보 조회"""
        parts = parts or ['snippet', 'statistics']
        response = self.service.channels().list(
            part=','.join(parts),
            id=channel_id
        ).execute()

        if not response['items']:
            return None

        return response['items'][0]

    def get_channel_videos(self, channel_id, max_results=None):
        """채널 영상 목록"""
        # 1. uploads 재생목록 ID
        channel = self.get_channel(channel_id, parts=['contentDetails'])
        uploads_id = channel['contentDetails']['relatedPlaylists']['uploads']

        # 2. 영상 ID 수집
        video_ids = []
        next_page_token = None

        while True:
            response = self.service.playlistItems().list(
                part="contentDetails",
                playlistId=uploads_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for item in response['items']:
                video_ids.append(item['contentDetails']['videoId'])

            next_page_token = response.get('nextPageToken')
            if not next_page_token or (max_results and len(video_ids) >= max_results):
                break

        if max_results:
            video_ids = video_ids[:max_results]

        # 3. 영상 상세 정보 배치 조회
        return self._get_videos_by_ids(video_ids)

    def _get_videos_by_ids(self, video_ids):
        """영상 ID 목록으로 상세 정보 조회"""
        all_videos = []

        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            response = self.service.videos().list(
                part="snippet,contentDetails,statistics",
                id=','.join(batch)
            ).execute()
            all_videos.extend(response['items'])

        return all_videos

# 사용
api = YouTubeAPI(api_key=os.getenv('YOUTUBE_API_KEY'))

channel = api.get_channel('UCqC_GY2ZiENFz2pwL0cSfAw')
print(f"채널: {channel['snippet']['title']}")
print(f"구독자: {channel['statistics']['subscriberCount']}")

videos = api.get_channel_videos('UCqC_GY2ZiENFz2pwL0cSfAw', max_results=100)
print(f"영상 개수: {len(videos)}")
```

### 9.3 비동기 래퍼 (asyncio)

**문제**: google-api-python-client는 동기 라이브러리

**해결**: asyncio와 함께 사용
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncYouTubeAPI:
    def __init__(self, api_key, max_workers=10):
        self.service = build('youtube', 'v3', developerKey=api_key)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def get_channel(self, channel_id):
        """비동기 채널 정보 조회"""
        loop = asyncio.get_event_loop()
        request = self.service.channels().list(
            part="snippet,statistics",
            id=channel_id
        )

        # 블로킹 execute()를 스레드 풀에서 실행
        response = await loop.run_in_executor(
            self.executor,
            request.execute
        )

        return response['items'][0] if response['items'] else None

    async def get_multiple_channels(self, channel_ids):
        """여러 채널 동시 조회"""
        tasks = [self.get_channel(cid) for cid in channel_ids]
        return await asyncio.gather(*tasks)

# 사용
async def main():
    api = AsyncYouTubeAPI(api_key=os.getenv('YOUTUBE_API_KEY'))

    channel_ids = ['UC1', 'UC2', 'UC3', ..., 'UC10']

    # 10개 채널 동시 조회
    channels = await api.get_multiple_channels(channel_ids)

    for channel in channels:
        if channel:
            print(f"{channel['snippet']['title']}: {channel['statistics']['subscriberCount']}")

asyncio.run(main())
```

**주의**:
- YouTube API 할당량은 여전히 소모됨
- 속도 제한 (rate limit) 주의

---

## 10. DannyIbo 코드 패턴 분석

### 10.1 youtubeAPIkey 함수

**DannyIbo 코드**:
```python
# youtube_data_module.py:39-47
def youtubeAPIkey(DEVELOPER_KEY, OAUTHLIB_INSECURE_TRANSPORT="1", api_service_name="youtube", api_version="v3"):
    '''Get YouTube Data API credentials via API Key'''
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = OAUTHLIB_INSECURE_TRANSPORT
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY
    )
    return youtube
```

**분석**:
- ✅ 기본 파라미터로 유연성 제공
- ⚠️ `OAUTHLIB_INSECURE_TRANSPORT="1"`: OAuth 미사용인데 설정 (불필요)
- ⚠️ `googleapiclient.discovery.build` 대신 `build` 직접 import 권장
- ⚠️ Service 객체를 close() 안 함

**개선안**:
```python
from googleapiclient.discovery import build

def create_youtube_service(api_key=None, credentials=None):
    """YouTube service 객체 생성"""
    if api_key:
        return build('youtube', 'v3', developerKey=api_key, static_discovery=True)
    elif credentials:
        return build('youtube', 'v3', credentials=credentials, static_discovery=True)
    else:
        raise ValueError("api_key 또는 credentials 필요")

# Context manager 버전
from contextlib import contextmanager

@contextmanager
def youtube_service(api_key):
    """Context manager로 자동 close"""
    service = build('youtube', 'v3', developerKey=api_key)
    try:
        yield service
    finally:
        service.close()

# 사용
with youtube_service(API_KEY) as service:
    response = service.channels().list(...).execute()
# 자동으로 close() 호출됨
```

### 10.2 DannyIbo의 API 호출 패턴

**패턴 1: 직접 execute()**:
```python
# app.py:27-28
youtube = ydt.youtubeAPIkey(API_KEY)
query_result = ydt.youtubeSearchListStatistics(youtube, q=query)
```

**패턴 2: 래퍼 함수**:
```python
# youtube_data_module.py:49-62
def youtubeSearchList(youtube, channel_id=None, q=None, maxResults=50, type=None):
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=maxResults,
        q=q,
        fields='items(id,snippet),nextPageToken',
        type=type
    )
    responseSearchList = request.execute()
    return responseSearchList
```

**장점**:
- 재사용 가능한 래퍼 함수
- 기본값 제공

**단점**:
- 에러 처리 없음
- 할당량 추적 없음
- Service 객체 재생성 (비효율)

**개선안**:
```python
class YouTubeAPIWrapper:
    def __init__(self, api_key):
        self.service = build('youtube', 'v3', developerKey=api_key)
        self.quota_used = 0
        self.logger = logging.getLogger(__name__)

    def search(self, q=None, channel_id=None, max_results=50, video_type=None):
        """검색 (할당량 100 units)"""
        try:
            response = self.service.search().list(
                part="snippet",
                q=q,
                channelId=channel_id,
                maxResults=max_results,
                type=video_type,
                fields='items(id,snippet),nextPageToken'
            ).execute()

            self.quota_used += 100
            self.logger.info(f"할당량 사용: +100 (총 {self.quota_used})")
            return response

        except HttpError as e:
            self.logger.error(f"검색 에러: {e}")
            raise

    def get_quota_usage(self):
        """사용한 할당량"""
        return self.quota_used

# 사용
api = YouTubeAPIWrapper(API_KEY)
results = api.search(q="python tutorial", max_results=10)
print(f"할당량 사용: {api.get_quota_usage()} / 10000")
```

### 10.3 페이지네이션 패턴

**DannyIbo 코드**:
```python
# youtube_data_module.py:100-112
playlistNextPageToken = ''

while playlistNextPageToken != None:
    requestPlaylistItems = youtube.playlistItems().list(
        part="snippet",
        maxResults=50,
        pageToken=playlistNextPageToken,
        playlistId=channelUploadPlaylistID
    )
    responsePlaylistItems = requestPlaylistItems.execute()

    for video in responsePlaylistItems['items']:
        videoIdList.append(video['snippet']['resourceId']['videoId'])

    playlistNextPageToken = responsePlaylistItems.get('nextPageToken')
```

**분석**:
- ✅ nextPageToken 올바르게 사용
- ✅ maxResults=50으로 최대 효율
- ⚠️ 초기값 '' 대신 None 권장

**개선안**:
```python
def get_all_playlist_items(service, playlist_id):
    """재생목록의 모든 항목 수집"""
    items = []
    next_page_token = None
    page_count = 0

    while True:
        response = service.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        items.extend(response['items'])
        page_count += 1

        logger.info(f"페이지 {page_count}: {len(response['items'])}개 항목 수집")

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    logger.info(f"총 {len(items)}개 항목 수집 완료 (할당량: {page_count} units)")
    return items
```

---

## 11. 요약 및 베스트 프랙티스

### 11.1 핵심 포인트

✅ **라이브러리 사용**:
- `build()`로 service 객체 생성
- Context manager 또는 명시적 close()
- static_discovery=True (v2.x 기본값)

✅ **API 호출**:
- `service.{resource}().{method}(**params)`
- `.execute()`로 실행
- HttpError 예외 처리 필수

✅ **효율성**:
- Service 객체 재사용 (싱글톤 패턴)
- 배치 처리 (최대 50개)
- 페이지네이션 올바르게 구현

### 11.2 체크리스트

**설정**:
- [ ] google-api-python-client 설치 (v2.x)
- [ ] API 키 환경 변수 설정
- [ ] import 경로 확인 (`from googleapiclient.discovery import build`)

**개발**:
- [ ] Service 객체 재사용 (build() 반복 호출 X)
- [ ] Context manager 사용 또는 close() 호출
- [ ] HttpError 예외 처리
- [ ] 할당량 추적 로직

**최적화**:
- [ ] 배치 처리 (50개씩)
- [ ] 페이지네이션 최대 효율 (maxResults=50/100)
- [ ] 불필요한 part 요청하지 않기
- [ ] 캐싱 구현

---

**다음 단계**: 실제 프로젝트에 적용하여 10개 채널 모니터링 시스템 구축
