# 기술 스택 상세 문서

## 개요

전체 스택은 **Python 기반 백엔드 + FFmpeg 미디어 처리 + 선택적 웹 UI**로 구성

---

## 코어 기술

### Python 3.10+

**선택 이유**:
- 미디어 처리 라이브러리 풍부 (MoviePy, Pillow, pydub)
- FFmpeg 래퍼 지원 우수
- 데이터 처리 (Pandas) 및 API 통합 용이
- 비동기 작업 (Celery) 생태계 성숙

**주요 패키지**:
```python
# requirements.txt
pillow==10.2.0          # 이미지 처리
moviepy==1.0.3          # 영상 편집
pandas==2.1.4           # 데이터 처리
pydub==0.25.1           # 오디오 처리
opencv-python==4.9.0    # 고급 영상 처리
numpy==1.26.3           # 수치 연산

# API & Web
fastapi==0.109.0        # REST API
uvicorn==0.27.0         # ASGI 서버
celery==5.3.4           # 비동기 작업
redis==5.0.1            # 캐시 & 큐
pydantic==2.5.3         # 데이터 검증

# External APIs
requests==2.31.0        # HTTP 클라이언트
google-api-python-client==2.115.0  # YouTube API
openai==1.10.0          # LLM (optional)

# Utils
python-dotenv==1.0.0    # 환경변수
pyyaml==6.0.1           # 설정 파일
tqdm==4.66.1            # 진행률 표시
click==8.1.7            # CLI 도구
```

---

### FFmpeg

**버전**: 6.0+

**선택 이유**:
- 업계 표준 미디어 처리 도구
- 복잡한 필터 체인 지원
- 하드웨어 가속 (NVENC, QSV, VideoToolbox)
- 무료 & 오픈소스

**설치**:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg

# 버전 확인
ffmpeg -version
```

**주요 기능 활용**:
```bash
# 리사이즈 & 크롭
-vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"

# 블러 처리
-vf "gblur=sigma=50"

# 오버레이
-filter_complex "[0:v][1:v]overlay=x:y"

# 텍스트 번인
-vf "drawtext=fontfile=font.ttf:text='Hello':x=10:y=10:fontsize=24"

# 전환 효과 (xfade)
-filter_complex "xfade=transition=fade:duration=1:offset=5"

# 하드웨어 가속 (NVIDIA)
-hwaccel cuda -c:v h264_cuvid ... -c:v h264_nvenc

# 오디오 믹싱
-filter_complex "[0:a][1:a]amix=inputs=2:duration=longest"
```

---

## 미디어 처리 라이브러리

### Pillow (PIL Fork)

**용도**: 템플릿 이미지 생성, 오버레이, 썸네일

**주요 기능**:
```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 이미지 생성
img = Image.new('RGBA', (1080, 1920), (255, 255, 255, 0))

# 텍스트 렌더링
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("font.ttf", 72)
draw.text((540, 960), "제목", font=font, fill=(255, 255, 255), anchor="mm")

# 둥근 모서리
def add_rounded_corners(img, radius):
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius, fill=255)
    img.putalpha(mask)
    return img

# 그라데이션 생성
def create_gradient(start_color, end_color, width, height):
    base = Image.new('RGB', (width, height), start_color)
    top = Image.new('RGB', (width, height), end_color)
    mask = Image.new('L', (width, height))
    for y in range(height):
        mask.putpixel((0, y), int(255 * (y / height)))
    base.paste(top, (0, 0), mask)
    return base

# 블러
img = img.filter(ImageFilter.GaussianBlur(radius=20))

# 저장
img.save('output.png', 'PNG')
```

**한글 폰트**:
```python
# Noto Sans CJK 다운로드
# https://fonts.google.com/noto/specimen/Noto+Sans+KR

font_bold = ImageFont.truetype("NotoSansKR-Bold.ttf", 70)
font_regular = ImageFont.truetype("NotoSansKR-Regular.ttf", 50)
```

**이모지 지원**:
```python
# Noto Color Emoji 필요
# https://fonts.google.com/noto/specimen/Noto+Color+Emoji

emoji_font = ImageFont.truetype("NotoColorEmoji.ttf", 100)
draw.text((100, 100), "😹", font=emoji_font, embedded_color=True)
```

---

### MoviePy

**용도**: 고수준 영상 편집 (Python API)

**장점**:
- Python 네이티브 API (FFmpeg 래퍼)
- 직관적인 클립 조작
- 전환 효과 내장

**단점**:
- FFmpeg 직접 사용보다 느림
- 메모리 사용 많음

**주요 기능**:
```python
from moviepy.editor import *

# 클립 로드
clip = VideoFileClip("input.mp4")

# 자르기
clip = clip.subclip(5, 15)  # 5초~15초

# 리사이즈
clip = clip.resize(height=1920)

# 크롭
clip = clip.crop(x1=100, y1=200, x2=1180, y2=2120)

# 속도 조절
clip = clip.speedx(1.5)  # 1.5배속

# 텍스트
txt = TextClip("제목", fontsize=70, color='white', font='NotoSansKR-Bold')
txt = txt.set_position(('center', 'bottom')).set_duration(clip.duration)

# 합성
video = CompositeVideoClip([clip, txt])

# 연결
final = concatenate_videoclips([clip1, clip2, clip3], method="compose")

# 전환 효과
final = concatenate_videoclips([clip1, clip2], method="compose", padding=-1)  # crossfade

# 오디오
audio = AudioFileClip("bgm.mp3")
video = video.set_audio(audio)

# 렌더링
video.write_videofile(
    "output.mp4",
    fps=30,
    codec='libx264',
    audio_codec='aac',
    preset='medium',  # ultrafast, fast, medium, slow
    threads=4
)
```

**사용 전략**:
- 간단한 작업: MoviePy (빠른 프로토타이핑)
- 복잡한 작업: FFmpeg 직접 사용 (성능)

---

### pydub

**용도**: 오디오 편집

**주요 기능**:
```python
from pydub import AudioSegment
from pydub.effects import normalize

# 로드
audio = AudioSegment.from_file("audio.mp3")

# 자르기
clip = audio[5000:15000]  # 5초~15초 (ms 단위)

# 볼륨 조절
quiet = audio - 10  # -10dB
loud = audio + 5    # +5dB

# 페이드
audio = audio.fade_in(2000).fade_out(2000)

# 믹싱
mixed = audio1.overlay(audio2)

# Normalize
audio = normalize(audio)

# Export
audio.export("output.mp3", format="mp3", bitrate="192k")
```

**Ducking (음성 나올 때 BGM 줄이기)**:
```python
def duck_bgm(voice: AudioSegment, bgm: AudioSegment, duck_amount: int = 15):
    """
    voice: 음성 트랙
    bgm: 배경음악
    duck_amount: BGM 감소량 (dB)
    """
    # BGM 길이 맞추기
    if len(bgm) < len(voice):
        bgm = bgm * ((len(voice) // len(bgm)) + 1)
    bgm = bgm[:len(voice)]

    # Ducking (간단 버전 - 전체 구간)
    ducked_bgm = bgm - duck_amount

    # 믹싱
    return voice.overlay(ducked_bgm)

# 사용
result = duck_bgm(voice_audio, bgm_audio)
result.export("mixed.mp3", format="mp3")
```

---

## 외부 API

### Pexels API

**용도**: 무료 스톡 영상/이미지

**가격**: 무료 (Rate limit: 200 req/hour)

**문서**: https://www.pexels.com/api/documentation/

**API 키 발급**:
1. https://www.pexels.com/api/ 접속
2. 계정 생성 & API 키 발급

**사용 예시**:
```python
import requests

PEXELS_API_KEY = "YOUR_API_KEY"

def search_pexels_videos(query: str, orientation: str = "portrait", per_page: int = 10):
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "orientation": orientation,  # portrait, landscape, square
        "per_page": per_page
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    videos = []
    for video in data.get('videos', []):
        # 최고 화질 선택
        video_files = sorted(video['video_files'], key=lambda x: x.get('width', 0), reverse=True)
        videos.append({
            'id': video['id'],
            'url': video_files[0]['link'],
            'duration': video['duration'],
            'width': video_files[0]['width'],
            'height': video_files[0]['height'],
            'thumbnail': video['image']
        })

    return videos

# 검색
results = search_pexels_videos("cat funny", orientation="portrait")
print(f"Found {len(results)} videos")

# 다운로드
def download_video(url: str, output_path: str):
    response = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

download_video(results[0]['url'], "video.mp4")
```

---

### Pixabay API

**용도**: 대안 스톡 소스

**가격**: 무료 (Rate limit: 100 req/min)

**문서**: https://pixabay.com/api/docs/

**사용 예시**:
```python
PIXABAY_API_KEY = "YOUR_API_KEY"

def search_pixabay_videos(query: str, per_page: int = 10):
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": per_page
    }

    response = requests.get(url, params=params)
    data = response.json()

    videos = []
    for hit in data.get('hits', []):
        # 'large' 화질 선택
        video_url = hit['videos']['large']['url']
        videos.append({
            'id': hit['id'],
            'url': video_url,
            'duration': hit['duration'],
            'width': hit['videos']['large']['width'],
            'height': hit['videos']['large']['height']
        })

    return videos
```

---

### Google Cloud TTS (선택)

**용도**: 고품질 한국어 TTS (Vrew 대안)

**가격**: $16 / 1M 문자 (무료 할당: 0-4M 문자/월)

**문서**: https://cloud.google.com/text-to-speech/docs

**설정**:
```bash
# 1. GCP 프로젝트 생성
# 2. Cloud TTS API 활성화
# 3. 서비스 계정 키 다운로드 (JSON)

export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

# SDK 설치
pip install google-cloud-texttospeech
```

**사용 예시**:
```python
from google.cloud import texttospeech

def generate_tts(text: str, output_path: str, voice_name: str = "ko-KR-Neural2-A"):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name=voice_name  # ko-KR-Neural2-A (여성), ko-KR-Neural2-C (남성)
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,  # 0.25 ~ 4.0
        pitch=0.0           # -20.0 ~ 20.0
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open(output_path, "wb") as f:
        f.write(response.audio_content)

    print(f"Audio saved to {output_path}")

# 사용
generate_tts("안녕하세요, 오늘은 멋진 하루입니다.", "output.mp3")
```

**SSML 활용** (고급):
```python
ssml_text = """
<speak>
  안녕하세요.
  <break time="500ms"/>
  오늘은 <emphasis level="strong">정말 멋진</emphasis> 하루입니다.
  <prosody rate="slow" pitch="+2st">천천히 높은 목소리로</prosody>
</speak>
"""

synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
```

---

### YouTube Data API v3

**용도**: 영상 업로드 자동화

**가격**: 무료 (일일 쿼터: 10,000 units, 업로드 1회 = 1600 units)

**문서**: https://developers.google.com/youtube/v3

**OAuth 설정**:
```bash
# 1. GCP Console에서 OAuth 2.0 클라이언트 ID 생성
# 2. credentials.json 다운로드
# 3. 첫 실행 시 브라우저에서 인증

pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

**사용 예시**:
```python
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, file_path: str, title: str, description: str, tags: list, privacy: str = "private"):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '22'  # People & Blogs
        },
        'status': {
            'privacyStatus': privacy,  # public, unlisted, private
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    print(f"Upload complete! Video ID: {response['id']}")
    return f"https://www.youtube.com/watch?v={response['id']}"

# 사용
youtube = authenticate()
url = upload_video(
    youtube,
    "output.mp4",
    "🔥 TOP 10 고양이 순간들",
    "2024년 최고의 고양이 영상 모음\n\n출처: Pexels (CC0)",
    ["고양이", "TOP10", "쇼츠"],
    privacy="public"
)
print(url)
```

---

## 웹 스택 (Phase 4)

### FastAPI

**용도**: REST API 서버

**장점**:
- 빠름 (Starlette 기반)
- 자동 문서화 (OpenAPI/Swagger)
- 타입 힌팅 & 검증 (Pydantic)
- WebSocket 지원

**예시**:
```python
from fastapi import FastAPI, BackgroundTasks, UploadFile, File
from pydantic import BaseModel
from typing import List

app = FastAPI()

class RenderRequest(BaseModel):
    items: List[dict]
    style: str = "modern"
    aspect_ratio: str = "9:16"

@app.post("/api/shorts/render")
async def render_shorts(request: RenderRequest, background_tasks: BackgroundTasks):
    task_id = generate_task_id()

    background_tasks.add_task(
        render_task,
        task_id=task_id,
        data=request.dict()
    )

    return {"task_id": task_id, "status": "processing"}

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    # Redis에서 상태 조회
    status = redis_client.get(f"task:{task_id}")
    return {"task_id": task_id, "status": status}

@app.post("/api/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()
    # CSV 파싱
    return {"filename": file.filename, "rows": 10}

# 실행
# uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

### Celery + Redis

**용도**: 비동기 백그라운드 작업 (렌더링)

**설정**:
```python
# src/api/celery_app.py
from celery import Celery

celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
)
```

**Task 정의**:
```python
# src/api/tasks.py
from src.api.celery_app import celery_app
from src.shorts.batch_renderer import BatchRenderer

@celery_app.task(bind=True)
def render_task(self, task_id: str, data: dict):
    try:
        # 진행률 업데이트
        self.update_state(state='PROGRESS', meta={'progress': 10})

        renderer = BatchRenderer(style=data['style'])

        # 렌더링 (진행률 콜백)
        video_path = renderer.render(data['items'], output_dir=f"output/{task_id}")

        self.update_state(state='PROGRESS', meta={'progress': 90})

        # S3 업로드 (optional)
        # s3_url = upload_to_s3(video_path)

        return {'status': 'completed', 'video_url': video_path}

    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
```

**Worker 실행**:
```bash
celery -A src.api.celery_app worker --loglevel=info
```

---

### Next.js (프론트엔드)

**용도**: 웹 UI

**주요 페이지**:
```
pages/
├── index.tsx           # 홈 (프로젝트 선택)
├── shorts/
│   ├── upload.tsx      # CSV 업로드
│   ├── preview.tsx     # 스타일 선택 & 미리보기
│   └── result.tsx      # 결과 다운로드
└── api/
    └── render.ts       # Proxy to FastAPI
```

**예시 (업로드 페이지)**:
```tsx
// pages/shorts/upload.tsx
import { useState } from 'react'
import { useRouter } from 'next/router'

export default function ShortsUpload() {
  const [file, setFile] = useState(null)
  const router = useRouter()

  const handleSubmit = async () => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch('/api/render', {
      method: 'POST',
      body: formData
    })

    const { task_id } = await response.json()
    router.push(`/shorts/result?task_id=${task_id}`)
  }

  return (
    <div className="container">
      <h1>쇼츠 랭킹 영상 생성</h1>
      <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleSubmit}>생성 시작</button>
    </div>
  )
}
```

---

## 배포

### Docker

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

# FFmpeg 설치
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./output:/app/output
    depends_on:
      - redis

  worker:
    build: .
    command: celery -A src.api.celery_app worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./output:/app/output
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 성능 최적화

### FFmpeg 하드웨어 가속

**NVIDIA GPU (NVENC)**:
```bash
# 인코딩 2~5배 빠름
ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc -preset fast output.mp4
```

**Intel QSV**:
```bash
ffmpeg -hwaccel qsv -c:v h264_qsv -i input.mp4 -c:v h264_qsv output.mp4
```

**Apple Silicon (VideoToolbox)**:
```bash
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v h264_videotoolbox output.mp4
```

---

### Celery 분산 처리

```yaml
# docker-compose에서 worker 스케일 아웃
docker-compose up --scale worker=4
```

---

### Redis 캐싱

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Asset 검색 결과 캐싱 (24시간)
def search_with_cache(keyword: str):
    cache_key = f"asset:{keyword}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # API 호출
    results = fetch_from_pexels(keyword)

    redis_client.setex(cache_key, 86400, json.dumps(results))
    return results
```

---

## 모니터링

### Sentry (에러 추적)

```python
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    traces_sample_rate=1.0
)

# 자동 에러 캡처
```

---

### Prometheus (메트릭)

```python
from prometheus_client import Counter, Histogram, start_http_server

render_count = Counter('video_renders_total', 'Total renders')
render_duration = Histogram('video_render_duration_seconds', 'Render duration')

@render_duration.time()
def render_video():
    # 렌더링 로직
    render_count.inc()

# 메트릭 서버
start_http_server(8001)
```

---

## 개발 도구

### 코드 품질

```bash
# Linting
pip install ruff
ruff check src/

# Formatting
pip install black
black src/

# Type checking
pip install mypy
mypy src/
```

### 테스트

```bash
pip install pytest pytest-asyncio

# 실행
pytest tests/ -v
```

---

## 총 비용 (월간 예상)

| 항목 | 비용 |
|------|------|
| Vrew Pro | ₩10,000 (~$8) |
| Canva Pro (선택) | $13 |
| Google Cloud TTS (선택) | $0-16 |
| AWS EC2 t3.medium (선택) | $30 |
| S3 스토리지 100GB (선택) | $2 |
| **로컬 개발** | **$0-10** |
| **클라우드 배포** | **$30-60** |

---

## 다음 단계

1. 개발 환경 세팅 (Python, FFmpeg)
2. requirements.txt 작성 & 패키지 설치
3. Pexels API 키 발급
4. 샘플 클립 준비
5. 첫 테스트 렌더링
