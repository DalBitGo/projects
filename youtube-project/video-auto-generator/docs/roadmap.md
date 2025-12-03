# 구현 로드맵 v2

## 전체 타임라인 (수정됨)

```
Week 1-2:  MVP - 랭킹 쇼츠 생성기 (BGM only)
Week 3-4:  확장 - 템플릿 추가 & 선택적 기능
Week 5-6:  자동화 - YouTube 업로드 & 품질 개선
Week 7-8:  웹 UI (선택)
```

**핵심 변경**: Vrew 제거, 쇼츠 생성기에 집중

---

## Phase 1: MVP - 랭킹 쇼츠 생성기 (Week 1-2)

### 목표
CSV 입력 → 템플릿 합성 → BGM 믹싱 → MP4 출력

**의존성**: Python + FFmpeg + Pillow (최소)

---

### Week 1: 환경 & 템플릿

#### Day 1-2: 개발 환경
```bash
# 프로젝트 구조
mkdir -p src/{core,shorts,utils,cli}
mkdir -p templates/ranking/modern/{assets,}
mkdir -p assets/{fonts,bgm,clips}
mkdir -p output/{overlays,clips,videos,logs}

# 의존성
pip install pillow pandas pyyaml tqdm click
```

**검증**:
- FFmpeg 버전 확인: `ffmpeg -version`
- Python 패키지 import 테스트

---

#### Day 3-5: Modern 템플릿 디자인 (Canva)

**작업**:
1. 9:16 캔버스 생성
2. 레이어:
   - 순위 뱃지 (금/은/동/일반)
   - 프레임 (둥근 모서리)
   - 배경 그라데이션 (선택)
3. PNG export (투명 배경)

**선택**: 직접 Pillow로 생성 가능 (템플릿 불필요)

**시간**: 4-6시간

---

#### Day 6-7: TemplateEngine (Pillow)

**파일**: `src/shorts/template_engine.py`

**기능**:
- config.yaml 로드
- 뱃지 렌더링 (금/은/동)
- 텍스트 박스 (제목/설명)
- 이모지 합성

**코드 골격**:
```python
class TemplateEngine:
    def __init__(self, style: str = "modern"):
        self.config = self.load_config(f"templates/ranking/{style}/config.yaml")

    def create_overlay(self, rank, title, emoji, score) -> str:
        canvas = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
        # 뱃지, 텍스트, 이모지 렌더링
        canvas.save(f"output/overlays/overlay_{rank}.png")
        return ...
```

**시간**: 8-10시간

---

### Week 2: 영상 합성 & 배치 처리

#### Day 8-10: VideoCompositor (FFmpeg)

**파일**: `src/shorts/video_compositor.py`

**기능**:
- 클립 리사이즈 (9:16)
- 배경 블러
- 오버레이 합성
- 전환 효과
- BGM 추가

**시간**: 10-12시간

---

#### Day 11-12: BatchRenderer & CLI

**파일**:
- `src/shorts/ranking.py` (RankingShortsGenerator)
- `src/cli/generate.py`

**CLI**:
```bash
python -m src.cli.generate shorts ranking \
  --input data/ranking.csv \
  --bgm assets/bgm/upbeat.mp3
```

**시간**: 8-10시간

---

#### Day 13-14: 테스트 & 버그 수정

**작업**:
- 10개 샘플 클립 준비
- CSV 작성
- 전체 파이프라인 테스트
- 에러 처리 추가

**시간**: 8-10시간

---

## Phase 2: 확장 - 템플릿 & 선택적 기능 (Week 3-4)

### Week 3: 템플릿 확장

#### Day 15-17: 새 템플릿 스타일 (2-3개)

**추가 스타일**:
- Neon (네온 효과)
- Minimal (미니멀)
- Gradient (그라데이션)

**작업**:
- config.yaml 작성
- 색상/폰트/레이아웃 정의
- 테스트

**시간**: 8-10시간

---

#### Day 18-21: 쇼츠 타입 확장 (선택)

**새 타입**:
- ComparisonGenerator (A vs B)
- BeforeAfterGenerator (전후 비교)

**base.py** (추상 클래스):
```python
class ShortsGenerator(ABC):
    @abstractmethod
    def validate_input(self, data: Dict) -> bool:
        pass

    @abstractmethod
    def generate(self, data: Dict, output_dir: str) -> str:
        pass
```

**시간**: 10-12시간

---

### Week 4: 선택적 기능

#### Day 22-24: 나레이션 (Cloud TTS)

**파일**: `src/core/audio_processor.py`

**기능**:
- 스크립트 자동 생성
- Google Cloud TTS 연동
- BGM ducking

**시간**: 8-10시간

---

#### Day 25-28: BGM 비트 싱크 (librosa)

**기능**:
- 비트 검출
- 클립 전환 타이밍 조정

**시간**: 8-10시간

---

## Phase 3: 자동화 & 품질 (Week 5-6)

### Week 5: YouTube 업로드

#### Day 29-32: YouTube API 통합

**파일**: `src/core/youtube_uploader.py`

**기능**:
- OAuth 인증
- 영상 업로드
- 메타데이터 설정
- 썸네일 업로드

**시간**: 10-12시간

---

#### Day 33-35: 썸네일 자동 생성

**기능**:
- 최적 프레임 캡처
- 텍스트 오버레이

**시간**: 6-8시간

---

### Week 6: 품질 개선

#### Day 36-38: 고급 전환 효과

**기능**:
- xfade 필터 체인
- 다양한 전환 타입 (slide, wipe, etc.)

**시간**: 8-10시간

---

#### Day 39-42: 테스트 & 문서화

**작업**:
- 통합 테스트
- 에러 처리 강화
- 문서 업데이트

**시간**: 10-12시간

---

## Phase 4: 웹 UI (Week 7-8, 선택)

### Week 7: FastAPI 백엔드

#### Day 43-46: REST API

**엔드포인트**:
```python
POST /api/shorts/render
GET  /api/tasks/{task_id}
POST /api/upload/csv
```

**시간**: 10-12시간

---

#### Day 47-49: Celery Worker

**기능**:
- 비동기 렌더링
- 진행률 업데이트

**시간**: 8-10시간

---

### Week 8: Next.js 프론트엔드

#### Day 50-54: 웹 UI

**페이지**:
1. CSV 업로드
2. 스타일 선택
3. 진행률 표시
4. 결과 다운로드

**시간**: 12-15시간

---

#### Day 55-56: 배포

**작업**:
- Docker 이미지
- docker-compose
- 배포 (AWS/GCP)

**시간**: 8-10시간

---

## 총 예상 시간 (수정)

| Phase | 작업 | 시간 |
|-------|-----|------|
| **Phase 1** | 랭킹 쇼츠 MVP (BGM only) | 40-50시간 |
| **Phase 2** | 템플릿 & 선택 기능 | 35-45시간 |
| **Phase 3** | YouTube & 품질 | 35-45시간 |
| **Phase 4** | 웹 UI (선택) | 40-50시간 |
| **총계 (MVP)** | Phase 1만 | **40-50시간** |
| **총계 (Full)** | Phase 1-3 | **110-140시간** |
| **총계 (웹 포함)** | Phase 1-4 | **150-190시간** |

**1인 개발**:
- MVP만: 1-1.5주 (풀타임)
- Full: 3-4주 (풀타임)
- 웹 포함: 4-5주 (풀타임)

---

## 마일스톤

### M1: MVP (Week 2)
- CSV → 영상 생성 가능
- BGM 믹싱
- CLI 도구 작동
- 10개 샘플 성공

### M2: 확장 (Week 4)
- 3개 템플릿 스타일
- 나레이션 선택 기능 (TTS)
- BGM 비트 싱크

### M3: 자동화 (Week 6)
- YouTube 자동 업로드
- 썸네일 자동 생성
- 고급 전환 효과

### M4: 웹 서비스 (Week 8, 선택)
- REST API
- 웹 UI
- 배포

---

## 핵심 변경 사항 (v1 대비)

❌ **제거됨**:
- Vrew 통합 (일반 영상 생성은 별도 프로젝트)
- Scene Analyzer
- Asset Fetcher (Pexels/Pixabay)
- Timeline Builder

✅ **유지/추가**:
- 랭킹 쇼츠 생성기 (핵심)
- 템플릿 시스템
- 플러그인 구조 (확장 가능)
- 선택적 나레이션 (Cloud TTS)

🎯 **프로젝트 범위 명확화**:
- Phase 1: 쇼츠 생성기 (랭킹, 비교, 전후)
- Phase 2 (추후): 일반 영상 생성기 (별도 프로젝트)

---

## 다음 액션

1. Day 1-2: 환경 세팅
2. Day 3-5: 템플릿 디자인 or Pillow 직접 생성
3. Day 6-7: TemplateEngine 구현
4. Day 8-10: VideoCompositor 구현
5. Day 11-12: CLI 도구 & 통합
6. Day 13-14: 테스트
