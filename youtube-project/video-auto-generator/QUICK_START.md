# 빠른 시작 가이드

## 1️⃣ 생성된 비디오 확인

### 테스트로 생성된 비디오들
```bash
# 기본 테스트
output/integration_test/test1_basic/ranking_raw.mp4

# 에지 케이스 (긴 제목, 특수문자)
output/integration_test/test2_edge_cases/ranking_raw.mp4

# 커스텀 템플릿
output/integration_test/test3_custom_template/ranking_raw.mp4

# 폴더 모드
output/integration_test/test4_folder_mode/ranking_raw.mp4

# AI 제목 생성 테스트
output/ai_title_test/ranking_raw.mp4
```

### 비디오 재생
```bash
# Windows (WSL)
explorer.exe output/integration_test/test1_basic/ranking_raw.mp4

# Linux
vlc output/integration_test/test1_basic/ranking_raw.mp4
# 또는
mpv output/integration_test/test1_basic/ranking_raw.mp4

# macOS
open output/integration_test/test1_basic/ranking_raw.mp4
```

---

## 2️⃣ 템플릿 미리보기 확인

### 새 템플릿 미리보기 이미지
```bash
# Neon 스타일
output/template_previews/neon_preview.png

# Bubble 스타일
output/template_previews/bubble_preview.png

# Retro 스타일
output/template_previews/retro_preview.png
```

### 이미지 열기
```bash
# Windows (WSL)
explorer.exe output/template_previews/

# Linux
eog output/template_previews/neon_preview.png

# macOS
open output/template_previews/
```

---

## 3️⃣ 템플릿 에디터 실행 (GUI)

### Streamlit 템플릿 에디터
```bash
streamlit run template_editor_app.py
```

브라우저에서 자동으로 열림 (보통 http://localhost:8501)

**할 수 있는 것:**
- 템플릿 선택 (neon, bubble, retro 등)
- 실시간 색상/폰트/위치 조정
- 미리보기 즉시 확인
- 커스텀 템플릿 저장

---

## 4️⃣ 새로운 쇼츠 생성하기

### 방법 1: Neon 템플릿으로 생성
```bash
python -c "
from src.shorts.ranking import RankingShortsGenerator

generator = RankingShortsGenerator(style='neon', aspect_ratio='9:16')
generator.generate_from_dir(
    input_dir='downloads/user_clips',
    output_dir='output/my_neon_shorts',
    top=5,
    order='desc',
    title_mode='local',
    enable_rail=True
)
"
```

### 방법 2: Bubble 템플릿으로 생성
```bash
python -c "
from src.shorts.ranking import RankingShortsGenerator

generator = RankingShortsGenerator(style='bubble', aspect_ratio='9:16')
generator.generate_from_dir(
    input_dir='downloads/user_clips',
    output_dir='output/my_bubble_shorts',
    top=5,
    order='desc',
    title_mode='local',
    enable_rail=True
)
"
```

### 방법 3: Retro 템플릿으로 생성
```bash
python -c "
from src.shorts.ranking import RankingShortsGenerator

generator = RankingShortsGenerator(style='retro', aspect_ratio='9:16')
generator.generate_from_dir(
    input_dir='downloads/user_clips',
    output_dir='output/my_retro_shorts',
    top=5,
    order='desc',
    title_mode='local',
    enable_rail=True
)
"
```

---

## 5️⃣ AI 제목 생성 테스트 (선택)

### 1. OpenAI API 키 설정
```bash
# .env 파일 생성
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env

# openai 패키지 설치
pip install openai python-dotenv
```

### 2. AI 모드로 생성
```bash
python -c "
from src.shorts.ranking import RankingShortsGenerator

generator = RankingShortsGenerator(style='neon', aspect_ratio='9:16')
generator.generate_from_dir(
    input_dir='downloads/user_clips',
    output_dir='output/ai_generated_shorts',
    top=3,
    order='desc',
    title_mode='ai',  # AI 제목 생성!
    enable_rail=True
)
"
```

**주의**: API 키가 없으면 자동으로 `local` 모드로 전환됩니다.

---

## 6️⃣ 템플릿 비교

### 모든 템플릿으로 동시 생성
```bash
python -c "
from src.shorts.ranking import RankingShortsGenerator

templates = ['modern', 'neon', 'bubble', 'retro']

for template in templates:
    print(f'\n생성 중: {template}')
    generator = RankingShortsGenerator(style=template, aspect_ratio='9:16')
    generator.generate_from_csv(
        csv_path='data/test_ranking_real.csv',
        output_dir=f'output/compare_{template}',
        enable_rail=True,
        enable_intro=False
    )
    print(f'완료: output/compare_{template}/ranking_raw.mp4')
"
```

그러면 다음 파일들이 생성됩니다:
- `output/compare_modern/ranking_raw.mp4`
- `output/compare_neon/ranking_raw.mp4`
- `output/compare_bubble/ranking_raw.mp4`
- `output/compare_retro/ranking_raw.mp4`

---

## 7️⃣ 내 영상으로 쇼츠 만들기

### 1. 영상 준비
```bash
# 내 영상을 이 폴더에 넣기
mkdir -p my_videos
# my_videos/ 폴더에 clip_1.mp4, clip_2.mp4 등 복사
```

### 2. 쇼츠 생성
```bash
python -c "
from src.shorts.ranking import RankingShortsGenerator

generator = RankingShortsGenerator(style='neon', aspect_ratio='9:16')
final = generator.generate_from_dir(
    input_dir='my_videos',
    output_dir='output/final_shorts',
    top=5,
    order='desc',
    title_mode='local',
    enable_rail=True
)
print(f'\n✅ 완성! {final}')
"
```

---

## 🎨 템플릿 선택 가이드

| 템플릿 | 분위기 | 색상 | 추천 용도 |
|--------|--------|------|-----------|
| **modern** | 세련됨 | 금/은/동 | 일반 랭킹 |
| **neon** | 화려함 | 네온 색상 | 게이밍, 파티 |
| **bubble** | 귀여움 | 파스텔 | 키즈, 펫 |
| **retro** | 복고풍 | 80년대 | 빈티지, 레트로 |

---

## 📝 주요 옵션

### `generate_from_dir()` 파라미터
- `input_dir`: 비디오 파일 폴더
- `output_dir`: 출력 폴더
- `top`: 상위 N개만 사용 (None이면 전체)
- `order`: "desc" (5→1) 또는 "asc" (1→5)
- `title_mode`: "local" (파일명), "manual" (CSV), "ai" (AI 생성)
- `enable_rail`: 좌측 숫자 레일 활성화
- `enable_intro`: 인트로 화면 활성화
- `bgm_path`: BGM 파일 경로 (선택)

---

## 🚀 다음 단계

1. **템플릿 커스터마이징**: `streamlit run template_editor_app.py`
2. **내 영상으로 쇼츠 만들기**: 위 가이드 참고
3. **BGM 추가**: `bgm_path` 파라미터 사용
4. **AI 제목 생성**: OpenAI API 키 설정 후 `title_mode='ai'`

---

**도움말**: `python test_integration.py` 실행하면 모든 기능을 한번에 테스트할 수 있습니다!
