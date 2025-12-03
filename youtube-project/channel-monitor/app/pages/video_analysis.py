"""
영상별 상세 분석 페이지
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

from database.operations import (
    get_all_channels,
    get_videos_by_channel,
    get_video_traffic_source_summary
)

# ============================================================================
# 페이지 설정
# ============================================================================

st.set_page_config(
    page_title="영상 상세 분석",
    page_icon="🎬",
    layout="wide"
)

st.markdown("# 🎬 영상 상세 분석")
st.markdown("특정 영상의 상세 성과를 분석합니다.")

# ============================================================================
# 헬퍼 함수
# ============================================================================

@st.cache_data(ttl=300)
def load_channels():
    """채널 목록 조회"""
    return get_all_channels()


@st.cache_data(ttl=300)
def load_channel_videos(channel_id, limit=100):
    """채널의 영상 조회"""
    return get_videos_by_channel(channel_id, limit=limit)


@st.cache_data(ttl=300)
def load_video_traffic(video_id, days=30):
    """영상의 트래픽 소스 조회"""
    end_date = date.today() - timedelta(days=2)
    start_date = end_date - timedelta(days=days)
    return get_video_traffic_source_summary(video_id, start_date, end_date)


# ============================================================================
# 사이드바
# ============================================================================

channels = load_channels()

if not channels:
    st.error("채널 데이터가 없습니다.")
    st.stop()

channel_options = {ch['channel_name']: ch['channel_id'] for ch in channels}
selected_channel_name = st.sidebar.selectbox(
    "채널 선택",
    options=list(channel_options.keys()),
    index=0
)

selected_channel_id = channel_options[selected_channel_name]

# 영상 목록 조회
videos = load_channel_videos(selected_channel_id, limit=100)

if not videos:
    st.error("영상이 없습니다.")
    st.stop()

# 영상 선택
video_options = {f"{v['title'][:50]} ({v['published_at'][:10]})": v['video_id'] for v in videos}
selected_video_title = st.sidebar.selectbox(
    "영상 선택",
    options=list(video_options.keys()),
    index=0
)

selected_video_id = video_options[selected_video_title]
selected_video = next(v for v in videos if v['video_id'] == selected_video_id)

# 기간 선택
days_range = st.sidebar.selectbox(
    "분석 기간",
    options=[7, 14, 30, 90],
    format_func=lambda x: f"최근 {x}일",
    index=2  # 기본 30일
)

# ============================================================================
# 메인 화면
# ============================================================================

st.markdown(f"## {selected_video['title']}")

# 기본 정보
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("조회수", f"{selected_video['view_count']:,}")

with col2:
    st.metric("좋아요", f"{selected_video['like_count']:,}")

with col3:
    st.metric("댓글", f"{selected_video['comment_count']:,}")

with col4:
    duration_formatted = f"{selected_video['duration_seconds']//60}:{selected_video['duration_seconds']%60:02d}"
    st.metric("길이", duration_formatted)

st.markdown("---")

# 추가 정보
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"**업로드 날짜**: {selected_video['published_at'][:10]}")

with col2:
    like_rate = (selected_video['like_count'] / selected_video['view_count'] * 100) if selected_video['view_count'] > 0 else 0
    st.markdown(f"**좋아요율**: {like_rate:.2f}%")

with col3:
    st.markdown(f"**영상 ID**: `{selected_video['video_id']}`")

# YouTube 링크
st.markdown(f"[📺 YouTube에서 보기](https://youtube.com/watch?v={selected_video['video_id']})")

st.markdown("---")

# ============================================================================
# 트래픽 소스 분석
# ============================================================================

st.markdown(f"### 🚪 트래픽 소스 분석 (최근 {days_range}일)")

traffic_sources = load_video_traffic(selected_video_id, days=days_range)

if traffic_sources:
    # 소스명 한글화
    source_names_kr = {
        'YT_SEARCH': 'YouTube 검색',
        'RELATED_VIDEO': '추천 영상 (알고리즘!)',
        'SUBSCRIBER': '구독 피드',
        'EXTERNAL': '외부 링크',
        'PLAYLIST': '재생목록',
        'NOTIFICATION': '알림',
        'BROWSE': '탐색',
        'SHORTS': 'Shorts',
        'YT_CHANNEL': '채널 페이지'
    }

    df_traffic = pd.DataFrame(traffic_sources)
    df_traffic['source_name_kr'] = df_traffic['source_type'].map(
        lambda x: source_names_kr.get(x, x)
    )

    total_views = df_traffic['total_views'].sum()
    df_traffic['percentage'] = (df_traffic['total_views'] / total_views * 100).round(1)

    col1, col2 = st.columns([1, 1])

    with col1:
        # 파이 차트
        fig_pie = px.pie(
            df_traffic,
            values='total_views',
            names='source_name_kr',
            title='트래픽 소스 분포'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown("**소스별 상세**")

        for _, row in df_traffic.iterrows():
            st.markdown(
                f"**{row['source_name_kr']}**: {row['total_views']:,}회 ({row['percentage']:.1f}%)"
            )

        # 인사이트
        st.markdown("---")
        st.markdown("**💡 인사이트**")

        related_pct = df_traffic[df_traffic['source_type'] == 'RELATED_VIDEO']['percentage'].sum()
        search_pct = df_traffic[df_traffic['source_type'] == 'YT_SEARCH']['percentage'].sum()

        if related_pct > 30:
            st.success(f"✅ 추천 영상 {related_pct:.1f}% - 알고리즘 선택!")
        elif related_pct > 15:
            st.info(f"📊 추천 영상 {related_pct:.1f}% - 양호")
        else:
            st.warning(f"⚠️ 추천 영상 {related_pct:.1f}% - 낮음")

        if search_pct > 40:
            st.success(f"✅ 검색 {search_pct:.1f}% - SEO 우수!")

else:
    st.info(f"최근 {days_range}일 트래픽 소스 데이터가 없습니다.")

st.markdown("---")

# ============================================================================
# 다른 영상과 비교
# ============================================================================

st.markdown("### 📊 채널 평균과 비교")

# 채널 평균 계산
df_all = pd.DataFrame(videos)
avg_views = df_all['view_count'].mean()
avg_likes = df_all['like_count'].mean()
avg_comments = df_all['comment_count'].mean()
avg_like_rate = (df_all['like_count'].sum() / df_all['view_count'].sum() * 100) if df_all['view_count'].sum() > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    views_diff = ((selected_video['view_count'] / avg_views - 1) * 100) if avg_views > 0 else 0
    st.metric(
        "조회수",
        f"{selected_video['view_count']:,}",
        delta=f"{views_diff:+.0f}% vs 평균"
    )

with col2:
    likes_diff = ((selected_video['like_count'] / avg_likes - 1) * 100) if avg_likes > 0 else 0
    st.metric(
        "좋아요",
        f"{selected_video['like_count']:,}",
        delta=f"{likes_diff:+.0f}% vs 평균"
    )

with col3:
    comments_diff = ((selected_video['comment_count'] / avg_comments - 1) * 100) if avg_comments > 0 else 0
    st.metric(
        "댓글",
        f"{selected_video['comment_count']:,}",
        delta=f"{comments_diff:+.0f}% vs 평균"
    )

with col4:
    like_rate_diff = like_rate - avg_like_rate
    st.metric(
        "좋아요율",
        f"{like_rate:.2f}%",
        delta=f"{like_rate_diff:+.2f}%p vs 평균"
    )

# ============================================================================
# 푸터
# ============================================================================

st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: gray; font-size: 0.9em;">'
    '영상별 상세 분석 | YouTube Intelligence Dashboard'
    '</div>',
    unsafe_allow_html=True
)
