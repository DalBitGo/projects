# 개발 환경 세팅 가이드

## 필수 요구사항

### 1. Python 3.10+
```bash
python --version  # 3.10 이상 확인
```

### 2. FFmpeg 6.0+
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg

# 확인
ffmpeg -version
```

---

## 설치 방법

### 1. 프로젝트 클론
```bash
cd youtube-project/video-auto-generator
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv

# 활성화
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

---

## 폰트 설치 (한글 지원)

### Noto Sans KR
```bash
# Ubuntu/Debian
sudo apt install fonts-noto-cjk

# macOS
brew tap homebrew/cask-fonts
brew install font-noto-sans-cjk-kr

# 수동 설치
# 1. https://fonts.google.com/noto/specimen/Noto+Sans+KR 다운로드
# 2. assets/fonts/에 복사
```

폰트 파일 경로:
```
assets/fonts/
├── NotoSansKR-Bold.ttf
├── NotoSansKR-Regular.ttf
└── NotoColorEmoji.ttf (선택)
```

---

## 샘플 클립 준비

테스트용 샘플 영상 필요:
```
assets/clips/
├── sample1.mp4  (10초, 720p 이상)
├── sample2.mp4
└── sample3.mp4
```

**샘플 영상 생성 (FFmpeg)**:
```bash
# 색상 테스트 영상 생성 (10초)
ffmpeg -f lavfi -i testsrc=duration=10:size=1920x1080:rate=30 \
  -pix_fmt yuv420p assets/clips/sample1.mp4

ffmpeg -f lavfi -i testsrc=duration=10:size=1920x1080:rate=30 \
  -vf "hue=s=0" -pix_fmt yuv420p assets/clips/sample2.mp4

ffmpeg -f lavfi -i rgbtestsrc=duration=10:size=1920x1080:rate=30 \
  -pix_fmt yuv420p assets/clips/sample3.mp4
```

---

## BGM 준비 (선택)

```bash
# 무료 BGM 다운로드 (예시)
# - YouTube Audio Library
# - Epidemic Sound
# - Artlist

# 저장 위치
assets/bgm/upbeat.mp3
```

---

## 테스트

### 1. TemplateEngine 테스트
```bash
python src/shorts/template_engine.py
# → output/overlays/overlay_01.png 생성 확인
```

### 2. CLI 테스트
```bash
python src/cli/generate.py shorts ranking \
  --input data/sample_ranking.csv \
  --output output/test
```

---

## 문제 해결

### FFmpeg not found
```bash
# 환경변수 확인
which ffmpeg  # Linux/macOS
where ffmpeg  # Windows

# PATH에 추가 필요 시
export PATH="/usr/local/bin:$PATH"
```

### 폰트 로드 실패
```bash
# 폰트 경로 확인
ls assets/fonts/

# config.yaml 경로 수정
# templates/ranking/modern/config.yaml
```

### Pillow 설치 오류
```bash
# 시스템 라이브러리 설치
sudo apt install libjpeg-dev zlib1g-dev  # Ubuntu
brew install jpeg zlib  # macOS
```

---

## 다음 단계

1. **샘플 영상 생성**: [테스트 실행](README_SETUP.md#테스트)
2. **자체 데이터 준비**: CSV 작성 + 클립 준비
3. **첫 쇼츠 생성**: CLI 실행
4. **결과 확인**: `output/videos/final.mp4`

---

## 추가 옵션 (선택)

### Cloud TTS (나레이션)
```bash
# Google Cloud SDK 설치
# https://cloud.google.com/sdk/docs/install

# 인증
gcloud auth application-default login

# 의존성 설치
pip install google-cloud-texttospeech
```

### YouTube 업로드
```bash
# OAuth 설정
# 1. Google Cloud Console에서 OAuth 클라이언트 생성
# 2. credentials.json 다운로드

pip install google-api-python-client google-auth-oauthlib
```

---

문제가 있으면 GitHub Issues에 보고해주세요!
