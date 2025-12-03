# YouTube 쇼츠 자동 생성기

CSV 데이터 입력부터 영상 합성, BGM 믹싱, 업로드까지 완전 자동화

## 주요 기능

### 🎬 쇼츠 생성기 (Phase 1)
- **랭킹형**: Top 10, 베스트 5 등 순위 기반 컨텐츠
- **비교형** (확장): A vs B 비교
- **전후형** (확장): Before & After
- **커스터마이징**: 템플릿 스타일, BGM, 나레이션(선택)
- **자동 업로드**: YouTube API 연동

### 🔮 일반 영상 생성기 (Phase 2, 추후)
스크립트 → TTS → B-roll 자동 삽입 (별도 프로젝트)

---

## 프로젝트 구조

```
video-auto-generator/
├── docs/                        # 📚 설계 문서
│   ├── ARCHITECTURE.md          # 전체 아키텍처 (v2)
│   ├── shorts-spec.md           # 쇼츠 상세 스펙 (v2)
│   ├── roadmap.md               # 구현 로드맵 (v2)
│   ├── tech-stack.md            # 기술 스택 상세
│   └── project-discussion.md    # 초기 논의
│
├── src/ (예정)                 # 💻 소스 코드
│   ├── core/                    # 공통 유틸
│   ├── shorts/                  # 쇼츠 생성기
│   │   ├── base.py             # 추상 클래스
│   │   ├── ranking.py          # 랭킹 타입
│   │   ├── comparison.py       # 비교 타입 (확장)
│   │   ├── template_engine.py  # 템플릿 엔진
│   │   └── video_compositor.py # FFmpeg 래퍼
│   ├── utils/
│   └── cli/                     # CLI 도구
│
├── templates/ (예정)            # 🎨 디자인 템플릿
│   └── ranking/
│       ├── modern/
│       ├── neon/
│       └── minimal/
│
├── assets/ (예정)               # 📦 리소스
│   ├── fonts/
│   ├── bgm/
│   └── clips/
│
└── output/ (예정)               # 📹 출력물
```

---

## 기술 스택

### 코어 (필수)
- **Python 3.10+**: 백엔드 & 미디어 처리
- **FFmpeg 6.0+**: 영상 합성/편집
- **Pillow**: 템플릿/이미지 생성
- **Pandas**: CSV 데이터 처리

### 선택적 기능
- **Google Cloud TTS**: 나레이션 (선택)
- **librosa**: BGM 비트 싱크 (선택)
- **YouTube Data API**: 자동 업로드 (선택)
- **FastAPI + Celery**: 웹 API (Phase 4)

---

## 비용 예상

| 방식 | 월 비용 | 비고 |
|------|---------|------|
| **로컬 기본** | **$0** | Python + FFmpeg + Pillow만 |
| 나레이션 추가 | $0-16 | Cloud TTS 사용량에 따라 |
| 웹 서버 | $30-60 | AWS/GCP 배포 시 |

**추천**: 로컬에서 무료로 시작

---

## 구현 로드맵

### MVP (1-2주)
- CSV → 랭킹 쇼츠 생성
- BGM 믹싱
- CLI 도구
- **의존성**: Python + FFmpeg + Pillow

### Phase 2 (3-4주)
- 3개 템플릿 스타일
- 나레이션 (Cloud TTS, 선택)
- BGM 비트 싱크
- 쇼츠 타입 확장 (비교, 전후)

### Phase 3 (5-6주)
- YouTube 자동 업로드
- 썸네일 자동 생성
- 고급 전환 효과

### Phase 4 (7-8주, 선택)
- REST API (FastAPI)
- 웹 UI (Next.js)
- 배포

**예상 소요 시간**:
- MVP만: 40-50시간 (1-1.5주 풀타임)
- Full (Phase 1-3): 110-140시간 (3-4주 풀타임)

---

## 빠른 시작 (예정)

### 환경 세팅
```bash
# Python 3.10+ 확인
python --version

# FFmpeg 설치
# Ubuntu: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: choco install ffmpeg

# 프로젝트 클론 (추후)
# git clone ...

# 의존성 설치
pip install pillow pandas pyyaml tqdm click
```

### 기본 사용법
```bash
# CSV 준비
# rank,title,clip_path,emoji,score
# 1,웃긴 고양이,clips/cat1.mp4,😹,9.8

# 영상 생성
python -m src.cli.generate shorts ranking \
  --input data/ranking.csv \
  --bgm assets/bgm/upbeat.mp3 \
  --output output/videos

# 출력: output/videos/final.mp4
```

### 고급 옵션
```bash
# 스타일 선택
--style neon

# 나레이션 추가 (선택, Cloud TTS 필요)
--narration auto --voice ko-KR-Neural2-A

# YouTube 업로드 (선택)
--upload --title "🔥 TOP 10" --privacy public
```

---

## 문서

| 문서 | 내용 |
|------|------|
| [**ARCHITECTURE.md**](ARCHITECTURE.md) | 전체 시스템 아키텍처 v2 |
| [**shorts-spec.md**](docs/shorts-spec.md) | 랭킹 쇼츠 상세 스펙 v2 |
| [**roadmap.md**](docs/roadmap.md) | 구현 로드맵 v2 (Day-by-Day) |
| [**tech-stack.md**](docs/tech-stack.md) | 기술 스택 상세 가이드 |
| [**project-discussion.md**](project-discussion.md) | 초기 논의 정리 |

---

## 현재 상태

✅ **완료 (v2)**
- 프로젝트 재설계 (쇼츠 생성기 집중)
- 모듈화/플러그인 구조 설계
- Vrew 의존성 제거 (선택적 기능으로)
- 최소 의존성 확정 (Python + FFmpeg + Pillow)
- 문서 업데이트

🚧 **진행 중**
- 개발 환경 세팅 (예정)
- 템플릿 디자인 (예정)

📅 **예정**
- Week 1-2: MVP 구현 (랭킹 쇼츠)
- Week 3-4: 템플릿 & 확장
- Week 5-6: YouTube 자동화

---

## 설계 철학

### 1. 모듈화 (Plugin Architecture)
각 쇼츠 타입을 독립적인 플러그인으로 구현
```python
class ShortsGenerator(ABC):
    @abstractmethod
    def generate(self, data: Dict, output_dir: str) -> str:
        pass

# 쉽게 추가 가능
class QuizShortsGenerator(ShortsGenerator):
    def generate(self, data: Dict, output_dir: str) -> str:
        # 퀴즈형 로직
        pass
```

### 2. 템플릿 기반
디자인과 로직 분리, 비개발자도 수정 가능
```yaml
# templates/ranking/modern/config.yaml
colors:
  gold: "#FFD700"
  primary: "#667eea"
fonts:
  bold: "NotoSansKR-Bold.ttf"
```

### 3. 선택적 의존성
- 기본: BGM + 텍스트 오버레이
- 선택: 나레이션, 비트 싱크, 자동 업로드

---

## 확장 가능성

### 새 쇼츠 타입 추가
```bash
# 1. Generator 클래스 작성
# src/shorts/quiz.py

# 2. CLI에 등록
python -m src.cli.generate shorts quiz --input quiz.json
```

### 새 템플릿 스타일 추가
```bash
# 1. 폴더 생성
mkdir templates/ranking/cyberpunk

# 2. config.yaml 작성
# 3. 사용
--style cyberpunk
```

---

## 라이선스 & 저작권

### 프로젝트
MIT License (예정)

### 사용 라이브러리
- Python 패키지: 각 라이선스 준수
- FFmpeg: LGPL/GPL

### BGM & 클립
- 사용자 책임으로 라이선스 준수
- 출처 표기 권장

---

## 기여

현재 1인 개발 프로젝트

---

## 다음 단계

1. **Day 1-2**: 환경 세팅, 프로젝트 구조 생성
2. **Day 3-7**: TemplateEngine 구현 (Pillow)
3. **Day 8-12**: VideoCompositor (FFmpeg) + CLI
4. **Day 13-14**: 테스트 & 버그 수정
5. **Week 3+**: 템플릿 확장 & 선택 기능

---

**Made for YouTube Creators 🎥**
