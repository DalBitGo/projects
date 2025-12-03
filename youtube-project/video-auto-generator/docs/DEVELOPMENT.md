# 개발 과정 상세 문서

## 프로젝트 개요

YouTube 쇼츠 랭킹 영상 자동 생성기 v0.1.0 MVP 개발

**기간**: 2024-01-24 (Day 1)
**목표**: CSV → 랭킹 쇼츠 영상 자동 생성 (BGM + 텍스트 오버레이)
**기술 스택**: Python + FFmpeg + Pillow

---

## 개발 단계

### Phase 1: 프로젝트 구조 생성

#### 디렉토리 구조
```bash
mkdir -p src/{core,shorts,utils,cli}
mkdir -p templates/ranking/modern
mkdir -p assets/{fonts,bgm,clips}
mkdir -p output/{overlays,clips,videos,logs}
mkdir -p tests config data
```

**생성된 구조**:
```
video-auto-generator/
├── src/
│   ├── core/          # 공통 유틸 (추후)
│   ├── shorts/        # 쇼츠 생성기
│   ├── utils/         # 헬퍼 함수
│   └── cli/           # CLI 도구
├── templates/
│   └── ranking/modern/  # Modern 템플릿
├── assets/
│   ├── fonts/         # 폰트 파일
│   ├── bgm/           # 배경음악
│   └── clips/         # 소스 클립
├── output/            # 생성된 파일
├── data/              # 샘플 데이터
└── docs/              # 문서
```

---

### Phase 2: 의존성 관리

#### requirements.txt
```txt
pillow>=10.2.0      # 이미지 처리
pandas>=2.1.4       # CSV 데이터
pyyaml>=6.0.1       # 설정 파일
tqdm>=4.66.1        # 진행률 표시
click>=8.1.7        # CLI 프레임워크
```

**설계 결정**:
- 최소 의존성 유지 (5개 패키지만)
- 선택적 기능은 주석 처리 (TTS, YouTube 등)
- 버전 명시로 호환성 보장

---

### Phase 3: 템플릿 시스템

#### config.yaml 설계

**파일**: `templates/ranking/modern/config.yaml`

**주요 섹션**:
1. **colors**: 색상 팔레트 (금/은/동/일반)
2. **fonts**: 폰트 경로
3. **layout**: 각 요소 위치
4. **sizes**: 요소 크기
5. **effects**: 시각 효과
6. **animations**: 애니메이션 설정

**설계 이유**:
- YAML로 비개발자도 수정 가능
- 새 스타일 추가 시 코드 수정 불필요
- 레이아웃 조정 용이

**예시 값**:
```yaml
colors:
  gold: "#FFD700"     # 1위 (금메달 색)
  silver: "#C0C0C0"   # 2위 (은메달 색)
  bronze: "#CD7F32"   # 3위 (동메달 색)
  primary: "#667eea"  # 4위 이하 (보라색)

layout:
  badge_position: [60, 80]      # 좌상단
  emoji_position: [920, 80]     # 우상단
  title_position: [540, 1650]   # 하단 중앙
```

---

### Phase 4: TemplateEngine 구현

#### 클래스 설계

**파일**: `src/shorts/template_engine.py`

**핵심 메서드**:
1. `__init__(style, aspect_ratio)`: 초기화 & 설정 로드
2. `create_overlay()`: 오버레이 이미지 생성 (메인)
3. `_create_badge()`: 순위 뱃지 렌더링
4. `_render_emoji()`: 이모지 렌더링
5. `_draw_score()`: 점수 표시
6. `_create_title_box()`: 제목 박스 생성

**구현 세부사항**:

##### 1. 캔버스 생성
```python
canvas = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
draw = ImageDraw.Draw(canvas)
```
- RGBA 모드 (투명도 지원)
- 9:16 세로 화면 (1080x1920)

##### 2. 순위 뱃지
```python
def _create_badge(self, rank: int):
    # 순위별 색상 결정
    if rank == 1:
        color = colors['gold']
    elif rank == 2:
        color = colors['silver']
    elif rank == 3:
        color = colors['bronze']
    else:
        color = colors['primary']

    # 원형 뱃지
    draw.ellipse([0, 0, size, size], fill=color)

    # 숫자 중앙 정렬
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_pos = ((size - text_w) // 2, (size - text_h) // 2)
```

**핵심 기법**:
- `textbbox()`로 텍스트 크기 계산
- 중앙 정렬을 위한 offset 계산

##### 3. 제목 박스
```python
def _create_title_box(self, title, description):
    # 반투명 박스 (검정, 투명도 180/255)
    draw.rounded_rectangle(
        box_coords,
        radius=20,
        fill=(0, 0, 0, 180)
    )

    # 제목 텍스트 (중앙 정렬)
    draw.text((center_x, 30), title,
             font=font_title,
             fill=(255, 255, 255),
             anchor="mt")  # middle-top
```

**고려사항**:
- 폰트 로드 실패 시 `ImageFont.load_default()` 대체
- 이모지 폰트 없어도 동작하도록 예외 처리
- 긴 제목 자동 줄바꿈 (추후 개선 필요)

---

### Phase 5: VideoCompositor 구현

#### FFmpeg 래퍼 설계

**파일**: `src/shorts/video_compositor.py`

**핵심 메서드**:
1. `compose_clip()`: 단일 클립 합성
2. `concatenate_clips()`: 여러 클립 연결
3. `add_bgm()`: BGM 추가

**구현 세부사항**:

##### 1. 클립 합성 필터 체인
```bash
# 필터 체인 구조
[0:v]scale=1080:1920:...,crop=1080:1920[scaled]
  ↓
[scaled]split[main][blur]
  ↓                  ↓
[main]            [blur]gblur=sigma=50[blurred]
  ↓                  ↓
[resized]      [blurred]+[vignette]overlay[bg]
  ↓                  ↓
  └─────[bg][resized]overlay[with_clip]
                     ↓
              [with_clip][overlay]overlay
                     ↓
              fade in/out
```

**단계별 설명**:
1. **Scale & Crop**: 원본 클립을 9:16으로 리사이즈 & 크롭
2. **Split**: 메인/블러용 2개 스트림 생성
3. **Blur Background**: 배경용 블러 처리 (sigma=50)
4. **Vignette**: 어두운 비네팅 오버레이
5. **Main Clip**: 중앙에 작은 크기로 배치 (900x1600)
6. **Overlay**: 텍스트/그래픽 오버레이
7. **Fade**: 페이드 인/아웃 (0.5초/0.3초)

##### 2. BGM 추가
```python
def add_bgm(self, video_path, bgm_path, output_path, volume=0.3):
    # 1. 영상 길이 추출
    duration = get_video_duration(video_path)

    # 2. BGM 처리
    # - 무한 반복 (-stream_loop -1)
    # - 볼륨 조절 (volume={volume})
    # - 페이드 인/아웃 (2초)
    # - 영상 길이만큼 자르기 (atrim)

    cmd = f"""
    ffmpeg -y -i {video_path} -stream_loop -1 -i {bgm_path}
    -filter_complex "
      [1:a]volume={volume},
      afade=t=in:st=0:d=2,
      afade=t=out:st={duration-2}:d=2,
      atrim=duration={duration}[bgm]
    "
    -map 0:v -map [bgm] -c:v copy -c:a aac -shortest {output_path}
    """
```

**최적화 팁**:
- `-preset fast`: 인코딩 속도 우선
- `-crf 23`: 품질 (낮을수록 고품질, 18-28 권장)
- `-c:v copy`: BGM 추가 시 비디오 재인코딩 없음

---

### Phase 6: RankingShortsGenerator 통합

#### 전체 파이프라인 구현

**파일**: `src/shorts/ranking.py`

**워크플로우**:
```python
def generate_from_csv(csv_path, output_dir, bgm_path):
    # 1. CSV 읽기
    df = pd.read_csv(csv_path)

    # 2. 각 항목 처리 (루프)
    for idx, row in tqdm(df.iterrows()):
        # 2.1 오버레이 생성
        overlay = template_engine.create_overlay(
            rank=row['rank'],
            title=row['title'],
            ...
        )

        # 2.2 클립 합성
        compositor.compose_clip(
            clip_path=row['clip_path'],
            overlay_path=overlay,
            output_path=f"clip_{rank:02d}.mp4",
            duration=row.get('duration', 10)
        )

    # 3. 클립 연결
    compositor.concatenate_clips(clip_list, "ranking_raw.mp4")

    # 4. BGM 추가 (선택)
    if bgm_path:
        compositor.add_bgm("ranking_raw.mp4", bgm_path, "final.mp4")
```

**데이터 흐름**:
```
CSV 파일
  ↓
Pandas DataFrame
  ↓
각 행 반복
  ├─> TemplateEngine.create_overlay() → overlay.png
  └─> VideoCompositor.compose_clip() → clip_XX.mp4
  ↓
[clip_01.mp4, clip_02.mp4, ...] 리스트
  ↓
VideoCompositor.concatenate_clips() → ranking_raw.mp4
  ↓
VideoCompositor.add_bgm() → final.mp4 (완성!)
```

**예외 처리**:
- CSV 필수 컬럼 검증
- 클립 파일 존재 여부 확인
- FFmpeg 오류 캐치 & 사용자 친화적 메시지

---

### Phase 7: CLI 도구 구현

#### Click 기반 CLI

**파일**: `src/cli/generate.py`

**명령어 구조**:
```bash
python -m src.cli.generate [COMMAND] [SUBCOMMAND] [OPTIONS]

# 예시
python -m src.cli.generate shorts ranking --input data.csv
```

**주요 옵션**:
- `--input, -i`: CSV 파일 경로 (필수)
- `--output, -o`: 출력 디렉토리 (기본: output/videos)
- `--style, -s`: 템플릿 스타일 (기본: modern)
- `--aspect, -a`: 화면 비율 (9:16 or 16:9)
- `--bgm, -b`: BGM 파일 경로 (선택)
- `--bgm-volume`: BGM 볼륨 (0.0-1.0, 기본: 0.3)

**사용 예시**:
```bash
# 기본 사용
python -m src.cli.generate shorts ranking -i data/ranking.csv

# 고급 옵션
python -m src.cli.generate shorts ranking \
  -i data/ranking.csv \
  -o output/my_shorts \
  -s modern \
  -a 9:16 \
  -b assets/bgm/upbeat.mp3 \
  --bgm-volume 0.2
```

**진행률 표시**:
```
🎬 Ranking Shorts Generator
Style: modern, Aspect: 9:16
Input: data/ranking.csv

📊 Loaded 3 items from CSV

Processing items: 100%|████████████| 3/3 [00:15<00:00,  5.2s/it]
✓ Composed: clip_01.mp4
✓ Composed: clip_02.mp4
✓ Composed: clip_03.mp4

✓ Created 3 clips

🔗 Concatenating clips...
✓ Concatenated 3 clips

🎵 Adding BGM: upbeat.mp3...
✓ Added BGM: final.mp4

✅ Done! Output: output/videos/final.mp4
```

---

## 핵심 기술 결정

### 1. 최소 의존성 전략

**채택 이유**:
- 설치/배포 간소화
- 충돌 위험 최소화
- 학습 곡선 완만

**대안 고려**:
- ❌ MoviePy: 느리고 메모리 많이 사용
- ✅ FFmpeg 직접 사용: 빠르고 강력

### 2. 템플릿 기반 설계

**장점**:
- 코드 수정 없이 디자인 변경
- 다양한 스타일 쉽게 추가
- 비개발자도 커스터마이징 가능

**단점**:
- 초기 설정 복잡
- 극단적인 레이아웃은 코드 수정 필요

### 3. FFmpeg 커맨드라인 사용

**장점**:
- 최고 성능
- 하드웨어 가속 지원
- 표준 도구

**단점**:
- 복잡한 필터 체인 학습 필요
- 디버깅 어려움

**해결책**:
- 자주 쓰는 패턴 래퍼 함수로 추상화
- 에러 메시지 개선

---

## 성능 최적화

### 1. 병렬 처리 (추후 개선)

현재:
```python
for item in items:
    create_overlay(item)
    compose_clip(item)
```

개선안:
```python
from multiprocessing import Pool

with Pool(4) as pool:
    pool.map(process_item, items)
```

**예상 효과**: 4배 속도 향상 (4코어 기준)

### 2. FFmpeg 하드웨어 가속

```bash
# NVIDIA GPU (NVENC)
-hwaccel cuda -c:v h264_cuvid ... -c:v h264_nvenc

# Intel QSV
-hwaccel qsv -c:v h264_qsv

# Apple Silicon
-hwaccel videotoolbox -c:v h264_videotoolbox
```

**예상 효과**: 2-5배 속도 향상

### 3. 프리셋 최적화

| 프리셋 | 속도 | 품질 | 파일 크기 |
|--------|------|------|----------|
| ultrafast | ⚡⚡⚡⚡⚡ | ⭐ | 큼 |
| fast | ⚡⚡⚡⚡ | ⭐⭐⭐ | 중간 |
| medium | ⚡⚡⚡ | ⭐⭐⭐⭐ | 중간 |
| slow | ⚡⚡ | ⭐⭐⭐⭐⭐ | 작음 |

**현재 설정**: `fast` (균형)

---

## 테스트 전략

### 1. 단위 테스트
```bash
# TemplateEngine 테스트
python src/shorts/template_engine.py

# VideoCompositor 테스트
python src/shorts/video_compositor.py
```

### 2. 통합 테스트
```bash
# 샘플 데이터로 전체 파이프라인 테스트
python src/cli/generate.py shorts ranking \
  -i data/sample_ranking.csv \
  -o output/test
```

### 3. 검증 항목
- [ ] 오버레이 이미지 정상 생성
- [ ] 텍스트 정렬 정확
- [ ] 클립 합성 오류 없음
- [ ] BGM 싱크 정확
- [ ] 최종 파일 재생 가능

---

## 문제 해결 로그

### 문제 1: 한글 폰트 렌더링 실패
**증상**: 한글이 □□□로 표시
**원인**: Noto Sans KR 폰트 미설치
**해결**: 폰트 설치 가이드 추가 (README_SETUP.md)

### 문제 2: FFmpeg 필터 체인 복잡도
**증상**: 긴 필터 체인 가독성 저하
**원인**: 여러 필터를 한 줄에 작성
**해결**: `.replace('\n', '').replace(' ', '')` 패턴 사용

### 문제 3: 이모지 렌더링
**증상**: 일부 시스템에서 이모지 깨짐
**원인**: Noto Color Emoji 폰트 부재
**해결**: 선택적 기능으로 변경, 폰트 없어도 동작

---

## 다음 단계 (Phase 2+)

### Week 3-4: 기능 확장
- [ ] Neon/Minimal 템플릿 추가
- [ ] 비교형 쇼츠 생성기
- [ ] Cloud TTS 나레이션 (선택)
- [ ] BGM 비트 싱크

### Week 5-6: 자동화
- [ ] YouTube API 업로드
- [ ] 썸네일 자동 생성
- [ ] 고급 전환 효과 (xfade 완전 구현)

### Week 7-8: 웹 UI (선택)
- [ ] FastAPI REST API
- [ ] Celery 백그라운드 작업
- [ ] Next.js 프론트엔드
- [ ] Docker 배포

---

## 참고 자료

### FFmpeg
- [공식 문서](https://ffmpeg.org/documentation.html)
- [필터 가이드](https://ffmpeg.org/ffmpeg-filters.html)
- [Xfade 전환](https://trac.ffmpeg.org/wiki/Xfade)

### Pillow
- [공식 문서](https://pillow.readthedocs.io/)
- [ImageDraw 레퍼런스](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html)

### Click
- [공식 문서](https://click.palletsprojects.com/)

---

## 프로젝트 통계

- **총 라인 수**: ~800 줄
- **파일 수**: 12개 (Python 코드)
- **의존성**: 5개 패키지
- **개발 시간**: ~8시간 (MVP)
- **예상 렌더링 시간**: 10개 클립 < 5분 (CPU)

---

**작성일**: 2024-01-24
**작성자**: Development Team
**버전**: v0.1.0
