"""
실시간 템플릿 에디터 - Streamlit UI
템플릿 커스터마이징 및 실시간 미리보기 제공
"""

import streamlit as st
import os
import sys
from pathlib import Path

# 모듈 import
sys.path.append(str(Path(__file__).parent))
from src.core.template_config import TemplateConfig, TemplateConfigManager
from src.shorts.template_engine import TemplateEngine

# 페이지 설정
st.set_page_config(
    page_title="템플릿 에디터 - YouTube 쇼츠 생성기",
    page_icon="🎨",
    layout="wide"
)

# 세션 상태 초기화
if 'config_manager' not in st.session_state:
    st.session_state.config_manager = TemplateConfigManager()

if 'current_config' not in st.session_state:
    st.session_state.current_config = st.session_state.config_manager._get_default_config()

if 'preview_image' not in st.session_state:
    st.session_state.preview_image = None

if 'show_save_dialog' not in st.session_state:
    st.session_state.show_save_dialog = False

# 타이틀
st.title("🎨 템플릿 에디터")
st.markdown("쇼츠 템플릿을 커스터마이징하고 실시간으로 미리보기를 확인하세요")
st.markdown("---")

# 2단 레이아웃
col_settings, col_preview = st.columns([1, 1])

with col_settings:
    st.header("⚙️ 설정")

    # 템플릿 선택
    config_manager = st.session_state.config_manager
    templates = config_manager.list_templates()

    if not templates:
        templates = ["default"]

    selected_template = st.selectbox(
        "템플릿 선택",
        templates,
        help="기본 템플릿을 선택하거나 저장된 커스텀 템플릿을 불러오세요",
        key="selected_template_selector"
    )

    # 템플릿 로드 버튼
    col_load, col_new = st.columns(2)
    with col_load:
        if st.button("📂 불러오기", use_container_width=True):
            st.session_state.current_config = config_manager.load_template(selected_template)
            st.success(f"✅ '{selected_template}' 템플릿 로드 완료")
            st.rerun()

    with col_new:
        if st.button("🆕 새로 만들기", use_container_width=True):
            st.session_state.current_config = config_manager._get_default_config()
            st.success("✅ 기본 템플릿으로 초기화")
            st.rerun()

    config = st.session_state.current_config

    st.markdown("---")

    # ===== 숫자 레일 설정 =====
    with st.expander("🔢 숫자 레일", expanded=True):
        config.rail.enabled = st.checkbox(
            "숫자 레일 활성화",
            value=config.rail.enabled,
            key="rail_enabled"
        )

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

            st.subheader("효과")
            col1, col2 = st.columns(2)

            with col1:
                config.rail.inactive_opacity = st.slider(
                    "비활성 투명도",
                    min_value=0.0,
                    max_value=1.0,
                    value=config.rail.inactive_opacity,
                    step=0.1,
                    key="rail_inactive_opacity"
                )

            with col2:
                config.rail.active_stroke = st.slider(
                    "활성 외곽선 두께",
                    min_value=0,
                    max_value=10,
                    value=config.rail.active_stroke,
                    key="rail_active_stroke"
                )

            st.subheader("제목 표시")
            config.rail.title_enabled = st.checkbox(
                "숫자 옆 제목 표시",
                value=getattr(config.rail, 'title_enabled', True),
                key="rail_title_enabled"
            )

            if config.rail.title_enabled:
                col1, col2 = st.columns(2)
                with col1:
                    config.rail.title_offset_x = st.number_input(
                        "제목 X 오프셋",
                        min_value=50,
                        max_value=300,
                        value=getattr(config.rail, 'title_offset_x', 100),
                        key="rail_title_offset_x"
                    )
                with col2:
                    config.rail.title_font_size = st.number_input(
                        "제목 폰트 크기",
                        min_value=20,
                        max_value=80,
                        value=getattr(config.rail, 'title_font_size', 40),
                        key="rail_title_font_size"
                    )

    # ===== 제목 설정 =====
    with st.expander("📝 제목", expanded=True):
        config.title.enabled = st.checkbox(
            "제목 활성화",
            value=config.title.enabled,
            key="title_enabled"
        )

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
                col1, col2, col3 = st.columns(3)
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
                        step=0.1,
                        key="title_bg_opacity"
                    )
                with col3:
                    config.title.background.border_radius = st.slider(
                        "둥근 모서리",
                        min_value=0,
                        max_value=50,
                        value=config.title.background.border_radius,
                        key="title_bg_radius"
                    )

    # ===== 헤더 설정 =====
    with st.expander("📢 상단 헤더", expanded=False):
        config.header.enabled = st.checkbox(
            "헤더 활성화",
            value=config.header.enabled,
            key="header_enabled"
        )

        if config.header.enabled:
            st.subheader("메인 제목")

            config.header.main_title['text'] = st.text_input(
                "텍스트",
                value=config.header.main_title['text'],
                key="header_main_text"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                config.header.main_title['font_size'] = st.slider(
                    "폰트 크기",
                    min_value=30,
                    max_value=100,
                    value=config.header.main_title['font_size'],
                    key="header_main_size"
                )

            with col2:
                config.header.main_title['color'] = st.color_picker(
                    "색상",
                    value=config.header.main_title['color'],
                    key="header_main_color"
                )

            with col3:
                config.header.main_title['alignment'] = st.selectbox(
                    "정렬",
                    ["left", "center", "right"],
                    index=["left", "center", "right"].index(config.header.main_title.get('alignment', 'center')),
                    format_func=lambda x: {"left": "왼쪽", "center": "중앙", "right": "오른쪽"}[x],
                    key="header_main_align"
                )

            col1, col2 = st.columns(2)
            with col1:
                config.header.main_title['position'][0] = st.number_input(
                    "X 위치",
                    min_value=0,
                    max_value=1080,
                    value=config.header.main_title['position'][0],
                    key="header_main_x"
                )
            with col2:
                config.header.main_title['position'][1] = st.number_input(
                    "Y 위치",
                    min_value=0,
                    max_value=500,
                    value=config.header.main_title['position'][1],
                    key="header_main_y"
                )

            # 효과
            st.write("**효과**")
            col1, col2 = st.columns(2)
            with col1:
                if 'stroke_width' not in config.header.main_title:
                    config.header.main_title['stroke_width'] = 0
                config.header.main_title['stroke_width'] = st.slider(
                    "외곽선 두께",
                    min_value=0,
                    max_value=10,
                    value=config.header.main_title['stroke_width'],
                    key="header_main_stroke"
                )
            with col2:
                if 'stroke_color' not in config.header.main_title:
                    config.header.main_title['stroke_color'] = '#000000'
                config.header.main_title['stroke_color'] = st.color_picker(
                    "외곽선 색상",
                    value=config.header.main_title['stroke_color'],
                    key="header_main_stroke_color"
                )

            st.markdown("---")
            st.subheader("부제목")

            config.header.subtitle['text'] = st.text_input(
                "텍스트",
                value=config.header.subtitle['text'],
                key="header_sub_text"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                config.header.subtitle['font_size'] = st.slider(
                    "폰트 크기",
                    min_value=20,
                    max_value=80,
                    value=config.header.subtitle['font_size'],
                    key="header_sub_size"
                )

            with col2:
                config.header.subtitle['color'] = st.color_picker(
                    "색상",
                    value=config.header.subtitle['color'],
                    key="header_sub_color"
                )

            with col3:
                config.header.subtitle['alignment'] = st.selectbox(
                    "정렬",
                    ["left", "center", "right"],
                    index=["left", "center", "right"].index(config.header.subtitle.get('alignment', 'center')),
                    format_func=lambda x: {"left": "왼쪽", "center": "중앙", "right": "오른쪽"}[x],
                    key="header_sub_align"
                )

            col1, col2 = st.columns(2)
            with col1:
                config.header.subtitle['position'][0] = st.number_input(
                    "X 위치",
                    min_value=0,
                    max_value=1080,
                    value=config.header.subtitle['position'][0],
                    key="header_sub_x"
                )
            with col2:
                config.header.subtitle['position'][1] = st.number_input(
                    "Y 위치",
                    min_value=0,
                    max_value=500,
                    value=config.header.subtitle['position'][1],
                    key="header_sub_y"
                )

            # 효과
            st.write("**효과**")
            col1, col2 = st.columns(2)
            with col1:
                if 'stroke_width' not in config.header.subtitle:
                    config.header.subtitle['stroke_width'] = 0
                config.header.subtitle['stroke_width'] = st.slider(
                    "외곽선 두께",
                    min_value=0,
                    max_value=10,
                    value=config.header.subtitle['stroke_width'],
                    key="header_sub_stroke"
                )
            with col2:
                if 'stroke_color' not in config.header.subtitle:
                    config.header.subtitle['stroke_color'] = '#000000'
                config.header.subtitle['stroke_color'] = st.color_picker(
                    "외곽선 색상",
                    value=config.header.subtitle['stroke_color'],
                    key="header_sub_stroke_color"
                )

    # ===== 전역 설정 =====
    with st.expander("🎨 전역 설정"):
        config.global_settings.background['blur_strength'] = st.slider(
            "배경 블러 강도",
            min_value=0,
            max_value=100,
            value=config.global_settings.background['blur_strength'],
            key="blur_strength"
        )

        config.global_settings.background['vignette_enabled'] = st.checkbox(
            "비네팅 효과",
            value=config.global_settings.background['vignette_enabled'],
            key="vignette_enabled"
        )

        if config.global_settings.background['vignette_enabled']:
            config.global_settings.background['vignette_opacity'] = st.slider(
                "비네팅 투명도",
                min_value=0.0,
                max_value=1.0,
                value=config.global_settings.background['vignette_opacity'],
                step=0.1,
                key="vignette_opacity"
            )

    # ===== 저장/초기화 버튼 =====
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 초기화", use_container_width=True):
            st.session_state.current_config = config_manager._get_default_config()
            st.success("✅ 기본 설정으로 초기화")
            st.rerun()

    with col2:
        if st.button("💾 템플릿 저장하기", use_container_width=True):
            st.session_state.show_save_dialog = True
            st.rerun()

# ===== 미리보기 영역 =====
with col_preview:
    st.header("👁️ 실시간 미리보기")

    # 샘플 데이터 입력
    st.subheader("샘플 데이터")

    preview_rank = st.selectbox(
        "현재 활성 순위",
        list(range(1, 6)),
        index=0,
        key="preview_rank"
    )

    st.write("**순위별 제목 입력** (1~5위)")

    # 제목 입력 (5개)
    sample_titles = {}
    cols = st.columns(2)
    for i in range(1, 6):
        col_idx = (i - 1) % 2
        with cols[col_idx]:
            title = st.text_input(
                f"{i}위",
                value=f"샘플 제목 {i}",
                key=f"sample_title_{i}"
            )
            sample_titles[i] = title

    # 미리보기 생성 버튼
    if st.button("🔄 미리보기 생성", type="primary", use_container_width=True):
        with st.spinner("미리보기 생성 중..."):
            try:
                # TemplateEngine으로 미리보기 생성
                engine = TemplateEngine(config=config, aspect_ratio="9:16")

                # 레일 오버레이 생성 (제목 포함)
                rail_path = engine.draw_ranking_rail(
                    max_rank=5,
                    active_rank=preview_rank,
                    titles=sample_titles
                )

                st.session_state.preview_image = rail_path
                st.success("✅ 미리보기 생성 완료!")

            except Exception as e:
                st.error(f"❌ 미리보기 생성 실패: {e}")
                import traceback
                st.code(traceback.format_exc())

    # 미리보기 이미지 표시
    if st.session_state.preview_image and os.path.exists(st.session_state.preview_image):
        st.image(
            st.session_state.preview_image,
            use_container_width=True,
            caption=f"미리보기 - 활성 순위: {preview_rank}"
        )
    else:
        # 플레이스홀더
        st.info("👆 위에서 설정을 조정하고 '미리보기 생성'을 클릭하세요")
        st.markdown("""
        **조정 가능한 설정:**
        - 🔢 숫자 레일: 크기, 색상, 위치, 간격
        - 📝 제목: 크기, 색상, 위치, 배경
        - 🎨 전역: 블러, 비네팅
        """)

# ===== 저장 다이얼로그 =====
if st.session_state.show_save_dialog:
    st.markdown("---")
    st.subheader("💾 템플릿 저장")

    save_name = st.text_input(
        "템플릿 이름",
        placeholder="예: 내_브랜드_스타일",
        key="save_template_name"
    )

    config.name = st.text_input(
        "템플릿 표시 이름",
        value=config.name,
        key="template_display_name"
    )

    config.description = st.text_area(
        "설명 (선택)",
        value=config.description,
        key="template_description"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("저장", type="primary", use_container_width=True):
            if save_name:
                try:
                    # 설정 검증
                    is_valid, error_msg = config_manager.validate_config(config)
                    if not is_valid:
                        st.error(f"❌ 설정 오류: {error_msg}")
                    else:
                        # 저장
                        config_manager.save_custom_template(save_name, config)
                        st.success(f"✅ '{save_name}' 템플릿 저장 완료!")
                        st.session_state.show_save_dialog = False
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ 저장 실패: {e}")
            else:
                st.error("템플릿 이름을 입력하세요")

    with col2:
        if st.button("취소", use_container_width=True):
            st.session_state.show_save_dialog = False
            st.rerun()

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🎨 실시간 템플릿 에디터 | Made with ❤️ by YouTube Shorts Generator</p>
</div>
""", unsafe_allow_html=True)
