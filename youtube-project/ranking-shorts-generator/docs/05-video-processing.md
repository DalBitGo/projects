# 영상 처리 파이프라인 설계

## 1. 개요

### 1.1 목적
선택된 TikTok 영상들을 다운로드하고, 편집하여 하나의 랭킹 쇼츠 영상으로 생성

### 1.2 처리 단계
```
Input: 5-7개 선택된 영상 URL
  ↓
[1] Download → 원본 영상 다운로드
  ↓
[2] Preprocess → 크롭, 리사이즈, 트림
  ↓
[3] Add Ranking Text → 랭킹 번호 텍스트 오버레이
  ↓
[4] Concatenate → 영상들을 순서대로 이어붙이기
  ↓
[5] Add Background Music → 배경음악 추가
  ↓
[6] Final Rendering → 최종 인코딩
  ↓
Output: 완성된 랭킹 쇼츠 (MP4)
```

---

## 2. 영상 다운로드

### 2.1 다운로드 전략

**사용 도구**:
- **yt-dlp**: TikTok, YouTube Shorts 등 다양한 플랫폼 지원
- **TikTokApi**: TikTok 전용

**선택**: yt-dlp (더 안정적, 범용적)

### 2.2 yt-dlp 설치 및 설정

```bash
pip install yt-dlp
```

### 2.3 다운로드 구현

```python
import yt_dlp
from pathlib import Path

def download_video(url: str, output_dir: str = "storage/downloads") -> str:
    """
    TikTok 영상 다운로드

    Args:
        url: TikTok 영상 URL
        output_dir: 저장 디렉토리

    Returns:
        str: 다운로드된 파일 경로
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        'format': 'best[height<=1920]',  # 최대 1080p
        'outtmpl': str(output_path / '%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename
```

### 2.4 병렬 다운로드

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def download_videos_parallel(urls: list) -> list:
    """
    여러 영상을 병렬로 다운로드

    Args:
        urls: 영상 URL 리스트

    Returns:
        list: 다운로드된 파일 경로 리스트
    """
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [
            loop.run_in_executor(executor, download_video, url)
            for url in urls
        ]
        results = await asyncio.gather(*tasks)

    return results
```

### 2.5 진행 상황 추적

```python
from tqdm import tqdm

class DownloadProgressHook:
    """다운로드 진행 상황 훅"""

    def __init__(self, callback=None):
        self.callback = callback
        self.pbar = None

    def __call__(self, d):
        if d['status'] == 'downloading':
            if self.pbar is None:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                self.pbar = tqdm(total=total, unit='B', unit_scale=True)

            downloaded = d.get('downloaded_bytes', 0)
            self.pbar.n = downloaded
            self.pbar.refresh()

            if self.callback:
                progress = (downloaded / d.get('total_bytes', 1)) * 100
                self.callback(progress)

        elif d['status'] == 'finished':
            if self.pbar:
                self.pbar.close()
            print(f"Download completed: {d['filename']}")

# 사용
ydl_opts = {
    'progress_hooks': [DownloadProgressHook()],
    # ... 기타 옵션
}
```

---

## 3. 영상 전처리 (Preprocessing)

### 3.1 요구사항
- **종횡비**: 9:16 (세로 영상, 1080x1920)
- **길이**: 각 영상 5~10초
- **품질**: 1080p, 30fps

### 3.2 FFmpeg를 사용한 전처리

#### 3.2.1 종횡비 감지 및 크롭

```python
import ffmpeg
import json

def get_video_info(video_path: str) -> dict:
    """영상 정보 추출"""
    probe = ffmpeg.probe(video_path)
    video_stream = next(
        (s for s in probe['streams'] if s['codec_type'] == 'video'),
        None
    )

    return {
        'width': int(video_stream['width']),
        'height': int(video_stream['height']),
        'duration': float(video_stream['duration']),
        'fps': eval(video_stream['r_frame_rate'])  # "30/1" → 30
    }

def crop_to_9_16(input_path: str, output_path: str):
    """
    영상을 9:16 비율로 크롭

    - 세로 영상 (9:16): 그대로 유지
    - 정사각형 (1:1): 좌우 크롭
    - 가로 영상 (16:9): 좌우 크롭 후 세로로 회전 또는 크롭
    """
    info = get_video_info(input_path)
    width, height = info['width'], info['height']

    # 목표 비율
    target_ratio = 9 / 16

    # 현재 비율
    current_ratio = width / height

    if abs(current_ratio - target_ratio) < 0.01:
        # 이미 9:16
        stream = ffmpeg.input(input_path)
    else:
        # 크롭 필요
        if current_ratio > target_ratio:
            # 너무 넓음 → 좌우 크롭
            crop_width = int(height * target_ratio)
            crop_height = height
            x_offset = (width - crop_width) // 2
            y_offset = 0
        else:
            # 너무 높음 → 상하 크롭
            crop_width = width
            crop_height = int(width / target_ratio)
            x_offset = 0
            y_offset = (height - crop_height) // 2

        stream = ffmpeg.input(input_path)
        stream = ffmpeg.crop(stream, x_offset, y_offset, crop_width, crop_height)

    # 1080x1920으로 리사이즈
    stream = ffmpeg.filter(stream, 'scale', 1080, 1920)

    # 출력
    stream = ffmpeg.output(stream, output_path, vcodec='libx264', crf=23, preset='medium')
    ffmpeg.run(stream, overwrite_output=True, quiet=True)
```

#### 3.2.2 영상 트림 (5-10초)

```python
def trim_video(input_path: str, output_path: str, duration: int = 7):
    """
    영상을 지정된 길이로 트림

    Args:
        input_path: 입력 영상 경로
        output_path: 출력 영상 경로
        duration: 목표 길이 (초)
    """
    info = get_video_info(input_path)
    video_duration = info['duration']

    if video_duration <= duration:
        # 이미 짧음 → 그대로 복사
        stream = ffmpeg.input(input_path)
    else:
        # 중간 부분 추출 (가장 흥미로운 부분이라고 가정)
        start_time = (video_duration - duration) / 2
        stream = ffmpeg.input(input_path, ss=start_time, t=duration)

    stream = ffmpeg.output(stream, output_path, vcodec='copy', acodec='copy')
    ffmpeg.run(stream, overwrite_output=True, quiet=True)
```

#### 3.2.3 통합 전처리 함수

```python
def preprocess_video(
    input_path: str,
    output_path: str,
    target_duration: int = 7
) -> str:
    """
    영상 전처리: 크롭 + 리사이즈 + 트림

    Returns:
        str: 처리된 영상 경로
    """
    temp_cropped = output_path.replace('.mp4', '_cropped.mp4')

    # 1. 크롭 및 리사이즈
    crop_to_9_16(input_path, temp_cropped)

    # 2. 트림
    trim_video(temp_cropped, output_path, target_duration)

    # 3. 임시 파일 삭제
    Path(temp_cropped).unlink()

    return output_path
```

---

## 4. 랭킹 텍스트 오버레이

### 4.1 텍스트 디자인

**랭킹 1위**:
- 텍스트: "🥇 #1"
- 폰트: Arial Bold, 72pt
- 색상: 흰색 + 검은색 테두리
- 위치: 화면 상단 중앙 (y=100px)
- 애니메이션: 페이드 인 (0.5초)

**랭킹 2~10위**:
- 텍스트: "#2", "#3", ... "#10"
- 아이콘: 🥈 (2위), 🥉 (3위)

### 4.2 MoviePy를 사용한 텍스트 추가

```python
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def add_ranking_text(
    input_path: str,
    output_path: str,
    rank: int
) -> str:
    """
    랭킹 텍스트 오버레이 추가

    Args:
        input_path: 입력 영상
        output_path: 출력 영상
        rank: 랭킹 순위 (1, 2, 3, ...)

    Returns:
        str: 처리된 영상 경로
    """
    # 영상 로드
    video = VideoFileClip(input_path)

    # 랭킹 텍스트 생성
    if rank == 1:
        text = "🥇 #1"
    elif rank == 2:
        text = "🥈 #2"
    elif rank == 3:
        text = "🥉 #3"
    else:
        text = f"#{rank}"

    # 텍스트 클립 생성
    txt_clip = TextClip(
        text,
        fontsize=72,
        color='white',
        font='Arial-Bold',
        stroke_color='black',
        stroke_width=3,
        method='caption',
        size=(video.w, None)
    )

    # 위치 및 지속 시간 설정
    txt_clip = txt_clip.set_position(('center', 100)).set_duration(video.duration)

    # 페이드 인 효과 (0.5초)
    txt_clip = txt_clip.crossfadein(0.5)

    # 영상과 텍스트 합성
    final = CompositeVideoClip([video, txt_clip])

    # 저장
    final.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=30,
        preset='medium',
        threads=4
    )

    # 메모리 정리
    video.close()
    txt_clip.close()
    final.close()

    return output_path
```

### 4.3 FFmpeg를 사용한 텍스트 추가 (대안)

```python
def add_ranking_text_ffmpeg(
    input_path: str,
    output_path: str,
    rank: int,
    font_path: str = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
) -> str:
    """
    FFmpeg drawtext 필터를 사용한 텍스트 오버레이
    """
    # 랭킹 텍스트
    if rank == 1:
        text = "🥇 #1"
    elif rank == 2:
        text = "🥈 #2"
    elif rank == 3:
        text = "🥉 #3"
    else:
        text = f"#{rank}"

    # 이모지는 FFmpeg에서 렌더링 어려움 → 대체 텍스트 사용
    text_alt = f"RANK #{rank}"

    stream = ffmpeg.input(input_path)
    stream = ffmpeg.drawtext(
        stream,
        text=text_alt,
        fontfile=font_path,
        fontsize=72,
        fontcolor='white',
        borderw=3,
        bordercolor='black',
        x='(w-text_w)/2',  # 중앙
        y=100,
        enable=f'gte(t,0.5)'  # 0.5초 후 표시
    )

    stream = ffmpeg.output(stream, output_path, vcodec='libx264', acodec='copy')
    ffmpeg.run(stream, overwrite_output=True, quiet=True)

    return output_path
```

---

## 5. 영상 이어붙이기 (Concatenation)

### 5.1 MoviePy 사용

```python
from moviepy.editor import concatenate_videoclips

def concatenate_videos(video_paths: list, output_path: str) -> str:
    """
    여러 영상을 순서대로 이어붙이기

    Args:
        video_paths: 영상 경로 리스트 (순서대로)
        output_path: 출력 경로

    Returns:
        str: 최종 영상 경로
    """
    clips = [VideoFileClip(path) for path in video_paths]

    # 이어붙이기
    final_clip = concatenate_videoclips(clips, method="compose")

    # 저장
    final_clip.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=30,
        preset='medium',
        threads=4
    )

    # 메모리 정리
    for clip in clips:
        clip.close()
    final_clip.close()

    return output_path
```

### 5.2 FFmpeg concat 사용 (더 빠름)

```python
def concatenate_videos_ffmpeg(video_paths: list, output_path: str) -> str:
    """
    FFmpeg concat demuxer를 사용한 이어붙이기 (빠름)
    """
    # concat 파일 생성
    concat_file = "concat_list.txt"
    with open(concat_file, 'w') as f:
        for path in video_paths:
            f.write(f"file '{path}'\n")

    # FFmpeg concat
    stream = ffmpeg.input(concat_file, format='concat', safe=0)
    stream = ffmpeg.output(stream, output_path, c='copy')
    ffmpeg.run(stream, overwrite_output=True, quiet=True)

    # concat 파일 삭제
    Path(concat_file).unlink()

    return output_path
```

---

## 6. 배경음악 추가

### 6.1 음악 라이브러리 관리

```
storage/music/
├── energetic_1.mp3
├── chill_1.mp3
├── epic_1.mp3
└── ...
```

### 6.2 배경음악 믹싱

```python
from moviepy.editor import AudioFileClip

def add_background_music(
    video_path: str,
    music_path: str,
    output_path: str,
    music_volume: float = 0.3  # 30% 볼륨
) -> str:
    """
    배경음악 추가

    Args:
        video_path: 영상 경로
        music_path: 음악 경로
        output_path: 출력 경로
        music_volume: 배경음악 볼륨 (0.0~1.0)

    Returns:
        str: 최종 영상 경로
    """
    video = VideoFileClip(video_path)
    music = AudioFileClip(music_path)

    # 음악 길이 조정
    if music.duration > video.duration:
        music = music.subclip(0, video.duration)
    else:
        # 음악이 짧으면 루프
        music = music.audio_loop(duration=video.duration)

    # 볼륨 조정
    music = music.volumex(music_volume)

    # 원본 오디오와 믹싱
    if video.audio:
        final_audio = CompositeAudioClip([video.audio, music])
    else:
        final_audio = music

    # 영상에 오디오 추가
    final_video = video.set_audio(final_audio)

    # 저장
    final_video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=30,
        preset='medium',
        threads=4
    )

    # 메모리 정리
    video.close()
    music.close()
    final_video.close()

    return output_path
```

### 6.3 FFmpeg를 사용한 음악 추가

```python
def add_background_music_ffmpeg(
    video_path: str,
    music_path: str,
    output_path: str,
    music_volume: float = 0.3
) -> str:
    """
    FFmpeg를 사용한 배경음악 추가 (더 빠름)
    """
    video = ffmpeg.input(video_path)
    audio = ffmpeg.input(music_path)

    # 오디오 믹싱
    video_audio = video.audio
    music_audio = audio.filter('volume', music_volume)

    mixed = ffmpeg.filter([video_audio, music_audio], 'amix', duration='first')

    # 최종 출력
    out = ffmpeg.output(
        video.video,
        mixed,
        output_path,
        vcodec='copy',
        acodec='aac',
        audio_bitrate='192k'
    )

    ffmpeg.run(out, overwrite_output=True, quiet=True)

    return output_path
```

---

## 7. 최종 렌더링 및 최적화

### 7.1 인코딩 설정

```python
def final_render(
    input_path: str,
    output_path: str,
    quality: str = 'high'  # 'low', 'medium', 'high'
) -> str:
    """
    최종 렌더링 및 최적화

    Args:
        input_path: 입력 영상
        output_path: 출력 영상
        quality: 품질 ('low': 모바일, 'medium': 일반, 'high': 고품질)

    Returns:
        str: 최종 영상 경로
    """
    # 품질별 설정
    quality_settings = {
        'low': {'crf': 28, 'preset': 'faster', 'bitrate': '2M'},
        'medium': {'crf': 23, 'preset': 'medium', 'bitrate': '5M'},
        'high': {'crf': 18, 'preset': 'slow', 'bitrate': '8M'},
    }

    settings = quality_settings[quality]

    stream = ffmpeg.input(input_path)
    stream = ffmpeg.output(
        stream,
        output_path,
        vcodec='libx264',
        acodec='aac',
        crf=settings['crf'],
        preset=settings['preset'],
        video_bitrate=settings['bitrate'],
        audio_bitrate='192k',
        **{'movflags': '+faststart'}  # 웹 스트리밍 최적화
    )

    ffmpeg.run(stream, overwrite_output=True, quiet=True)

    return output_path
```

### 7.2 GPU 가속 (NVENC)

```python
def final_render_gpu(input_path: str, output_path: str) -> str:
    """
    NVIDIA GPU를 사용한 하드웨어 가속 인코딩
    """
    stream = ffmpeg.input(input_path)
    stream = ffmpeg.output(
        stream,
        output_path,
        vcodec='h264_nvenc',  # NVENC 사용
        preset='p4',  # p1~p7 (p7이 가장 느리고 고품질)
        acodec='aac',
        video_bitrate='8M',
        audio_bitrate='192k'
    )

    ffmpeg.run(stream, overwrite_output=True, quiet=True)

    return output_path
```

---

## 8. 전체 파이프라인 통합

### 8.1 메인 처리 함수

```python
from pathlib import Path
import uuid

def generate_ranking_video(
    video_urls: list,
    output_path: str,
    music_path: str = None,
    progress_callback=None
) -> str:
    """
    랭킹 쇼츠 영상 생성 전체 파이프라인

    Args:
        video_urls: 영상 URL 리스트 (순서대로)
        output_path: 최종 출력 경로
        music_path: 배경음악 경로 (선택)
        progress_callback: 진행 상황 콜백 함수

    Returns:
        str: 최종 영상 경로
    """
    temp_dir = Path("storage/temp") / str(uuid.uuid4())
    temp_dir.mkdir(parents=True, exist_ok=True)

    total_steps = len(video_urls) * 3 + 2  # 다운로드 + 전처리 + 텍스트 + 합치기 + 음악
    current_step = 0

    def update_progress(message: str):
        nonlocal current_step
        current_step += 1
        if progress_callback:
            progress_callback(current_step, total_steps, message)

    try:
        # 1. 다운로드
        downloaded_paths = []
        for i, url in enumerate(video_urls):
            update_progress(f"Downloading video {i+1}/{len(video_urls)}")
            path = download_video(url, str(temp_dir))
            downloaded_paths.append(path)

        # 2. 전처리 (크롭, 리사이즈, 트림)
        preprocessed_paths = []
        for i, path in enumerate(downloaded_paths):
            update_progress(f"Preprocessing video {i+1}/{len(video_urls)}")
            output = str(temp_dir / f"preprocessed_{i}.mp4")
            preprocess_video(path, output, target_duration=7)
            preprocessed_paths.append(output)

        # 3. 랭킹 텍스트 추가
        ranked_paths = []
        for i, path in enumerate(preprocessed_paths):
            update_progress(f"Adding ranking text {i+1}/{len(video_urls)}")
            output = str(temp_dir / f"ranked_{i}.mp4")
            add_ranking_text(path, output, rank=i+1)
            ranked_paths.append(output)

        # 4. 영상 합치기
        update_progress("Concatenating videos")
        concat_output = str(temp_dir / "concatenated.mp4")
        concatenate_videos(ranked_paths, concat_output)

        # 5. 배경음악 추가
        if music_path:
            update_progress("Adding background music")
            add_background_music(concat_output, music_path, output_path)
        else:
            # 음악 없으면 그대로 복사
            import shutil
            shutil.copy(concat_output, output_path)

        update_progress("Rendering complete!")

        return output_path

    finally:
        # 임시 파일 정리
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
```

### 8.2 Celery 작업 통합

```python
from celery import Task
from app.celery_app import celery_app

@celery_app.task(bind=True, name="generate_ranking_video")
def generate_ranking_video_task(
    self: Task,
    project_id: str,
    video_urls: list,
    music_path: str = None
):
    """
    Celery 작업: 랭킹 영상 생성
    """
    output_path = f"storage/output/pending/{project_id}.mp4"

    def progress_callback(current, total, message):
        self.update_state(
            state='PROGRESS',
            meta={
                'current': current,
                'total': total,
                'status': message,
                'percent': int((current / total) * 100)
            }
        )

    try:
        final_path = generate_ranking_video(
            video_urls,
            output_path,
            music_path,
            progress_callback
        )

        return {
            'project_id': project_id,
            'video_path': final_path,
            'status': 'completed'
        }

    except Exception as e:
        return {
            'project_id': project_id,
            'error': str(e),
            'status': 'failed'
        }
```

---

## 9. 성능 최적화

### 9.1 멀티스레딩

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_preprocess(video_paths: list) -> list:
    """
    병렬로 전처리 수행
    """
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(preprocess_video, path, path.replace('.mp4', '_processed.mp4'))
            for path in video_paths
        ]
        results = [f.result() for f in futures]

    return results
```

### 9.2 메모리 최적화

```python
import gc

def process_with_memory_cleanup(video_paths: list):
    """
    메모리 정리를 포함한 처리
    """
    for path in video_paths:
        # 처리
        result = preprocess_video(path, ...)

        # 메모리 정리
        gc.collect()

    return results
```

---

## 10. 에러 처리 및 품질 검증

### 10.1 영상 유효성 검사

```python
def validate_video(video_path: str) -> bool:
    """
    생성된 영상 유효성 검사
    """
    try:
        info = get_video_info(video_path)

        # 검증 조건
        checks = [
            info['width'] == 1080,
            info['height'] == 1920,
            info['duration'] > 0,
            Path(video_path).stat().st_size > 1024 * 100,  # 최소 100KB
        ]

        return all(checks)

    except Exception as e:
        print(f"Validation failed: {e}")
        return False
```

### 10.2 에러 복구

```python
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def robust_video_processing(input_path: str, output_path: str):
    """
    재시도 로직이 포함된 영상 처리
    """
    try:
        preprocess_video(input_path, output_path)

        if not validate_video(output_path):
            raise ValueError("Invalid output video")

        return output_path

    except Exception as e:
        print(f"Processing failed, retrying: {e}")
        raise
```

---

## 11. 썸네일 생성

```python
def generate_thumbnail(video_path: str, thumbnail_path: str, timestamp: float = 1.0):
    """
    영상에서 썸네일 추출

    Args:
        video_path: 영상 경로
        thumbnail_path: 썸네일 저장 경로
        timestamp: 추출 시간 (초)
    """
    stream = ffmpeg.input(video_path, ss=timestamp)
    stream = ffmpeg.output(stream, thumbnail_path, vframes=1)
    ffmpeg.run(stream, overwrite_output=True, quiet=True)

    return thumbnail_path
```

---

**문서 버전**: 1.0
**작성일**: 2025-10-19
**최종 수정일**: 2025-10-19
