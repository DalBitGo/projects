# 쇼츠 랭킹 영상 생성기 - 상세 스펙 v2

## 개요
CSV 데이터 입력 → 템플릿 기반 자동 조립 → BGM 믹싱 → 배치 렌더링 → MP4 출력

**핵심**: 음성/나레이션 없이 BGM + 텍스트 오버레이만으로 완결

---

## 입력 포맷

### CSV 구조
```csv
rank,title,description,clip_path,emoji,score,duration
1,웃긴 고양이,빵 터지는 순간,clips/cat1.mp4,😹,9.8,10
2,강아지 산책,귀여운 산책 영상,clips/dog1.mp4,🐶,9.5,12
3,햄스터 먹방,햄스터 먹는 모습,clips/hamster.mp4,🐹,9.2,8
```

### 필드 설명
- `rank` (필수): 순위 (1, 2, 3...)
- `title` (필수): 메인 제목 (30자 이내)
- `description` (선택): 부제목/설명 (50자 이내)
- `clip_path` (필수): 소스 영상 경로
- `emoji` (선택): 대표 이모지 (1개)
- `score` (선택): 점수 (표시용)
- `duration` (선택): 클립 길이 (초, 기본 10초)

### JSON 포맷 (대안)
```json
{
  "meta": {
    "title": "🔥 역대급 고양이 TOP 10",
    "description": "2024년 최고의 고양이 영상들",
    "style": "modern",
    "aspect_ratio": "9:16",
    "bgm": "assets/bgm/upbeat.mp3"
  },
  "items": [
    {
      "rank": 1,
      "title": "웃긴 고양이",
      "clip_path": "clips/cat1.mp4",
      "emoji": "😹",
      "score": 9.8,
      "duration": 10
    }
  ]
}
```

---

## 출력 스펙

### 영상 설정
```yaml
해상도: 1080x1920 (9:16) or 1920x1080 (16:9)
프레임레이트: 30fps
코덱: H.264 (libx264)
비트레이트: 8Mbps (VBR)
오디오: AAC 192kbps (BGM만)
길이:
  - 클립당: 8-15초
  - 전체: 60-90초 권장 (Shorts)
```

### 파일명 규칙
```
{title_slug}_{timestamp}.mp4
예: top10-cats_20240124_153045.mp4
```

---

## 디자인 템플릿

### 화면 구성 (9:16 기준)

```
┌────────────────────────┐  1920px
│                        │
│  [1위] 😹             │  ← 상단: 순위 뱃지 + 이모지
│   ⭐ 9.8 / 10         │
│                        │
│   ┌──────────────┐     │
│   │              │     │
│   │              │     │
│   │   클립 영역   │     │  ← 중앙: 원본 클립 (900x1600)
│   │              │     │     배경: 블러 처리
│   │              │     │     프레임: 둥근 모서리
│   │              │     │
│   └──────────────┘     │
│                        │
│  ┌──────────────────┐  │
│  │  웃긴 고양이 순간  │  │  ← 하단: 제목 (반투명 박스)
│  │  빵 터지는 모먼트  │  │     설명 (작은 글씨)
│  └──────────────────┘  │
│                        │
│    ━━━━━━━━━━━━━━━    │  ← 진행바 (선택)
└────────────────────────┘  1080px
```

### 레이어 구조
```
Layer 6: 진행바 (선택)
Layer 5: 텍스트 오버레이 (제목, 설명, 점수)
Layer 4: 순위 뱃지 + 이모지
Layer 3: 프레임 오버레이 (PNG alpha)
Layer 2: 클립 영상 (리사이즈)
Layer 1: 배경 (블러 or 그라데이션)
```

---

## 템플릿 스타일

### Style 1: Modern (기본)
```yaml
name: "Modern"
aspect_ratio: "9:16"

colors:
  gold: "#FFD700"      # 1위
  silver: "#C0C0C0"    # 2위
  bronze: "#CD7F32"    # 3위
  primary: "#667eea"   # 4위 이하
  secondary: "#764ba2"
  text: "#FFFFFF"
  background: "#000000"

fonts:
  bold: "NotoSansKR-Bold.ttf"
  regular: "NotoSansKR-Regular.ttf"
  emoji: "NotoColorEmoji.ttf"

layout:
  badge_position: [60, 80]      # 좌상단
  emoji_position: [920, 80]     # 우상단
  score_position: [60, 220]     # 좌상단 아래
  clip_area:
    width: 900
    height: 1600
    position: [90, 160]  # 중앙
  title_position: [540, 1650]   # 하단 중앙
  description_position: [540, 1730]

sizes:
  badge_diameter: 120
  emoji_size: 100
  title_font_size: 70
  description_font_size: 50
  score_font_size: 40

effects:
  blur_radius: 50
  vignette_opacity: 0.3
  corner_radius: 20
  shadow: "0px 10px 40px rgba(0,0,0,0.5)"

animations:
  intro_duration: 0.5    # 페이드인
  outro_duration: 0.3    # 페이드아웃
  transition: "crossfade"
  transition_duration: 0.3
```

### Style 2: Neon
```yaml
name: "Neon"
colors:
  primary: "#FF006E"
  secondary: "#8338EC"
  glow: "#00F5FF"

effects:
  glow_effect: true
  neon_border: 4
  pulse_animation: true
```

### Style 3: Minimal
```yaml
name: "Minimal"
colors:
  background: "#FFFFFF"
  text: "#000000"

effects:
  blur_radius: 0
  shadows: false
  simple_transitions: true
```

---

## 애니메이션 & 전환

### 인트로 (각 클립 시작)
```
Timeline:
0.0s: 순위 뱃지 등장 (Scale-in, 0.5 → 1.0)
0.1s: 클립 등장 (Fade-in + Slide-up 50px)
0.2s: 제목 등장 (Fade-in)
0.3s: 이모지 등장 (Bounce-in)
0.4s: 점수 등장 (Fade-in, 선택)
```

### 강조 효과 (중간)
```
Duration/2: 순위 뱃지 펄스
  - Scale: 1.0 → 1.1 → 1.0
  - Duration: 0.3s
```

### 아웃트로 (각 클립 끝)
```
-0.3s: 전체 Fade-out (0.3s)
```

### 클립 간 전환
```
타입: Crossfade (기본) or Slide
Duration: 0.3s
방향: 좌→우 (rank 순서)
```

---

## 오디오 처리

### BGM (기본)
```yaml
소스:
  - 사용자 제공 MP3/WAV
  - 기본 템플릿 BGM

처리:
  - 전체 길이에 맞춰 자동 루프
  - 페이드 인/아웃 (각 2초)
  - 볼륨: 0.3 (30%)

고급 (선택):
  - 비트 싱크: 클립 전환을 BGM 비트에 맞춤
  - Ducking: 나레이션 있을 경우 BGM 자동 감소
```

### 나레이션 (선택적 기능)
```yaml
방식: Cloud TTS (Google/Azure)
스크립트 자동 생성:
  - "1위는 [제목]입니다."
  - "[설명]"

타이밍:
  - 각 클립 시작 0.5초 후
  - 자막 자동 생성 (선택)

음성:
  - ko-KR-Neural2-A (여성)
  - ko-KR-Neural2-C (남성)
```

---

## 기술 구현

### Phase 1: 템플릿 생성 (Pillow)

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class TemplateEngine:
    def __init__(self, style: str = "modern"):
        self.config = self.load_config(f"templates/ranking/{style}/config.yaml")

    def create_overlay(self, rank: int, title: str, emoji: str = "",
                       score: float = None, description: str = "") -> str:
        """1080x1920 오버레이 생성"""

        # 투명 캔버스
        canvas = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        # 1. 순위 뱃지
        badge = self._create_badge(rank)
        badge_pos = tuple(self.config['layout']['badge_position'])
        canvas.paste(badge, badge_pos, badge)

        # 2. 이모지
        if emoji:
            emoji_img = self._render_emoji(emoji)
            emoji_pos = tuple(self.config['layout']['emoji_position'])
            canvas.paste(emoji_img, emoji_pos, emoji_img)

        # 3. 점수
        if score:
            score_text = f"⭐ {score} / 10"
            score_pos = tuple(self.config['layout']['score_position'])
            font_score = ImageFont.truetype(
                self.config['fonts']['regular'],
                self.config['sizes']['score_font_size']
            )
            draw.text(score_pos, score_text,
                     font=font_score,
                     fill=self.config['colors']['text'])

        # 4. 제목 박스
        title_img = self._create_title_box(title, description)
        title_pos = tuple(self.config['layout']['title_position'])
        canvas.paste(title_img, (0, title_pos[1]), title_img)

        # 저장
        output_path = f"output/overlays/overlay_{rank:02d}.png"
        canvas.save(output_path)
        return output_path

    def _create_badge(self, rank: int) -> Image:
        """금/은/동/일반 뱃지 생성"""
        colors = self.config['colors']
        if rank == 1:
            color = colors['gold']
        elif rank == 2:
            color = colors['silver']
        elif rank == 3:
            color = colors['bronze']
        else:
            color = colors['primary']

        size = self.config['sizes']['badge_diameter']
        badge = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(badge)

        # 원형 배경
        draw.ellipse([0, 0, size, size], fill=color)

        # 숫자
        font = ImageFont.truetype(self.config['fonts']['bold'], 60)
        text = str(rank)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_pos = ((size - text_w) // 2, (size - text_h) // 2)
        draw.text(text_pos, text, font=font, fill=(255, 255, 255))

        return badge

    def _create_title_box(self, title: str, description: str) -> Image:
        """제목 + 설명 박스"""
        box = Image.new('RGBA', (1080, 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(box)

        # 제목
        font_title = ImageFont.truetype(
            self.config['fonts']['bold'],
            self.config['sizes']['title_font_size']
        )
        bbox = draw.textbbox((0, 0), title, font=font_title)
        title_w = bbox[2] - bbox[0]

        # 반투명 박스
        padding = 40
        box_coords = [
            (540 - title_w//2 - padding, 20),
            (540 + title_w//2 + padding, 120)
        ]
        draw.rounded_rectangle(box_coords, radius=20, fill=(0, 0, 0, 180))

        # 제목 텍스트
        draw.text((540, 30), title,
                 font=font_title,
                 fill=(255, 255, 255),
                 anchor="mt")

        # 설명 (있으면)
        if description:
            font_desc = ImageFont.truetype(
                self.config['fonts']['regular'],
                self.config['sizes']['description_font_size']
            )
            draw.text((540, 90), description,
                     font=font_desc,
                     fill=(200, 200, 200),
                     anchor="mt")

        return box
```

---

### Phase 2: 영상 합성 (FFmpeg)

```python
import subprocess
from pathlib import Path

class VideoCompositor:
    def compose_clip(self, clip_path: str, overlay_path: str,
                     output_path: str, duration: float = 10,
                     aspect_ratio: str = "9:16"):
        """
        단일 랭킹 클립 합성
        1. 클립 리사이즈 (9:16 or 16:9)
        2. 배경 블러 처리
        3. 오버레이 합성
        """

        if aspect_ratio == "9:16":
            width, height = 1080, 1920
            clip_w, clip_h = 900, 1600
        else:  # 16:9
            width, height = 1920, 1080
            clip_w, clip_h = 1600, 900

        cmd = f"""
        ffmpeg -i "{clip_path}" -i "{overlay_path}" -filter_complex "
          [0:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}[scaled];
          [scaled]split[main][blur];
          [blur]gblur=sigma=50[blurred];
          color=c=black@0.3:s={width}x{height}:d={duration}[vignette];
          [blurred][vignette]overlay=0:0[bg];
          [main]scale={clip_w}:{clip_h}:force_original_aspect_ratio=decrease[resized];
          [bg][resized]overlay=(W-w)/2:(H-h)/2[with_clip];
          [with_clip][1:v]overlay=0:0,
          fade=t=in:st=0:d=0.5,fade=t=out:st={duration-0.3}:d=0.3
        " -t {duration} -c:v libx264 -preset fast -crf 23 -r 30 -an "{output_path}"
        """

        subprocess.run(cmd, shell=True, check=True)

    def concatenate_clips(self, clip_list: list, output_path: str,
                         transition: str = "crossfade",
                         transition_duration: float = 0.3):
        """
        여러 클립 연결 + 전환 효과
        """
        if transition == "crossfade":
            # xfade 필터 체인 생성
            self._concatenate_with_xfade(clip_list, output_path, transition_duration)
        else:
            # 단순 concat
            concat_file = Path("output/concat.txt")
            with open(concat_file, 'w') as f:
                for clip in clip_list:
                    f.write(f"file '{Path(clip).absolute()}'\n")

            cmd = f'ffmpeg -f concat -safe 0 -i "{concat_file}" -c copy "{output_path}"'
            subprocess.run(cmd, shell=True, check=True)

    def _concatenate_with_xfade(self, clips: list, output: str, duration: float):
        """xfade 전환 효과 (복잡한 필터 체인)"""
        if len(clips) == 1:
            subprocess.run(f'cp "{clips[0]}" "{output}"', shell=True, check=True)
            return

        # xfade 필터 체인 생성 (간단 버전: 2개만)
        cmd = f"""
        ffmpeg -i "{clips[0]}" -i "{clips[1]}" -filter_complex "
          [0:v][1:v]xfade=transition=fade:duration={duration}:offset=9.7
        " -c:v libx264 -preset fast "{output}"
        """
        subprocess.run(cmd, shell=True, check=True)

    def add_bgm(self, video_path: str, bgm_path: str,
                output_path: str, volume: float = 0.3):
        """
        BGM 추가 (자동 루프, 페이드)
        """
        cmd = f"""
        ffmpeg -i "{video_path}" -stream_loop -1 -i "{bgm_path}" -filter_complex "
          [1:a]volume={volume},afade=t=in:st=0:d=2,afade=t=out:st=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 '{video_path}' | awk '{{print $1-2}}'):d=2[bgm];
          [bgm]atrim=duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 '{video_path}')[bgm_final]
        " -map 0:v -map "[bgm_final]" -c:v copy -c:a aac -shortest "{output_path}"
        """
        subprocess.run(cmd, shell=True, check=True)
```

---

### Phase 3: 배치 처리 (Python)

```python
import pandas as pd
from tqdm import tqdm

class BatchRenderer:
    def __init__(self, style: str = "modern", aspect_ratio: str = "9:16"):
        self.template_engine = TemplateEngine(style)
        self.compositor = VideoCompositor()
        self.aspect_ratio = aspect_ratio

    def render_from_csv(self, csv_path: str, output_dir: str,
                        bgm_path: str = None) -> str:
        """
        CSV → 최종 영상
        """
        # 1. CSV 읽기
        df = pd.read_csv(csv_path)

        # 2. 각 항목 처리
        clip_paths = []
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Rendering"):
            # 오버레이 생성
            overlay = self.template_engine.create_overlay(
                rank=row['rank'],
                title=row['title'],
                emoji=row.get('emoji', ''),
                score=row.get('score'),
                description=row.get('description', '')
            )

            # 클립 합성
            output_clip = f"{output_dir}/clip_{row['rank']:02d}.mp4"
            self.compositor.compose_clip(
                clip_path=row['clip_path'],
                overlay_path=overlay,
                output_path=output_clip,
                duration=row.get('duration', 10),
                aspect_ratio=self.aspect_ratio
            )
            clip_paths.append(output_clip)

        # 3. 연결
        concat_output = f"{output_dir}/ranking_raw.mp4"
        self.compositor.concatenate_clips(clip_paths, concat_output)

        # 4. BGM 추가
        if bgm_path:
            final_output = f"{output_dir}/final.mp4"
            self.compositor.add_bgm(concat_output, bgm_path, final_output)
        else:
            final_output = concat_output

        print(f"✅ Video created: {final_output}")
        return final_output

# 사용 예시
renderer = BatchRenderer(style="modern", aspect_ratio="9:16")
video = renderer.render_from_csv(
    csv_path="data/ranking.csv",
    output_dir="output/videos",
    bgm_path="assets/bgm/upbeat.mp3"
)
```

---

## 선택적 기능

### 1. 나레이션 추가 (Cloud TTS)

```python
from google.cloud import texttospeech

class NarrationGenerator:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()

    def generate_script(self, items: list) -> str:
        """자동 스크립트 생성"""
        script = []
        for item in items:
            script.append(f"{item['rank']}위는 {item['title']}입니다.")
            if item.get('description'):
                script.append(item['description'])
        return " ".join(script)

    def synthesize(self, text: str, output_path: str,
                   voice: str = "ko-KR-Neural2-A"):
        """TTS 합성"""
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice_params = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name=voice
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )

        with open(output_path, "wb") as f:
            f.write(response.audio_content)

# 사용
narration_gen = NarrationGenerator()
script = narration_gen.generate_script(items)
narration_gen.synthesize(script, "output/narration.mp3")

# 영상에 추가 (BGM과 믹싱)
# ffmpeg로 narration + BGM ducking
```

---

### 2. BGM 비트 싱크

```python
import librosa
import numpy as np

class BeatAnalyzer:
    def detect_beats(self, audio_path: str) -> list:
        """BGM에서 비트 추출"""
        y, sr = librosa.load(audio_path)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        return beat_times.tolist()

    def align_clips_to_beats(self, clip_durations: list, beats: list) -> list:
        """클립 길이를 비트에 맞춤"""
        aligned = []
        current_beat_idx = 0

        for duration in clip_durations:
            # 가장 가까운 비트 찾기
            target_beats = int(duration / (60 / tempo))  # 비트 수
            beat_duration = beats[current_beat_idx + target_beats] - beats[current_beat_idx]
            aligned.append(beat_duration)
            current_beat_idx += target_beats

        return aligned

# 사용
analyzer = BeatAnalyzer()
beats = analyzer.detect_beats("assets/bgm/upbeat.mp3")
aligned_durations = analyzer.align_clips_to_beats([10, 12, 8], beats)
```

---

## 품질 체크리스트

### 렌더링 전
- [ ] 모든 클립 파일 존재 확인
- [ ] 클립 해상도 검증 (최소 720p)
- [ ] CSV 데이터 검증 (필수 필드)
- [ ] 폰트 파일 존재 확인
- [ ] BGM 파일 확인

### 렌더링 중
- [ ] FFmpeg 에러 모니터링
- [ ] 진행률 표시 (tqdm)
- [ ] 임시 파일 정리

### 렌더링 후
- [ ] 전체 길이 확인 (60-90초)
- [ ] 오디오 싱크 확인
- [ ] 텍스트 가독성 체크
- [ ] 전환 부드러움 확인
- [ ] 파일 크기 검증 (< 50MB)

---

## 성능 목표

| 항목 | 목표 |
|------|------|
| 10개 클립 (각 10초) 렌더링 | < 5분 (CPU) |
| GPU 가속 시 | < 2분 |
| 메모리 사용 | < 4GB |
| 출력 파일 크기 | 60초 < 50MB |

---

## CLI 사용법

```bash
# 기본 사용
python -m src.cli.generate shorts ranking \
  --input data/ranking.csv \
  --output output/videos

# 스타일 선택
python -m src.cli.generate shorts ranking \
  --input data/ranking.csv \
  --style neon \
  --aspect 16:9

# BGM 추가
python -m src.cli.generate shorts ranking \
  --input data/ranking.csv \
  --bgm assets/bgm/upbeat.mp3 \
  --bgm-volume 0.3

# 나레이션 추가 (선택)
python -m src.cli.generate shorts ranking \
  --input data/ranking.csv \
  --narration auto \
  --voice ko-KR-Neural2-A

# 비트 싱크 (선택)
python -m src.cli.generate shorts ranking \
  --input data/ranking.csv \
  --bgm music.mp3 \
  --beat-sync

# YouTube 업로드 (선택)
python -m src.cli.generate shorts ranking \
  --input data/ranking.csv \
  --upload \
  --title "🔥 TOP 10 고양이 순간들" \
  --privacy public
```

---

## 다음 단계

1. Modern 템플릿 완성 (Canva → PNG export)
2. TemplateEngine 구현
3. VideoCompositor 구현
4. BatchRenderer 통합
5. CLI 도구
6. 10개 샘플 영상 테스트
