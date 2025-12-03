# 실시간 템플릿 에디터 설계

**버전**: v0.2.0
**작성일**: 2025-10-25
**상태**: 설계 단계

---

## 목차

1. [개요](#개요)
2. [기능 요구사항](#기능-요구사항)
3. [시스템 아키텍처](#시스템-아키텍처)
4. [UI 설계](#ui-설계)
5. [데이터 구조](#데이터-구조)
6. [구현 계획](#구현-계획)
7. [기술적 고려사항](#기술적-고려사항)

---

## 개요

### 목표
**비개발자도 쇼츠 템플릿을 GUI로 커스터마이징**할 수 있는 실시간 에디터 제공

### 핵심 가치
- ❌ 코드 수정 불필요
- ⚡ 실시간 미리보기 (0.1~0.5초)
- 💾 커스텀 템플릿 저장/재사용
- 🎨 모든 비주얼 요소 조정 가능

### 타겟 사용자
- YouTube 크리에이터 (비개발자)
- 디자인 감각 있는 콘텐츠 제작자
- 브랜딩 스타일이 명확한 채널 운영자

---

## 기능 요구사항

### Phase 1: 핵심 커스터마이징

#### 1.1 숫자 레일 (Ranking Rail)

**조정 가능한 속성**:
```yaml
숫자:
  - 폰트 크기 (20~120px)
  - 폰트 종류 (시스템 폰트 목록)
  - 색상 (각 순위별 개별 지정 가능)
  - 투명도 (0~100%)
  - 외곽선 두께 (0~10px)
  - 외곽선 색상

레이아웃:
  - X 위치 (좌측 여백)
  - Y 시작 위치
  - 숫자 간 간격 (gap)
  - 정렬 (좌/우/중앙)

효과:
  - 그림자 (활성화/크기/색상)
  - 글로우 (활성화/강도/색상)
  - 현재 순위 하이라이트 효과
```

#### 1.2 제목 (Title)

**조정 가능한 속성**:
```yaml
텍스트:
  - 폰트 크기 (30~100px)
  - 폰트 종류
  - 색상
  - 투명도
  - 외곽선 두께
  - 외곽선 색상

레이아웃:
  - X 위치 (0~1080px)
  - Y 위치 (0~1920px)
  - 정렬 (좌/중앙/우)
  - 최대 너비

배경:
  - 배경 박스 활성화
  - 배경 색상
  - 배경 투명도
  - 배경 둥근 모서리 (radius)
  - 패딩 (상하좌우)
```

#### 1.3 상단 헤더 (Top Header)

**조정 가능한 속성**:
```yaml
메인 제목:
  - 텍스트 내용 (예: "Ranking Random")
  - 폰트 크기
  - 색상
  - 위치 (X, Y)

부제목:
  - 텍스트 내용 (예: "Impressive Moments")
  - 폰트 크기
  - 색상
  - 위치 (X, Y)

배경:
  - 헤더 배경 활성화
  - 배경 색상/투명도
```

#### 1.4 전역 설정 (Global)

```yaml
해상도:
  - 9:16 (1080x1920)
  - 16:9 (1920x1080)
  - 커스텀

배경:
  - 블러 강도 (0~100)
  - 비네팅 활성화/투명도
  - 배경 색상 오버레이

안전 영역:
  - 좌우 여백
  - 상하 여백
```

### Phase 2: 고급 기능 (추후)

```yaml
애니메이션:
  - 타이틀 인트로 (슬라이드/페이드)
  - 숫자 등장 효과
  - 트랜지션 타입

클립 효과:
  - 테두리 스타일
  - 그림자
  - 회전/확대

이모지/아이콘:
  - 위치
  - 크기
  - 순위별 아이콘 지정
```

---

## 시스템 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────────────┐
│              Streamlit UI (app.py)                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────┐        ┌──────────────────┐   │
│  │  템플릿 에디터  │◄──────►│  실시간 미리보기  │   │
│  │   (조정 패널)   │        │   (이미지 표시)   │   │
│  └────────┬───────┘        └─────────▲────────┘   │
│           │                           │             │
│           │ 설정 변경                 │ 미리보기    │
│           ▼                           │             │
│  ┌────────────────────────────────────┴────────┐   │
│  │      TemplateConfigManager                  │   │
│  │  (설정 관리, 검증, 저장/불러오기)            │   │
│  └────────────────┬──────────────────────────┘   │
│                   │                               │
└───────────────────┼───────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│         TemplateEngine (리팩토링)                    │
├─────────────────────────────────────────────────────┤
│  • create_overlay_with_config(config: dict)         │
│  • draw_ranking_rail(config: RailConfig)            │
│  • draw_title(config: TitleConfig)                  │
│  • apply_effects(config: EffectsConfig)             │
└─────────────────────────────────────────────────────┘
```

### 데이터 흐름

```
사용자 조작 (슬라이더, 컬러피커)
    ↓
Streamlit 위젯 → st.session_state 업데이트
    ↓
TemplateConfigManager.validate(config)
    ↓
TemplateEngine.create_preview_overlay(config)
    ↓
미리보기 이미지 생성 (0.1~0.5초)
    ↓
st.image() 업데이트 → 화면 표시
```

---

## UI 설계

### 레이아웃 구조

```
┌─────────────────────────────────────────────────────┐
│  🎬 YouTube 쇼츠 자동 생성기                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  [📤 업로드] [🎨 템플릿 에디터] [📊 결과]            │
│                                                      │
│  ┌─────────────────┬────────────────────────────┐   │
│  │  ⚙️ 설정 패널    │  👁️ 실시간 미리보기          │   │
│  │                 │                            │   │
│  │  [템플릿 선택]  │  ┌──────────────────────┐ │   │
│  │  ├─ Default    │  │                      │ │   │
│  │  ├─ Modern     │  │   [미리보기 이미지]   │ │   │
│  │  └─ Custom     │  │   (1080x1920)        │ │   │
│  │                 │  │                      │ │   │
│  │  🔢 숫자 레일   │  └──────────────────────┘ │   │
│  │  ├─ 크기: [60] │                            │   │
│  │  ├─ 색상: [🎨] │  [🔄 미리보기 생성]         │   │
│  │  └─ 간격: [150]│                            │   │
│  │                 │  샘플 데이터:              │   │
│  │  📝 제목        │  순위: [1▼] 제목: [입력]  │   │
│  │  ├─ 크기: [60] │                            │   │
│  │  ├─ 색상: [🎨] │                            │   │
│  │  └─ 위치 X/Y   │                            │   │
│  │                 │                            │   │
│  │  🎨 전역 설정   │                            │   │
│  │  ├─ 블러: [50] │                            │   │
│  │  └─ 해상도: 9:16│                            │   │
│  │                 │                            │   │
│  │  [💾 저장]     │  [💾 템플릿 저장하기]       │   │
│  │  [🔄 초기화]   │  이름: [내 템플릿]         │   │
│  └─────────────────┴────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 위젯 선택

```python
# Streamlit 위젯 매핑
숫자/범위 → st.slider()
색상 → st.color_picker()
폰트 → st.selectbox()
토글 → st.checkbox()
텍스트 → st.text_input()
위치 → st.number_input() (X, Y 각각)
```

### 인터랙션 플로우

```
1. 사용자가 템플릿 선택 (Default/Modern/Custom)
   → config 로드 → UI 위젯 값 자동 설정

2. 사용자가 슬라이더 조정 (예: 숫자 크기 60 → 80)
   → session_state 업데이트
   → 자동 미리보기 생성 버튼 활성화

3. [미리보기 생성] 클릭
   → 로딩 스피너 표시
   → TemplateEngine 호출
   → 이미지 생성 (0.5초)
   → 우측에 표시

4. [템플릿 저장] 클릭
   → 이름 입력 (예: "내 브랜드 스타일")
   → templates/ranking/custom_브랜드.yaml 저장
   → 다음에 "템플릿 선택"에서 사용 가능
```

---

## 데이터 구조

### 템플릿 Config YAML 구조 (확장)

```yaml
# templates/ranking/custom_example.yaml

name: "Custom Brand Style"
description: "내 채널 브랜드 스타일"
aspect_ratio: "9:16"

# 숫자 레일 설정
rail:
  enabled: true
  x: 60                    # 좌측 여백
  y_start: 400             # 시작 Y 위치
  gap: 150                 # 숫자 간 간격
  alignment: "left"        # left, center, right

  font:
    family: "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    size: 60

  colors:
    rank_1: "#FFD700"      # 금
    rank_2: "#C0C0C0"      # 은
    rank_3: "#CD7F32"      # 동
    default: "#667eea"     # 4위 이하

  effects:
    border_width: 3
    border_color: "#000000"
    shadow_enabled: true
    shadow_color: "#00000080"
    shadow_offset: [2, 2]
    glow_enabled: false

  active_highlight:
    opacity: 1.0
    scale: 1.2
    glow_enabled: true
    glow_color: "#FFFFFF"
    glow_radius: 10

# 제목 설정
title:
  enabled: true
  font:
    family: "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    size: 60
    color: "#FFFFFF"

  position:
    x: 540               # 중앙
    y: 1650
    alignment: "center"  # left, center, right
    max_width: 800

  background:
    enabled: true
    color: "#000000"
    opacity: 0.7         # 0.0 ~ 1.0
    border_radius: 20
    padding: [20, 40, 20, 40]  # top, right, bottom, left

  effects:
    border_width: 2
    border_color: "#FFFFFF"
    shadow_enabled: false

# 헤더 설정
header:
  enabled: true
  main_title:
    text: "Ranking Random"
    font_size: 56
    color: "#FFFFFF"
    position: [540, 80]
    alignment: "center"

  subtitle:
    text: "Impressive Moments"
    font_size: 36
    color: "#CCCCCC"
    position: [540, 150]
    alignment: "center"

  background:
    enabled: false
    color: "#000000"
    opacity: 0.5

# 전역 설정
global:
  resolution:
    width: 1080
    height: 1920

  background:
    blur_strength: 50      # 0~100
    vignette_enabled: true
    vignette_opacity: 0.3
    color_overlay: "#00000000"  # RGBA

  safe_area:
    horizontal: 60       # 좌우 여백
    vertical: 100        # 상하 여백

  clip_area:
    width: 900
    height: 1600
    position: "center"   # center, top, bottom

# 재생 설정
playback:
  order: "reverse"       # reverse (5→1), forward (1→5)
  clip_duration: 8
```

### Python Data Classes

```python
from dataclasses import dataclass
from typing import Optional, Tuple, List

@dataclass
class FontConfig:
    family: str
    size: int
    color: str = "#FFFFFF"

@dataclass
class PositionConfig:
    x: int
    y: int
    alignment: str = "center"  # left, center, right
    max_width: Optional[int] = None

@dataclass
class BackgroundConfig:
    enabled: bool = False
    color: str = "#000000"
    opacity: float = 0.7
    border_radius: int = 0
    padding: Tuple[int, int, int, int] = (0, 0, 0, 0)

@dataclass
class EffectsConfig:
    border_width: int = 0
    border_color: str = "#000000"
    shadow_enabled: bool = False
    shadow_color: str = "#00000080"
    shadow_offset: Tuple[int, int] = (2, 2)
    glow_enabled: bool = False
    glow_color: str = "#FFFFFF"
    glow_radius: int = 10

@dataclass
class RailConfig:
    enabled: bool = True
    x: int = 60
    y_start: int = 400
    gap: int = 150
    alignment: str = "left"
    font: FontConfig = None
    colors: dict = None
    effects: EffectsConfig = None
    active_highlight: dict = None

@dataclass
class TitleConfig:
    enabled: bool = True
    font: FontConfig = None
    position: PositionConfig = None
    background: BackgroundConfig = None
    effects: EffectsConfig = None

@dataclass
class TemplateConfig:
    name: str
    description: str
    aspect_ratio: str
    rail: RailConfig
    title: TitleConfig
    header: dict
    global_settings: dict
    playback: dict
```

---

## 구현 계획

### Step 1: TemplateEngine 리팩토링

**목표**: 모든 스타일 값을 파라미터로 받도록 변경

**작업 내용**:
```python
# 기존 (하드코딩)
class TemplateEngine:
    def create_overlay(self, rank, title):
        font_size = 60  # 하드코딩
        color = "#FFD700"  # 하드코딩
        # ...

# 변경 후 (파라미터화)
class TemplateEngine:
    def __init__(self, config: TemplateConfig):
        self.config = config

    def create_overlay(self, rank, title):
        font_size = self.config.title.font.size
        color = self.config.title.font.color
        # ...

    def draw_ranking_rail(self, max_rank, active_rank):
        rail_cfg = self.config.rail
        x = rail_cfg.x
        gap = rail_cfg.gap
        # ...
```

**예상 시간**: 3~4시간

---

### Step 2: TemplateConfigManager 구현

**역할**:
- Config 검증 (색상 형식, 범위 체크)
- YAML ↔ Python dataclass 변환
- 커스텀 템플릿 저장/불러오기
- 기본값 제공

**구현**:
```python
# src/core/template_config.py

class TemplateConfigManager:
    def __init__(self):
        self.templates_dir = "templates/ranking"
        self.custom_dir = f"{self.templates_dir}/custom"
        os.makedirs(self.custom_dir, exist_ok=True)

    def load_template(self, name: str) -> TemplateConfig:
        """템플릿 로드 (YAML → dataclass)"""
        path = f"{self.templates_dir}/{name}.yaml"
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return self._dict_to_config(data)

    def save_custom_template(self, name: str, config: TemplateConfig):
        """커스텀 템플릿 저장 (dataclass → YAML)"""
        data = self._config_to_dict(config)
        path = f"{self.custom_dir}/{name}.yaml"
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)

    def list_templates(self) -> List[str]:
        """사용 가능한 템플릿 목록"""
        templates = []

        # 기본 템플릿
        for file in os.listdir(self.templates_dir):
            if file.endswith('.yaml'):
                templates.append(file[:-5])

        # 커스텀 템플릿
        for file in os.listdir(self.custom_dir):
            if file.endswith('.yaml'):
                templates.append(f"custom/{file[:-5]}")

        return templates

    def validate_config(self, config: TemplateConfig) -> bool:
        """설정 검증"""
        # 색상 형식 체크
        if not self._is_valid_color(config.title.font.color):
            raise ValueError("Invalid color format")

        # 범위 체크
        if not (20 <= config.title.font.size <= 120):
            raise ValueError("Font size out of range")

        # ... 기타 검증

        return True

    def _is_valid_color(self, color: str) -> bool:
        """색상 형식 검증 (#RRGGBB or #RRGGBBAA)"""
        import re
        return bool(re.match(r'^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$', color))

    def _dict_to_config(self, data: dict) -> TemplateConfig:
        """YAML dict → dataclass"""
        # ... 변환 로직
        pass

    def _config_to_dict(self, config: TemplateConfig) -> dict:
        """dataclass → YAML dict"""
        # ... 변환 로직
        pass
```

**예상 시간**: 2~3시간

---

### Step 3: Streamlit 템플릿 에디터 UI

**파일**: `app.py` (기존 파일 확장)

**구현**:
```python
# 새 탭 추가
tab1, tab2, tab3 = st.tabs(["📤 업로드", "🎨 템플릿 에디터", "📊 결과"])

with tab2:
    st.header("🎨 템플릿 에디터")

    # 2단 레이아웃
    col_settings, col_preview = st.columns([1, 1])

    with col_settings:
        st.subheader("⚙️ 설정")

        # 템플릿 선택
        config_manager = TemplateConfigManager()
        templates = config_manager.list_templates()

        selected_template = st.selectbox(
            "템플릿 선택",
            templates,
            help="기본 템플릿을 선택하거나 저장된 커스텀 템플릿을 불러오세요"
        )

        # 템플릿 로드
        if 'current_config' not in st.session_state or st.session_state.get('selected_template') != selected_template:
            st.session_state.current_config = config_manager.load_template(selected_template)
            st.session_state.selected_template = selected_template

        config = st.session_state.current_config

        # ===== 숫자 레일 설정 =====
        with st.expander("🔢 숫자 레일", expanded=True):
            config.rail.enabled = st.checkbox("숫자 레일 활성화", value=config.rail.enabled)

            if config.rail.enabled:
                col1, col2 = st.columns(2)

                with col1:
                    config.rail.font.size = st.slider(
                        "폰트 크기",
                        min_value=20,
                        max_value=120,
                        value=config.rail.font.size,
                        key="rail_font_size"
                    )

                    config.rail.x = st.number_input(
                        "X 위치 (좌측 여백)",
                        min_value=0,
                        max_value=500,
                        value=config.rail.x,
                        key="rail_x"
                    )

                with col2:
                    config.rail.gap = st.slider(
                        "숫자 간격",
                        min_value=50,
                        max_value=300,
                        value=config.rail.gap,
                        key="rail_gap"
                    )

                    config.rail.y_start = st.number_input(
                        "Y 시작 위치",
                        min_value=0,
                        max_value=1920,
                        value=config.rail.y_start,
                        key="rail_y_start"
                    )

                st.subheader("순위별 색상")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    config.rail.colors['rank_1'] = st.color_picker(
                        "1위 (금)",
                        value=config.rail.colors['rank_1'],
                        key="color_rank_1"
                    )

                with col2:
                    config.rail.colors['rank_2'] = st.color_picker(
                        "2위 (은)",
                        value=config.rail.colors['rank_2'],
                        key="color_rank_2"
                    )

                with col3:
                    config.rail.colors['rank_3'] = st.color_picker(
                        "3위 (동)",
                        value=config.rail.colors['rank_3'],
                        key="color_rank_3"
                    )

                with col4:
                    config.rail.colors['default'] = st.color_picker(
                        "4위 이하",
                        value=config.rail.colors['default'],
                        key="color_default"
                    )

        # ===== 제목 설정 =====
        with st.expander("📝 제목", expanded=True):
            config.title.enabled = st.checkbox("제목 활성화", value=config.title.enabled)

            if config.title.enabled:
                col1, col2 = st.columns(2)

                with col1:
                    config.title.font.size = st.slider(
                        "폰트 크기",
                        min_value=30,
                        max_value=100,
                        value=config.title.font.size,
                        key="title_font_size"
                    )

                    config.title.font.color = st.color_picker(
                        "폰트 색상",
                        value=config.title.font.color,
                        key="title_color"
                    )

                with col2:
                    config.title.position.x = st.number_input(
                        "X 위치",
                        min_value=0,
                        max_value=1080,
                        value=config.title.position.x,
                        key="title_x"
                    )

                    config.title.position.y = st.number_input(
                        "Y 위치",
                        min_value=0,
                        max_value=1920,
                        value=config.title.position.y,
                        key="title_y"
                    )

                # 배경 설정
                st.subheader("배경")
                config.title.background.enabled = st.checkbox(
                    "배경 박스",
                    value=config.title.background.enabled,
                    key="title_bg_enabled"
                )

                if config.title.background.enabled:
                    col1, col2 = st.columns(2)
                    with col1:
                        config.title.background.color = st.color_picker(
                            "배경 색상",
                            value=config.title.background.color,
                            key="title_bg_color"
                        )
                    with col2:
                        config.title.background.opacity = st.slider(
                            "투명도",
                            min_value=0.0,
                            max_value=1.0,
                            value=config.title.background.opacity,
                            key="title_bg_opacity"
                        )

        # ===== 전역 설정 =====
        with st.expander("🎨 전역 설정"):
            config.global_settings['background']['blur_strength'] = st.slider(
                "배경 블러 강도",
                min_value=0,
                max_value=100,
                value=config.global_settings['background']['blur_strength'],
                key="blur_strength"
            )

            config.global_settings['background']['vignette_enabled'] = st.checkbox(
                "비네팅 효과",
                value=config.global_settings['background']['vignette_enabled'],
                key="vignette_enabled"
            )

        # ===== 저장/초기화 버튼 =====
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 초기화", use_container_width=True):
                st.session_state.current_config = config_manager.load_template(selected_template)
                st.rerun()

        with col2:
            if st.button("💾 현재 설정 저장", use_container_width=True):
                st.session_state.show_save_dialog = True

    # ===== 미리보기 영역 =====
    with col_preview:
        st.subheader("👁️ 실시간 미리보기")

        # 샘플 데이터 입력
        col1, col2 = st.columns(2)
        with col1:
            preview_rank = st.selectbox("순위", list(range(1, 11)), key="preview_rank")
        with col2:
            preview_title = st.text_input("제목", value="샘플 제목", key="preview_title")

        # 미리보기 생성 버튼
        if st.button("🔄 미리보기 생성", type="primary", use_container_width=True):
            with st.spinner("생성 중..."):
                # TemplateEngine으로 미리보기 생성
                engine = TemplateEngine(config)

                preview_path = engine.create_overlay(
                    rank=preview_rank,
                    title=preview_title,
                    emoji="",
                    score=None,
                    description=""
                )

                st.session_state.preview_image = preview_path

        # 미리보기 이미지 표시
        if 'preview_image' in st.session_state and os.path.exists(st.session_state.preview_image):
            st.image(
                st.session_state.preview_image,
                use_column_width=True,
                caption=f"순위 #{preview_rank}: {preview_title}"
            )
        else:
            st.info("👆 위에서 설정을 조정하고 '미리보기 생성'을 클릭하세요")

        # 저장 다이얼로그
        if st.session_state.get('show_save_dialog', False):
            st.markdown("---")
            st.subheader("💾 템플릿 저장")

            save_name = st.text_input(
                "템플릿 이름",
                placeholder="예: 내_브랜드_스타일",
                key="save_template_name"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("저장", type="primary", use_container_width=True):
                    if save_name:
                        config_manager.save_custom_template(save_name, config)
                        st.success(f"✅ '{save_name}' 템플릿 저장 완료!")
                        st.session_state.show_save_dialog = False
                        st.rerun()
                    else:
                        st.error("템플릿 이름을 입력하세요")

            with col2:
                if st.button("취소", use_container_width=True):
                    st.session_state.show_save_dialog = False
                    st.rerun()
```

**예상 시간**: 4~5시간

---

### Step 4: 실시간 미리보기 최적화

**목표**: 미리보기 생성 시간 0.1~0.5초로 단축

**최적화 방법**:

1. **캐싱**
```python
@st.cache_data(ttl=60)
def generate_preview(config_hash: str, rank: int, title: str):
    """설정이 같으면 캐시된 이미지 반환"""
    engine = TemplateEngine(config)
    return engine.create_overlay(rank, title, ...)
```

2. **저해상도 미리보기**
```python
# 미리보기용: 540x960 (절반 해상도)
preview_config = copy.deepcopy(config)
preview_config.global_settings['resolution'] = {
    'width': 540,
    'height': 960
}
```

3. **비동기 생성** (선택)
```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1)

if st.button("미리보기 생성"):
    future = executor.submit(generate_preview, ...)
    with st.spinner("생성 중..."):
        preview_path = future.result()
```

**예상 시간**: 1~2시간

---

### Step 5: 통합 테스트

**테스트 시나리오**:

1. ✅ 템플릿 선택 → UI 값 자동 로드
2. ✅ 슬라이더 조정 → 미리보기 생성
3. ✅ 커스텀 템플릿 저장 → 다시 불러오기
4. ✅ 저장된 템플릿으로 실제 쇼츠 생성
5. ✅ 에러 케이스 처리 (잘못된 색상, 범위 초과)

**예상 시간**: 2~3시간

---

## 기술적 고려사항

### 1. 성능

**문제**: Streamlit은 위젯 변경 시마다 전체 스크립트 재실행

**해결**:
- `st.cache_data`로 무거운 연산 캐싱
- `st.session_state`로 상태 유지
- "미리보기 생성" 버튼으로 수동 트리거 (자동 생성 X)

### 2. 폰트 관리

**문제**: 시스템마다 설치된 폰트가 다름

**해결**:
```python
def list_available_fonts():
    """시스템 폰트 목록 반환"""
    font_dirs = [
        "/usr/share/fonts",
        "/System/Library/Fonts",
        "C:\\Windows\\Fonts"
    ]

    fonts = []
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            for root, dirs, files in os.walk(font_dir):
                for file in files:
                    if file.endswith(('.ttf', '.ttc', '.otf')):
                        fonts.append(os.path.join(root, file))

    return sorted(fonts)
```

### 3. 색상 형식

**문제**: Streamlit `color_picker`는 `#RRGGBB`만 반환 (알파 채널 X)

**해결**:
```python
# 투명도는 별도 슬라이더로 조정
color = st.color_picker("색상", "#FF0000")
opacity = st.slider("투명도", 0.0, 1.0, 1.0)

# RGBA로 변환
rgba_color = color + format(int(opacity * 255), '02x')
# 결과: "#FF0000FF" (완전 불투명)
```

### 4. YAML 저장 시 한글 깨짐

**해결**:
```python
with open(path, 'w', encoding='utf-8') as f:
    yaml.dump(data, f, allow_unicode=True)
```

### 5. 미리보기 vs 실제 렌더링

**문제**: 미리보기는 오버레이만, 실제는 비디오 클립 + 오버레이

**해결**:
- 미리보기: 투명 배경 PNG (오버레이만)
- 실제 생성: 비디오 + 오버레이 합성
- 미리보기에 "샘플 배경 이미지" 표시 옵션

---

## 예상 총 소요 시간

| 단계 | 작업 | 시간 |
|-----|------|------|
| Step 1 | TemplateEngine 리팩토링 | 3~4시간 |
| Step 2 | TemplateConfigManager | 2~3시간 |
| Step 3 | Streamlit UI 구현 | 4~5시간 |
| Step 4 | 미리보기 최적화 | 1~2시간 |
| Step 5 | 통합 테스트 | 2~3시간 |
| **총계** | | **12~17시간** |

---

## 다음 단계

1. ✅ 설계 문서 검토
2. 🔄 TemplateEngine 리팩토링 시작
3. 🔄 기본 UI 프로토타입
4. 🔄 미리보기 기능 통합
5. 🔄 전체 테스트 및 버그 수정

---

**작성일**: 2025-10-25
**버전**: v0.2.0
**상태**: 설계 완료, 구현 대기
