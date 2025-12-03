"""
통합 YouTube 쇼츠 생성기 웹앱
- 템플릿 커스터마이징
- 영상 업로드 (CSV + 클립 or 폴더)
- 실시간 미리보기
- 쇼츠 자동 생성
"""

import streamlit as st
import pandas as pd
import os
import sys
import tempfile
import shutil
from pathlib import Path

# 모듈 import
sys.path.append(str(Path(__file__).parent))
from src.core.template_config import TemplateConfig, TemplateConfigManager
from src.shorts.template_engine import TemplateEngine
from src.shorts.ranking import RankingShortsGenerator

# 페이지 설정
st.set_page_config(
    page_title="YouTube 쇼츠 생성기 - 통합 버전",
    page_icon="🎬",
    layout="wide"
)

# 세션 상태 초기화
if 'config_manager' not in st.session_state:
    st.session_state.config_manager = TemplateConfigManager()

if 'current_config' not in st.session_state:
    st.session_state.current_config = st.session_state.config_manager._get_default_config()

if 'preview_image' not in st.session_state:
    st.session_state.preview_image = None

if 'output_video' not in st.session_state:
    st.session_state.output_video = None

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}


# ============================================================
# 사이드바: 템플릿 설정
# ============================================================
with st.sidebar:
    st.header("🎨 템플릿 설정")

    config_manager = st.session_state.config_manager
    config = st.session_state.current_config

    # 템플릿 선택
    templates = config_manager.list_templates()
    if not templates:
        templates = ["default"]

    selected_template = st.selectbox(
        "템플릿 선택",
        templates,
        help="기본 템플릿 또는 커스텀 템플릿 선택",
        key="template_selector"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📂 불러오기", use_container_width=True):
            st.session_state.current_config = config_manager.load_template(selected_template)
            st.success(f"✅ '{selected_template}' 로드")
            st.rerun()

    with col2:
        if st.button("🆕 초기화", use_container_width=True):
            st.session_state.current_config = config_manager._get_default_config()
            st.success("✅ 초기화 완료")
            st.rerun()

    st.markdown("---")

    # 템플릿 커스터마이징
    with st.expander("🔢 숫자 레일", expanded=False):
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
                    min_value=30,
                    max_value=100,
                    value=config.rail.font.size,
                    key="rail_font_size"
                )
            with col2:
                config.rail.gap = st.slider(
                    "간격",
                    min_value=100,
                    max_value=250,
                    value=config.rail.gap,
                    key="rail_gap"
                )

            st.write("**순위별 색상**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                config.rail.colors['rank_1'] = st.color_picker(
                    "1위",
                    value=config.rail.colors['rank_1'],
                    key="color_1"
                )
            with col2:
                config.rail.colors['rank_2'] = st.color_picker(
                    "2위",
                    value=config.rail.colors['rank_2'],
                    key="color_2"
                )
            with col3:
                config.rail.colors['rank_3'] = st.color_picker(
                    "3위",
                    value=config.rail.colors['rank_3'],
                    key="color_3"
                )
            with col4:
                config.rail.colors['default'] = st.color_picker(
                    "4위+",
                    value=config.rail.colors['default'],
                    key="color_default"
                )

    with st.expander("📢 상단 헤더", expanded=False):
        config.header.enabled = st.checkbox(
            "헤더 활성화",
            value=config.header.enabled,
            key="header_enabled"
        )

        if config.header.enabled:
            config.header.main_title['text'] = st.text_input(
                "메인 제목",
                value=config.header.main_title['text'],
                key="header_main_text"
            )

            config.header.main_title['font_size'] = st.slider(
                "메인 폰트 크기",
                min_value=40,
                max_value=100,
                value=config.header.main_title['font_size'],
                key="header_main_size"
            )

            config.header.main_title['color'] = st.color_picker(
                "메인 색상",
                value=config.header.main_title['color'],
                key="header_main_color"
            )

    st.markdown("---")

    # 템플릿 저장
    if st.button("💾 템플릿 저장", use_container_width=True):
        save_name = st.text_input("템플릿 이름", placeholder="my_template")
        if save_name:
            config_manager.save_custom_template(save_name, config)
            st.success(f"✅ '{save_name}' 저장 완료!")


# ============================================================
# 메인 영역: 탭
# ============================================================
st.title("🎬 YouTube 쇼츠 자동 생성기")
st.markdown("템플릿 커스터마이징부터 쇼츠 생성까지 한번에!")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📤 영상 업로드", "👁️ 미리보기", "🎬 생성 & 결과"])


# ============================================================
# Tab 1: 영상 업로드
# ============================================================
with tab1:
    st.header("1️⃣ 영상 업로드 방식 선택")

    upload_mode = st.radio(
        "업로드 방식",
        ["📋 CSV + 비디오 클립", "📁 폴더에서 불러오기"],
        horizontal=True
    )

    st.markdown("---")

    if upload_mode == "📋 CSV + 비디오 클립":
        st.subheader("CSV 파일 업로드")
        st.info("필수 컬럼: rank, title / 선택: emoji, score")

        csv_file = st.file_uploader(
            "CSV 파일",
            type=['csv'],
            key="csv_uploader"
        )

        if csv_file:
            df = pd.read_csv(csv_file)
            st.success(f"✅ CSV 로드: {len(df)}개 항목")
            st.dataframe(df, use_container_width=True)

            st.subheader("비디오 클립 업로드")
            st.info("각 순위에 해당하는 비디오 클립을 업로드하세요")

            uploaded_clips = {}
            cols = st.columns(5)

            for idx, row in df.iterrows():
                rank = int(row['rank'])
                with cols[idx % 5]:
                    st.write(f"**#{rank}**")
                    st.caption(row['title'][:20] + "..." if len(row['title']) > 20 else row['title'])

                    video_file = st.file_uploader(
                        f"클립 {rank}",
                        type=['mp4', 'mov', 'avi'],
                        key=f"clip_{rank}",
                        label_visibility="collapsed"
                    )

                    if video_file:
                        # 임시 저장
                        temp_path = f"temp_upload/clip_{rank}.mp4"
                        os.makedirs("temp_upload", exist_ok=True)
                        with open(temp_path, 'wb') as f:
                            f.write(video_file.read())
                        uploaded_clips[rank] = temp_path
                        st.success("✅")

            # 세션에 저장
            if uploaded_clips:
                st.session_state.uploaded_files = {
                    'mode': 'csv',
                    'csv_data': df,
                    'clips': uploaded_clips
                }

                if len(uploaded_clips) == len(df):
                    st.success(f"✅ 모든 클립 업로드 완료 ({len(uploaded_clips)}개)")
                else:
                    st.warning(f"⚠️ {len(uploaded_clips)}/{len(df)} 클립 업로드됨")

    else:  # 폴더 모드
        st.subheader("비디오 파일 업로드")
        st.info("여러 개의 비디오 파일을 한번에 업로드하세요")

        uploaded_videos = st.file_uploader(
            "비디오 파일들",
            type=['mp4', 'mov', 'avi'],
            accept_multiple_files=True,
            key="folder_uploader"
        )

        if uploaded_videos:
            st.success(f"✅ {len(uploaded_videos)}개 파일 업로드")

            # 임시 저장
            temp_folder = "temp_upload/folder"
            os.makedirs(temp_folder, exist_ok=True)

            saved_files = []
            for video_file in uploaded_videos:
                temp_path = os.path.join(temp_folder, video_file.name)
                with open(temp_path, 'wb') as f:
                    f.write(video_file.read())
                saved_files.append(temp_path)

            # 제목 생성 모드
            title_mode = st.radio(
                "제목 생성 방식",
                ["local", "ai"],
                format_func=lambda x: "파일명에서 추출" if x == "local" else "AI 자동 생성",
                horizontal=True,
                key="title_mode"
            )

            # 세션에 저장
            st.session_state.uploaded_files = {
                'mode': 'folder',
                'files': saved_files,
                'title_mode': title_mode
            }

            # 미리보기
            with st.expander("📋 업로드된 파일 목록"):
                for i, f in enumerate(uploaded_videos, 1):
                    st.write(f"{i}. {f.name} ({f.size / 1024 / 1024:.2f} MB)")


# ============================================================
# Tab 2: 미리보기
# ============================================================
with tab2:
    st.header("👁️ 템플릿 미리보기")

    st.subheader("샘플 데이터 입력")

    # 활성 순위
    preview_rank = st.selectbox(
        "현재 활성 순위",
        list(range(1, 6)),
        index=2,
        key="preview_rank"
    )

    # 샘플 제목들
    st.write("**순위별 제목** (1~5위)")
    sample_titles = {}
    cols = st.columns(5)

    for i in range(1, 6):
        with cols[i-1]:
            title = st.text_input(
                f"{i}위",
                value=f"샘플 제목 {i}",
                key=f"sample_title_{i}",
                label_visibility="visible"
            )
            sample_titles[i] = title

    if st.button("🔄 미리보기 생성", type="primary", use_container_width=True):
        with st.spinner("미리보기 생성 중..."):
            try:
                engine = TemplateEngine(config=config, aspect_ratio="9:16")

                rail_path = engine.draw_ranking_rail(
                    max_rank=5,
                    active_rank=preview_rank,
                    titles=sample_titles
                )

                st.session_state.preview_image = rail_path
                st.success("✅ 미리보기 생성 완료!")

            except Exception as e:
                st.error(f"❌ 미리보기 생성 실패: {e}")

    # 미리보기 이미지 표시
    if st.session_state.preview_image and os.path.exists(st.session_state.preview_image):
        st.image(
            st.session_state.preview_image,
            caption=f"활성 순위: {preview_rank}위",
            use_container_width=True
        )
    else:
        st.info("👆 위에서 설정을 조정하고 '미리보기 생성'을 클릭하세요")


# ============================================================
# Tab 3: 생성 & 결과
# ============================================================
with tab3:
    st.header("🎬 쇼츠 생성")

    # 업로드 확인
    if not st.session_state.uploaded_files:
        st.warning("⚠️ 먼저 '📤 영상 업로드' 탭에서 영상을 업로드하세요")
    else:
        upload_info = st.session_state.uploaded_files

        # 업로드 정보 표시
        if upload_info['mode'] == 'csv':
            st.info(f"📋 CSV 모드: {len(upload_info['clips'])}개 클립")
        else:
            st.info(f"📁 폴더 모드: {len(upload_info['files'])}개 파일 | 제목: {upload_info['title_mode']}")

        # 생성 옵션
        col1, col2 = st.columns(2)
        with col1:
            enable_rail = st.checkbox("숫자 레일 활성화", value=True)
        with col2:
            enable_intro = st.checkbox("인트로 화면 활성화", value=False)

        # 생성 버튼
        if st.button("🎬 쇼츠 생성 시작!", type="primary", use_container_width=True):
            with st.spinner("쇼츠 생성 중... 잠시만 기다려주세요"):
                try:
                    # 출력 디렉토리
                    output_dir = "output/web_generated"
                    os.makedirs(output_dir, exist_ok=True)

                    # 프로그레스바
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Generator 생성 (커스텀 config 사용)
                    generator = RankingShortsGenerator(style="modern", aspect_ratio="9:16")
                    # TODO: config를 generator에 전달하는 방법 필요

                    if upload_info['mode'] == 'csv':
                        # CSV 모드
                        status_text.text("CSV 데이터 준비 중...")
                        progress_bar.progress(10)

                        # CSV를 임시로 저장
                        temp_csv = "temp_upload/data.csv"
                        df = upload_info['csv_data']

                        # clip_path 컬럼 추가
                        df['clip_path'] = df['rank'].apply(lambda r: upload_info['clips'].get(r, ''))
                        df.to_csv(temp_csv, index=False)

                        status_text.text("쇼츠 생성 중...")
                        progress_bar.progress(30)

                        # 생성
                        final_video = generator.generate_from_csv(
                            csv_path=temp_csv,
                            output_dir=output_dir,
                            enable_rail=enable_rail,
                            enable_intro=enable_intro
                        )

                    else:
                        # 폴더 모드
                        status_text.text("비디오 파일 처리 중...")
                        progress_bar.progress(10)

                        # 폴더 생성 및 파일 복사
                        temp_folder = "temp_upload/folder_final"
                        os.makedirs(temp_folder, exist_ok=True)

                        for src in upload_info['files']:
                            dst = os.path.join(temp_folder, os.path.basename(src))
                            shutil.copy(src, dst)

                        status_text.text("쇼츠 생성 중...")
                        progress_bar.progress(30)

                        # 생성
                        final_video = generator.generate_from_dir(
                            input_dir=temp_folder,
                            output_dir=output_dir,
                            top=len(upload_info['files']),
                            order='desc',  # 기본 카운트다운
                            title_mode=upload_info['title_mode'],
                            enable_rail=enable_rail,
                            enable_intro=enable_intro
                        )

                    progress_bar.progress(100)
                    status_text.text("✅ 완료!")

                    # 결과 저장
                    st.session_state.output_video = final_video

                    st.success("🎉 쇼츠 생성 완료!")
                    st.balloons()

                except Exception as e:
                    st.error(f"❌ 생성 실패: {e}")
                    import traceback
                    st.code(traceback.format_exc())

    st.markdown("---")

    # 결과 표시
    if st.session_state.output_video and os.path.exists(st.session_state.output_video):
        st.header("📊 생성 결과")

        # 비디오 정보
        col1, col2, col3 = st.columns(3)

        with col1:
            size = os.path.getsize(st.session_state.output_video)
            st.metric("파일 크기", f"{size / 1024 / 1024:.2f} MB")

        with col2:
            # ffprobe로 길이 확인
            import subprocess
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', st.session_state.output_video],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                st.metric("길이", f"{duration:.1f}초")

        with col3:
            st.metric("해상도", "1080x1920")

        # 비디오 플레이어
        st.video(st.session_state.output_video)

        # 다운로드 버튼
        with open(st.session_state.output_video, 'rb') as f:
            st.download_button(
                label="📥 쇼츠 다운로드",
                data=f,
                file_name="my_ranking_shorts.mp4",
                mime="video/mp4",
                use_container_width=True,
                type="primary"
            )


# ============================================================
# 푸터
# ============================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🎬 YouTube 쇼츠 자동 생성기 v2.0 | Made with ❤️</p>
</div>
""", unsafe_allow_html=True)
