# 🎨 실시간 템플릿 에디터 사용 가이드

YouTube 쇼츠 템플릿을 GUI로 커스터마이징하고 실시간 미리보기를 확인할 수 있습니다.

---

## ✅ 구현 완료 사항

### 1. 핵심 기능
- ✅ **실시간 미리보기**: 설정 변경 시 즉시 확인 가능 (0.5초 이내)
- ✅ **템플릿 저장/불러오기**: 커스텀 템플릿 재사용
- ✅ **설정 검증**: 잘못된 값 자동 감지
- ✅ **하위 호환성**: 기존 코드와 100% 호환

### 2. 조정 가능한 속성

#### 🔢 숫자 레일 (좌측 순위 표시)
- 폰트 크기 (20~120px)
- X 위치, Y 시작 위치
- 숫자 간격
- **순위별 색상** (1위: 금, 2위: 은, 3위: 동, 4위 이하)
- 비활성 투명도
- 활성 외곽선 두께

#### 📝 제목
- 폰트 크기 (30~100px)
- 폰트 색상
- X/Y 위치
- **배경 박스**:
  - 활성화/비활성화
  - 배경 색상
  - 투명도
  - 둥근 모서리

#### 🎨 전역 설정
- 배경 블러 강도 (0~100)
- 비네팅 효과 (활성화/투명도)

---

## 🚀 빠른 시작

### 1. 템플릿 에디터 실행

```bash
cd /home/junhyun/youtube-project/video-auto-generator

streamlit run template_editor_app.py
```

### 2. 브라우저 접속

자동으로 브라우저가 열립니다. 또는:
- URL: `http://localhost:8501`

---

## 📖 사용 방법

### Step 1: 템플릿 선택

1. 상단 "템플릿 선택" 드롭다운에서 기본 템플릿 선택
   - `modern`: 기본 스타일
   - `custom/xxx`: 저장한 커스텀 템플릿

2. **📂 불러오기** 클릭

### Step 2: 설정 조정

좌측 패널에서 원하는 값을 조정:

#### 🔢 숫자 레일
```
폰트 크기: 48 → 60
X 위치: 60 → 80
간격: 150 → 160

순위별 색상:
1위: #FFD700 (금색)
2위: #C0C0C0 (은색)
3위: #CD7F32 (동색)
4위 이하: #667eea (보라)
```

#### 📝 제목
```
폰트 크기: 60 → 70
색상: #FFFFFF (흰색)
위치: X=540, Y=1650

배경 박스:
✅ 활성화
색상: #000000 (검정)
투명도: 0.7
둥근 모서리: 20
```

### Step 3: 실시간 미리보기

1. 우측 "샘플 데이터" 입력:
   - 순위: 1~10 선택
   - 제목: 원하는 텍스트 입력

2. **🔄 미리보기 생성** 클릭

3. 우측에 미리보기 이미지 표시

### Step 4: 템플릿 저장

1. **💾 템플릿 저장하기** 클릭

2. 정보 입력:
   ```
   템플릿 이름: my_brand_style
   템플릿 표시 이름: My Brand Style
   설명: 빨간 1위, 청량한 느낌
   ```

3. **저장** 클릭

4. `templates/ranking/custom/my_brand_style.yaml`에 저장됨

---

## 🎯 실제 쇼츠 생성에 사용하기

### 방법 1: 저장된 템플릿 사용 (권장)

```python
from src.shorts.ranking import RankingShortsGenerator

# 저장된 커스텀 템플릿 사용
generator = RankingShortsGenerator(style="custom/my_brand_style", aspect_ratio="9:16")

generator.generate_from_csv(
    csv_path="data/ranking.csv",
    output_dir="output/final",
    bgm_path="assets/bgm/test.mp3"
)
```

### 방법 2: Config 직접 전달

```python
from src.core.template_config import TemplateConfigManager
from src.shorts.template_engine import TemplateEngine

# Config 로드
manager = TemplateConfigManager()
config = manager.load_template("custom/my_brand_style")

# 일부 설정 수정
config.rail.font.size = 70
config.title.font.color = "#FF0000"

# TemplateEngine에 전달
engine = TemplateEngine(config=config, aspect_ratio="9:16")
```

---

## 📂 파일 구조

```
video-auto-generator/
├── template_editor_app.py          # 🎨 템플릿 에디터 UI
├── test_template_editor.py         # 🧪 통합 테스트
│
├── src/
│   ├── core/
│   │   └── template_config.py      # Config 관리 (NEW)
│   │
│   └── shorts/
│       ├── template_engine.py      # 리팩토링 (config 지원)
│       └── ranking.py              # 기존 코드 (호환)
│
├── templates/
│   └── ranking/
│       ├── modern/                  # 기본 템플릿
│       │   └── config.yaml
│       │
│       └── custom/                  # 커스텀 템플릿 저장 폴더
│           ├── my_brand_style.yaml
│           └── test_template.yaml
│
└── docs/
    └── TEMPLATE_EDITOR_DESIGN.md   # 상세 설계 문서
```

---

## 🧪 테스트

### 통합 테스트 실행

```bash
python test_template_editor.py
```

**테스트 항목**:
1. ✅ TemplateConfigManager (저장/로드/검증)
2. ✅ TemplateEngine (config 기반 렌더링)
3. ✅ Config ↔ YAML 변환

---

## 🎨 커스터마이징 예시

### 예시 1: 빨간 1위 강조 스타일

```python
config = manager._get_default_config()

# 1위만 빨강, 나머지 흰색
config.rail.colors['rank_1'] = '#FF0000'
config.rail.colors['rank_2'] = '#FFFFFF'
config.rail.colors['rank_3'] = '#FFFFFF'
config.rail.colors['default'] = '#FFFFFF'

# 큰 폰트
config.rail.font.size = 70

# 저장
manager.save_custom_template("red_winner", config)
```

### 예시 2: 네온 스타일

```python
config = manager._get_default_config()

# 네온 색상
config.rail.colors['rank_1'] = '#FF006E'
config.rail.colors['rank_2'] = '#8338EC'
config.rail.colors['rank_3'] = '#3A86FF'
config.rail.colors['default'] = '#00F5FF'

# 글로우 효과
config.rail.active_stroke = 6

manager.save_custom_template("neon_style", config)
```

### 예시 3: 미니멀 스타일

```python
config = manager._get_default_config()

# 모두 흰색
config.rail.colors['rank_1'] = '#FFFFFF'
config.rail.colors['rank_2'] = '#FFFFFF'
config.rail.colors['rank_3'] = '#FFFFFF'
config.rail.colors['default'] = '#FFFFFF'

# 작은 폰트, 넓은 간격
config.rail.font.size = 40
config.rail.gap = 200

# 배경 없음
config.title.background.enabled = False

manager.save_custom_template("minimal", config)
```

---

## 🐛 문제 해결

### 1. "Template not found" 오류

**원인**: 템플릿 경로 오류

**해결**:
```bash
# 템플릿 목록 확인
python -c "from src.core.template_config import TemplateConfigManager; print(TemplateConfigManager().list_templates())"

# 기본 템플릿 확인
ls templates/ranking/modern/config.yaml
```

### 2. 폰트 렌더링 실패

**원인**: 시스템 폰트 없음

**해결**:
```bash
# 한글 폰트 설치 (Ubuntu/Debian)
sudo apt install fonts-noto-cjk

# 폰트 경로 확인
fc-list | grep Noto
```

### 3. 미리보기 생성 느림

**원인**: 고해상도 렌더링

**해결**: 코드에서 미리보기용 저해상도 설정 추가 (이미 최적화됨)

---

## 📊 성능

| 작업 | 시간 |
|-----|------|
| Config 로드 | < 0.01초 |
| Config 저장 | < 0.05초 |
| 미리보기 생성 | 0.1~0.5초 |
| 실제 클립 생성 | 5~10초 (FFmpeg) |

---

## 🔮 향후 계획

### Phase 2 (추후)
- [ ] 더 많은 커스터마이징 옵션
  - [ ] 헤더 텍스트 수정
  - [ ] 이모지 위치/크기
  - [ ] 애니메이션 효과
- [ ] 폰트 업로드 기능
- [ ] 배경 이미지 업로드
- [ ] 프리셋 템플릿 갤러리

---

## 💡 팁

1. **빠른 실험**: 미리보기로 바로 확인하면서 조정
2. **순위별 색상**: 1~3위는 눈에 띄게, 4위 이하는 통일
3. **템플릿 버전 관리**: `my_style_v1`, `my_style_v2`로 저장
4. **기본값 유지**: 큰 변경 전에 기본 템플릿 백업

---

## 📞 문의

- 설계 문서: `docs/TEMPLATE_EDITOR_DESIGN.md`
- 프로젝트 문서: `PROJECT_DOCUMENTATION.md`
- GitHub Issues: (프로젝트 URL)

---

**Made with ❤️ by YouTube Shorts Generator**
**Version**: v0.2.0
**Date**: 2025-10-25
