"""
Step 3: Streamlit Web UI
- 파일 업로드 (CSV + 비디오 클립)
- 템플릿 선택 및 커스터마이징
- 실시간 쇼츠 생성
"""
import streamlit as st
import pandas as pd
import os
import subprocess
import yaml
import tempfile
import shutil
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="YouTube 쇼츠 자동 생성기",
    page_icon="🎬",
    layout="wide"
)

def remove_emoji(text):
    """텍스트에서 이모지 제거"""
    import re
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text).strip()

def load_template(template_name):
    """템플릿 로드"""
    template_path = f"templates/{template_name}.yaml"
    with open(template_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def process_clip_with_template(clip_data, template, all_items, output_path):
    """단일 클립 처리"""
    current_rank = clip_data['rank']
    clip_path = clip_data['clip_path']

    fonts = template['fonts']
    colors = template['colors']
    positions = template['positions']
    style = template['style']
    clip_duration = template['playback']['clip_duration']

    font_path = fonts['main']

    # drawtext 필터 구성
    drawtext_filters = []

    # 상단 제목
    drawtext_filters.append(
        f"drawtext=fontfile='{font_path}':text='Ranking Random'"
        f":fontsize={fonts['title_size']}:fontcolor={colors['title']}"
        f":x={positions['title_x']}:y={positions['title_y']}"
        f":borderw={style['border_width']}:bordercolor={colors['border']}"
    )
    drawtext_filters.append(
        f"drawtext=fontfile='{font_path}':text='Impressive Moments'"
        f":fontsize={fonts['subtitle_size']}:fontcolor={colors['subtitle']}"
        f":x={positions['subtitle_x']}:y={positions['subtitle_y']}"
        f":borderw={style['border_width']}:bordercolor={colors['border']}"
    )

    # 누적 표시
    if template['playback']['order'] == "reverse":
        display_ranks = range(5, current_rank - 1, -1)
    else:
        display_ranks = range(1, current_rank + 1)

    for display_rank in display_ranks:
        if display_rank not in all_items:
            continue

        item = all_items[display_rank]
        color = colors.get(f"rank{display_rank}", "white")

        if template['playback']['order'] == "reverse":
            y_pos = positions['ranking_start_y'] + (5 - display_rank) * positions['ranking_gap']
        else:
            y_pos = positions['ranking_start_y'] + (display_rank - 1) * positions['ranking_gap']

        safe_title = item['title'].replace("'", "\\'")

        # 번호
        drawtext_filters.append(
            f"drawtext=fontfile='{font_path}':text='{display_rank}.'"
            f":fontsize={fonts['ranking_number_size']}:fontcolor={color}"
            f":x={positions['ranking_x']}:y={y_pos}"
            f":borderw={style['border_width']}:bordercolor={colors['border']}"
        )

        # 제목
        drawtext_filters.append(
            f"drawtext=fontfile='{font_path}':text='{safe_title}'"
            f":fontsize={fonts['ranking_title_size']}:fontcolor={color}"
            f":x={positions['ranking_title_x']}:y={y_pos}"
            f":borderw={style['border_width']}:bordercolor={colors['border']}"
        )

    # FFmpeg 명령
    filter_string = ",".join(drawtext_filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', clip_path,
        '-vf', filter_string,
        '-c:a', 'copy',
        '-t', str(clip_duration),
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0

def generate_shorts(csv_data, video_clips, template):
    """쇼츠 생성"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # CSV 데이터를 DataFrame으로
        df = pd.DataFrame(csv_data)

        # 재생 순서에 따라 정렬
        if template['playback']['order'] == "reverse":
            df = df.sort_values('rank', ascending=False).reset_index(drop=True)
        else:
            df = df.sort_values('rank', ascending=True).reset_index(drop=True)

        # 전체 데이터 딕셔너리
        all_items = {}
        for _, row in df.iterrows():
            all_items[row['rank']] = {
                'title': remove_emoji(row['title']),
                'clip_path': video_clips[row['rank']]
            }

        # 클립 처리
        processed_clips = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, (_, row) in enumerate(df.iterrows()):
            current_rank = row['rank']
            output_clip = os.path.join(temp_dir, f"clip_{current_rank}.mp4")

            status_text.text(f"클립 #{current_rank} 처리 중...")

            clip_data = {
                'rank': current_rank,
                'clip_path': video_clips[current_rank]
            }

            success = process_clip_with_template(clip_data, template, all_items, output_clip)

            if success:
                processed_clips.append(output_clip)

            progress_bar.progress((idx + 1) / len(df))

        if not processed_clips:
            return None

        # 클립 연결
        status_text.text("클립 연결 중...")
        concat_list_path = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_list_path, 'w') as f:
            for clip in processed_clips:
                f.write(f"file '{os.path.basename(clip)}'\n")

        final_output = os.path.join(temp_dir, "final_shorts.mp4")

        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', 'concat_list.txt',
            '-c', 'copy',
            'final_shorts.mp4'
        ]

        result = subprocess.run(cmd, capture_output=True, cwd=temp_dir)

        if result.returncode == 0 and os.path.exists(final_output):
            # 임시 파일을 영구 위치로 복사
            output_dir = "output/web_ui"
            os.makedirs(output_dir, exist_ok=True)
            permanent_path = os.path.join(output_dir, "final_shorts.mp4")
            shutil.copy(final_output, permanent_path)

            status_text.text("✅ 완료!")
            progress_bar.progress(1.0)

            return permanent_path

        return None

# UI 구성
st.title("🎬 YouTube 쇼츠 자동 생성기")
st.markdown("---")

# 사이드바 - 템플릿 설정
with st.sidebar:
    st.header("⚙️ 설정")

    # 템플릿 선택
    template_name = st.selectbox(
        "템플릿 선택",
        ["default", "modern", "minimal"],
        help="미리 정의된 템플릿을 선택하세요"
    )

    # 템플릿 로드
    template = load_template(template_name)

    st.subheader("📝 템플릿 정보")
    st.write(f"**이름:** {template['name']}")
    st.write(f"**설명:** {template['description']}")

    # 고급 설정
    with st.expander("🎨 고급 설정"):
        # 재생 순서
        order = st.radio(
            "재생 순서",
            ["reverse", "forward"],
            index=0 if template['playback']['order'] == "reverse" else 1,
            format_func=lambda x: "역순 (5→1)" if x == "reverse" else "정순 (1→5)"
        )
        template['playback']['order'] = order

        # 클립 길이
        clip_duration = st.slider(
            "클립 길이 (초)",
            min_value=3,
            max_value=15,
            value=template['playback']['clip_duration']
        )
        template['playback']['clip_duration'] = clip_duration

        # 폰트 크기
        st.write("**폰트 크기**")
        col1, col2 = st.columns(2)
        with col1:
            title_size = st.number_input("제목", value=template['fonts']['title_size'], min_value=20, max_value=100)
            template['fonts']['title_size'] = title_size
        with col2:
            ranking_size = st.number_input("랭킹", value=template['fonts']['ranking_number_size'], min_value=20, max_value=120)
            template['fonts']['ranking_number_size'] = ranking_size

# 메인 영역
tab1, tab2 = st.tabs(["📤 업로드", "📊 결과"])

with tab1:
    st.header("1️⃣ CSV 데이터 업로드")

    csv_file = st.file_uploader(
        "CSV 파일을 업로드하세요",
        type=['csv'],
        help="rank, title, emoji, score 컬럼이 필요합니다"
    )

    if csv_file:
        df = pd.read_csv(csv_file)
        st.success(f"✅ CSV 로드 성공: {len(df)}개 항목")
        st.dataframe(df)

        st.header("2️⃣ 비디오 클립 업로드")
        st.info("각 랭킹에 해당하는 비디오 클립을 업로드하세요")

        video_clips = {}

        cols = st.columns(5)
        for idx, rank in enumerate(range(1, 6)):
            with cols[idx]:
                st.subheader(f"#{rank}")
                video_file = st.file_uploader(
                    f"클립 {rank}",
                    type=['mp4', 'mov'],
                    key=f"video_{rank}"
                )

                if video_file:
                    # 임시 파일로 저장
                    temp_path = f"temp_clip_{rank}.mp4"
                    with open(temp_path, 'wb') as f:
                        f.write(video_file.read())
                    video_clips[rank] = temp_path
                    st.success("✅")

        # 생성 버튼
        if len(video_clips) == 5:
            st.markdown("---")

            if st.button("🎬 쇼츠 생성", type="primary", use_container_width=True):
                with st.spinner("생성 중..."):
                    # CSV 데이터 준비
                    csv_data = df.to_dict('records')

                    # 쇼츠 생성
                    output_path = generate_shorts(csv_data, video_clips, template)

                    if output_path:
                        st.session_state['output_path'] = output_path
                        st.success("✅ 쇼츠 생성 완료!")
                        st.balloons()
                    else:
                        st.error("❌ 생성 실패")
        else:
            st.warning(f"⚠️ 5개의 비디오 클립이 모두 필요합니다 (현재 {len(video_clips)}/5)")

with tab2:
    st.header("📊 생성 결과")

    if 'output_path' in st.session_state:
        output_path = st.session_state['output_path']

        if os.path.exists(output_path):
            # 비디오 정보
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size',
                 '-of', 'default=noprint_wrappers=1', output_path],
                capture_output=True, text=True
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                size = os.path.getsize(output_path)
                st.metric("파일 크기", f"{size / 1024 / 1024:.2f} MB")

            with col2:
                # duration 추출
                duration_line = [line for line in result.stdout.split('\n') if 'duration=' in line]
                if duration_line:
                    duration = float(duration_line[0].split('=')[1])
                    st.metric("길이", f"{duration:.1f}초")

            with col3:
                st.metric("해상도", "1080x1920")

            # 비디오 플레이어
            st.video(output_path)

            # 다운로드 버튼
            with open(output_path, 'rb') as f:
                st.download_button(
                    label="📥 다운로드",
                    data=f,
                    file_name="ranking_shorts.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
    else:
        st.info("쇼츠를 생성하면 여기에 표시됩니다")

# 푸터
st.markdown("---")
st.markdown("Made with ❤️ by YouTube Shorts Generator")
