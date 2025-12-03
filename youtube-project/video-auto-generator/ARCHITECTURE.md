# 전체 아키텍처 설계 v2

## 프로젝트 개요

YouTube 쇼츠 자동 생성 시스템 - 데이터 입력부터 영상 합성, 편집, 업로드까지 완전 자동화

### 프로젝트 범위

**Phase 1 (현재)**: 쇼츠 생성기
- 랭킹형 (Top 10, 베스트 5)
- 비교형 (A vs B)
- 전후형 (Before & After)
- 기타 확장 가능한 쇼츠 타입

**Phase 2 (추후)**: 일반 영상 생성기 (별도 프로젝트)
- 스크립트 → TTS → B-roll 자동 삽입
- 10분+ 긴 영상 제작

---

## 설계 철학

### 1. 모듈화 (Plugin Architecture)
각 쇼츠 타입을 독립적인 플러그인으로 구현하여 확장 용이

### 2. 템플릿 기반
디자인과 로직을 분리하여 비개발자도 스타일 수정 가능

### 3. 선택적 의존성
- 기본: Python + FFmpeg + Pillow (최소 의존성)
- 선택: 나레이션(Cloud TTS), 자동 자막, BGM 비트 싱크 등

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  • CSV/JSON (구조화된 데이터)                                │
│  • Local Clips (사용자 클립)                                 │
│  • Parameters (style, aspect_ratio, bgm, narration)         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   SHORTS GENERATOR                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Data Parser & Validator                    │  │
│  │           (CSV/JSON → Structured Data)               │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Shorts Type Router                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │ Ranking  │  │Comparison│  │Before/   │  [+more] │  │
│  │  │Generator │  │Generator │  │After Gen │          │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘          │  │
│  └───────┼─────────────┼─────────────┼─────────────────┘  │
│          │             │             │                     │
│          └─────────────┼─────────────┘                     │
│                        ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Template Engine (Pillow)                   │  │
│  │   • Load Style Config                                │  │
│  │   • Render Text/Graphics                             │  │
│  │   • Generate Overlay PNGs                            │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Video Compositor (FFmpeg)                  │  │
│  │   • Clip Processing (resize, crop, blur)            │  │
│  │   • Overlay Composition                              │  │
│  │   • Transition Effects                               │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Audio Processor (Optional)                 │  │
│  │   • BGM Mixing                                       │  │
│  │   • Narration (Cloud TTS) - Optional                │  │
│  │   • Beat Sync - Optional                             │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Final Renderer (FFmpeg)                    │  │
│  │   • Concatenate Clips                                │  │
│  │   • Audio Mixing                                     │  │
│  │   • H.264 Encoding                                   │  │
│  └────────────────────┬─────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     OUTPUT LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  • MP4 Video (1080x1920 or 1920x1080)                      │
│  • Thumbnail (auto-generated)                               │
│  • Metadata (title, description) - Optional                │
│  • YouTube Upload - Optional                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 핵심 컴포넌트

### 1. Shorts Generator (추상 클래스)

**역할**: 모든 쇼츠 타입의 베이스 클래스

```python
from abc import ABC, abstractmethod
from typing import Dict, List

class ShortsGenerator(ABC):
    """쇼츠 생성기 베이스 클래스"""

    def __init__(self, style: str = "modern", aspect_ratio: str = "9:16"):
        self.style = style
        self.aspect_ratio = aspect_ratio
        self.template_engine = TemplateEngine(style)
        self.compositor = VideoCompositor()

    @abstractmethod
    def validate_input(self, data: Dict) -> bool:
        """입력 데이터 검증"""
        pass

    @abstractmethod
    def generate_overlays(self, data: Dict) -> List[str]:
        """오버레이 이미지 생성"""
        pass

    @abstractmethod
    def generate(self, data: Dict, output_dir: str) -> str:
        """영상 생성 (메인 로직)"""
        pass

    def add_bgm(self, video_path: str, bgm_path: str) -> str:
        """BGM 추가 (공통 기능)"""
        pass

    def add_narration(self, video_path: str, script: str) -> str:
        """나레이션 추가 (선택 기능)"""
        pass
```

---

### 2. Ranking Generator

**역할**: 랭킹형 쇼츠 생성

```python
class RankingShortsGenerator(ShortsGenerator):
    """랭킹형 쇼츠 생성기"""

    def validate_input(self, data: Dict) -> bool:
        """
        필수: rank, title, clip_path
        선택: emoji, score, description
        """
        required = ['rank', 'title', 'clip_path']
        return all(k in data for k in required)

    def generate_overlays(self, data: Dict) -> List[str]:
        """
        각 랭킹 항목마다 오버레이 생성
        - 순위 뱃지 (1, 2, 3... 금/은/동 구분)
        - 제목 텍스트 (반투명 박스)
        - 이모지 (우상단)
        - 점수 표시 (선택)
        """
        overlays = []
        for item in data['items']:
            overlay = self.template_engine.create_ranking_overlay(
                rank=item['rank'],
                title=item['title'],
                emoji=item.get('emoji', ''),
                score=item.get('score')
            )
            overlays.append(overlay)
        return overlays

    def generate(self, data: Dict, output_dir: str) -> str:
        """
        1. 오버레이 생성
        2. 각 클립 합성
        3. 전환 효과 추가
        4. 연결
        5. BGM 믹싱
        """
        # 구현...
        pass
```

**입력 예시**:
```csv
rank,title,clip_path,emoji,score,duration
1,웃긴 고양이,clips/cat1.mp4,😹,9.8,10
2,강아지 산책,clips/dog1.mp4,🐶,9.5,12
```

---

### 3. Comparison Generator (확장)

**역할**: A vs B 비교형 쇼츠 생성

```python
class ComparisonShortsGenerator(ShortsGenerator):
    """비교형 쇼츠 생성기"""

    def validate_input(self, data: Dict) -> bool:
        required = ['item_a', 'item_b', 'category']
        return all(k in data for k in required)

    def generate_overlays(self, data: Dict) -> List[str]:
        """
        좌우 분할 화면
        - 왼쪽: A 항목 + 라벨
        - 오른쪽: B 항목 + 라벨
        - 승자 강조 (테두리/반짝임)
        """
        pass

    def generate(self, data: Dict, output_dir: str) -> str:
        """
        화면을 좌우 분할하고 동시 재생
        승자 reveal 애니메이션
        """
        pass
```

**입력 예시**:
```csv
category,item_a,item_b,winner,clip_a,clip_b
카메라,iPhone 15,Galaxy S24,iPhone,clips/ip_cam.mp4,clips/gal_cam.mp4
배터리,iPhone 15,Galaxy S24,Galaxy,clips/ip_bat.mp4,clips/gal_bat.mp4
```

---

### 4. BeforeAfter Generator (확장)

**역할**: 전후 비교 쇼츠

```python
class BeforeAfterGenerator(ShortsGenerator):
    """전후 비교 쇼츠 생성기"""

    def validate_input(self, data: Dict) -> bool:
        required = ['title', 'before_clip', 'after_clip']
        return all(k in data for k in required)

    def generate_overlays(self, data: Dict) -> List[str]:
        """
        - "BEFORE" / "AFTER" 라벨
        - 전환 애니메이션 (슬라이드/와이프)
        """
        pass

    def generate(self, data: Dict, output_dir: str) -> str:
        """
        Before 클립 → 전환 → After 클립
        """
        pass
```

---

### 5. Template Engine

**역할**: 스타일별 디자인 렌더링

```python
class TemplateEngine:
    """템플릿 기반 그래픽 생성"""

    def __init__(self, style: str = "modern"):
        self.style = style
        self.config = self.load_config(style)
        self.load_assets()

    def load_config(self, style: str) -> Dict:
        """
        templates/{style}/config.yaml 로드
        - 색상, 폰트, 레이아웃 정보
        """
        with open(f"templates/{style}/config.yaml") as f:
            return yaml.safe_load(f)

    def load_assets(self):
        """
        templates/{style}/assets/ 이미지 로드
        - 배경, 프레임, 뱃지 등
        """
        pass

    def create_ranking_overlay(self, rank: int, title: str,
                               emoji: str = "", score: float = None) -> str:
        """
        랭킹 오버레이 생성 (Pillow)

        Returns:
            overlay_path: "output/overlays/overlay_{rank}.png"
        """
        canvas = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        # 순위 뱃지
        badge = self._render_badge(rank)
        canvas.paste(badge, self.config['layout']['badge_position'], badge)

        # 제목
        title_img = self._render_title(title)
        canvas.paste(title_img, self.config['layout']['title_position'], title_img)

        # 이모지
        if emoji:
            emoji_img = self._render_emoji(emoji)
            canvas.paste(emoji_img, self.config['layout']['emoji_position'], emoji_img)

        # 저장
        output_path = f"output/overlays/overlay_{rank}.png"
        canvas.save(output_path)
        return output_path

    def _render_badge(self, rank: int) -> Image:
        """금/은/동 뱃지 렌더링"""
        # 순위별 색상
        colors = {
            1: self.config['colors']['gold'],
            2: self.config['colors']['silver'],
            3: self.config['colors']['bronze']
        }
        color = colors.get(rank, self.config['colors']['primary'])

        # 원형 뱃지 생성
        badge = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
        draw = ImageDraw.Draw(badge)
        draw.ellipse([0, 0, 120, 120], fill=color)

        # 숫자
        font = ImageFont.truetype(self.config['fonts']['bold'], 60)
        bbox = draw.textbbox((0, 0), str(rank), font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text((60 - text_w//2, 60 - text_h//2), str(rank),
                  font=font, fill=(255, 255, 255))

        return badge
```

---

### 6. Video Compositor

**역할**: FFmpeg 기반 영상 합성

```python
class VideoCompositor:
    """FFmpeg 래퍼"""

    def compose_ranking_clip(self, clip_path: str, overlay_path: str,
                             output_path: str, duration: float = 10):
        """
        랭킹 클립 합성
        1. 클립 리사이즈 (9:16)
        2. 배경 블러 처리
        3. 오버레이 합성
        """
        cmd = f"""
        ffmpeg -i {clip_path} -i {overlay_path} -filter_complex "
          [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[scaled];
          [scaled]split[main][blur];
          [blur]gblur=sigma=50[blurred];
          color=c=black@0.3:s=1080x1920:d={duration}[vignette];
          [blurred][vignette]overlay=0:0[bg];
          [main]scale=900:1600:force_original_aspect_ratio=decrease[resized];
          [bg][resized]overlay=(W-w)/2:(H-h)/2[with_clip];
          [with_clip][1:v]overlay=0:0
        " -t {duration} -c:v libx264 -preset fast -crf 23 -r 30 {output_path}
        """
        subprocess.run(cmd, shell=True, check=True)

    def concatenate(self, clip_list: List[str], output_path: str,
                    transition: str = "crossfade"):
        """
        클립 연결 + 전환 효과
        """
        if transition == "crossfade":
            # xfade 필터 사용
            pass
        else:
            # concat 필터 사용
            concat_file = "output/concat.txt"
            with open(concat_file, 'w') as f:
                for clip in clip_list:
                    f.write(f"file '{clip}'\n")

            cmd = f"ffmpeg -f concat -safe 0 -i {concat_file} -c copy {output_path}"
            subprocess.run(cmd, shell=True, check=True)

    def add_bgm(self, video_path: str, bgm_path: str, output_path: str,
                bgm_volume: float = 0.3):
        """
        BGM 추가 (볼륨 조절)
        """
        cmd = f"""
        ffmpeg -i {video_path} -stream_loop -1 -i {bgm_path} -filter_complex "
          [1:a]volume={bgm_volume},aloop=loop=-1:size=2e+09[bgm];
          [bgm]atrim=duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {video_path})[bgm_trim]
        " -map 0:v -map [bgm_trim] -c:v copy -c:a aac -shortest {output_path}
        """
        subprocess.run(cmd, shell=True, check=True)
```

---

### 7. Audio Processor (선택)

**역할**: 나레이션, BGM 비트 싱크 등 고급 오디오 처리

```python
class AudioProcessor:
    """선택적 오디오 기능"""

    def generate_narration(self, script: str, voice: str = "ko-KR-Neural2-A") -> str:
        """
        Cloud TTS로 나레이션 생성

        Args:
            script: "1위는 웃긴 고양이입니다."
            voice: TTS 음성

        Returns:
            audio_path: "output/narration.mp3"
        """
        # Google Cloud TTS or Azure TTS
        pass

    def detect_beats(self, bgm_path: str) -> List[float]:
        """
        BGM에서 비트 타이밍 추출

        Returns:
            [0.5, 1.0, 1.5, ...] (초 단위)
        """
        # librosa 사용
        pass

    def align_cuts_to_beats(self, clip_durations: List[float],
                            beats: List[float]) -> List[float]:
        """
        클립 전환을 비트에 맞춤
        """
        pass
```

---

## 데이터 플로우

### 랭킹 쇼츠 생성 플로우

```
1. Input: ranking.csv
   [rank, title, clip_path, emoji, score, duration]
   ↓
2. Data Parser
   └─> 검증 & 구조화
   ↓
3. Shorts Type Router
   └─> RankingShortsGenerator 선택
   ↓
4. Template Engine (각 항목마다)
   └─> overlay_1.png, overlay_2.png, ...
   ↓
5. Video Compositor (각 항목마다)
   ├─> Clip 처리 (리사이즈, 블러 배경)
   ├─> Overlay 합성
   └─> clip_01.mp4, clip_02.mp4, ...
   ↓
6. Concatenate
   └─> ranking_raw.mp4
   ↓
7. Audio Processor (선택)
   ├─> BGM 추가 (기본)
   └─> Narration 추가 (선택)
   ↓
8. Final Output
   └─> final.mp4 (1080x1920, H.264)
   ↓
9. Post-processing (선택)
   ├─> Thumbnail 생성
   ├─> Metadata 생성
   └─> YouTube 업로드
```

---

## 파일 구조

```
video-auto-generator/
├── docs/
│   ├── ARCHITECTURE.md          # 이 문서
│   ├── shorts-spec.md           # 쇼츠 상세 스펙
│   ├── roadmap.md               # 구현 로드맵
│   └── tech-stack.md            # 기술 스택
│
├── src/
│   ├── core/                    # 공통 유틸
│   │   ├── ffmpeg_wrapper.py
│   │   ├── audio_processor.py
│   │   └── youtube_uploader.py
│   │
│   ├── shorts/                  # 쇼츠 생성기
│   │   ├── base.py             # ShortsGenerator 추상 클래스
│   │   ├── ranking.py          # RankingShortsGenerator
│   │   ├── comparison.py       # ComparisonShortsGenerator
│   │   ├── beforeafter.py      # BeforeAfterGenerator
│   │   ├── template_engine.py  # 템플릿 엔진
│   │   └── video_compositor.py # 영상 합성
│   │
│   ├── utils/
│   │   ├── data_parser.py      # CSV/JSON 파싱
│   │   ├── validator.py        # 입력 검증
│   │   └── logger.py           # 로깅
│   │
│   ├── api/                     # REST API (Phase 4)
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── tasks.py
│   │
│   └── cli/                     # CLI 도구
│       ├── generate.py         # 메인 CLI
│       └── config.py           # 설정
│
├── templates/                   # 템플릿 스타일
│   ├── ranking/
│   │   ├── modern/
│   │   │   ├── config.yaml     # 스타일 설정
│   │   │   └── assets/
│   │   │       ├── badge_bg.png
│   │   │       └── frame.png
│   │   ├── neon/
│   │   ├── minimal/
│   │   └── gradient/
│   │
│   ├── comparison/              # 비교형 템플릿
│   └── beforeafter/             # 전후형 템플릿
│
├── assets/
│   ├── fonts/
│   │   ├── NotoSansKR-Bold.ttf
│   │   └── NotoColorEmoji.ttf
│   ├── bgm/
│   │   └── upbeat.mp3
│   └── clips/                   # 사용자 클립
│
├── output/
│   ├── overlays/
│   ├── clips/
│   ├── videos/
│   └── logs/
│
├── tests/
│   ├── test_ranking_generator.py
│   ├── test_template_engine.py
│   └── test_compositor.py
│
├── config/
│   ├── api_keys.yaml           # API 키 (gitignore)
│   └── settings.yaml           # 전역 설정
│
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## 확장 가능성

### 1. 새로운 쇼츠 타입 추가

```python
# src/shorts/quiz.py (예시)
class QuizShortsGenerator(ShortsGenerator):
    """퀴즈형 쇼츠"""

    def validate_input(self, data: Dict) -> bool:
        required = ['question', 'options', 'answer']
        return all(k in data for k in required)

    def generate(self, data: Dict, output_dir: str) -> str:
        """
        질문 화면 → 옵션 화면 → 정답 reveal
        """
        pass
```

**사용**:
```bash
python -m src.cli.generate shorts quiz --input quiz.json
```

---

### 2. 새로운 템플릿 스타일 추가

```bash
# 1. 템플릿 폴더 생성
mkdir templates/ranking/cyberpunk

# 2. config.yaml 작성
templates/ranking/cyberpunk/config.yaml:
  name: "Cyberpunk"
  colors:
    primary: "#ff006e"
    secondary: "#8338ec"
  fonts:
    bold: "CyberpunkFont.ttf"
  layout:
    badge_position: [80, 100]

# 3. 사용
python -m src.cli.generate shorts ranking --input data.csv --style cyberpunk
```

---

### 3. 선택적 기능 활성화

```bash
# 기본 (BGM만)
python -m src.cli.generate shorts ranking --input data.csv

# 나레이션 추가
python -m src.cli.generate shorts ranking \
  --input data.csv \
  --narration auto \
  --voice ko-KR-Neural2-A

# BGM 비트 싱크
python -m src.cli.generate shorts ranking \
  --input data.csv \
  --bgm music.mp3 \
  --beat-sync

# 전부
python -m src.cli.generate shorts ranking \
  --input data.csv \
  --style neon \
  --narration auto \
  --bgm music.mp3 \
  --beat-sync \
  --upload
```

---

## 의존성 최소화

### 기본 의존성 (필수)
```
Python 3.10+
FFmpeg 6.0+
Pillow
pandas
```

### 선택적 의존성
```
# 나레이션
google-cloud-texttospeech  (Cloud TTS)

# BGM 비트 분석
librosa

# YouTube 업로드
google-api-python-client

# 웹 API
fastapi, celery, redis
```

---

## 성능 목표

| 항목 | 목표 |
|------|------|
| 10개 랭킹 클립 렌더링 | < 5분 (CPU) / < 2분 (GPU) |
| 메모리 사용 | < 4GB |
| 출력 파일 크기 | 60초 영상 < 50MB |
| 동시 작업 (웹) | 10+ (Celery workers) |

---

## 다음 단계

1. RankingShortsGenerator MVP 구현
2. Template Engine (Modern 스타일)
3. Video Compositor (FFmpeg 래퍼)
4. CLI 도구
5. 10개 샘플 영상 테스트
