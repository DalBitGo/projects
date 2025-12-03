"""
YouTube Intelligence Dashboard - MVP

성장 최적화 중심 대시보드
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

from database.operations import (
    get_all_channels,
    get_all_accounts,
    get_recent_videos,
    get_channel_analytics,
    get_traffic_source_summary,
    get_video_analytics,
    get_traffic_sources
)


# ============================================================================
# 페이지 설정
# ============================================================================

st.set_page_config(
    page_title="YouTube Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# 스타일
# ============================================================================

st.markdown("""
<style>
    .main-title {
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1em;
        border-radius: 0.5em;
        margin-bottom: 1em;
    }
    .alert-urgent {
        background-color: #ffebee;
        padding: 1em;
        border-left: 4px solid #f44336;
        margin-bottom: 1em;
    }
    .alert-success {
        background-color: #e8f5e9;
        padding: 1em;
        border-left: 4px solid #4caf50;
        margin-bottom: 1em;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# 헬퍼 함수
# ============================================================================

@st.cache_data(ttl=300)  # 5분 캐시
def load_channels():
    """채널 목록 조회"""
    return get_all_channels()


@st.cache_data(ttl=300)
def load_recent_videos(days=7):
    """최근 영상 조회"""
    return get_recent_videos(days=days)


@st.cache_data(ttl=300)
def load_all_channel_videos(channel_id, limit=100):
    """채널의 모든 영상 조회"""
    from database.operations import get_videos_by_channel
    return get_videos_by_channel(channel_id, limit=limit)


@st.cache_data(ttl=300)
def load_channel_analytics_data(channel_id, days=7):
    """채널 Analytics 조회"""
    end_date = date.today() - timedelta(days=2)
    start_date = end_date - timedelta(days=days)
    return get_channel_analytics(channel_id, start_date, end_date)


@st.cache_data(ttl=300)
def load_traffic_sources_data(channel_id, days=7):
    """트래픽 소스 조회"""
    end_date = date.today() - timedelta(days=2)
    start_date = end_date - timedelta(days=days)
    return get_traffic_source_summary(channel_id, start_date, end_date)


def calculate_algorithm_score(traffic_sources):
    """알고리즘 선택률 계산"""
    total_views = sum(ts['total_views'] for ts in traffic_sources)
    if total_views == 0:
        return 0

    # RELATED_VIDEO가 알고리즘 추천
    algorithm_views = sum(
        ts['total_views'] for ts in traffic_sources
        if ts['source_type'] == 'RELATED_VIDEO'
    )

    return (algorithm_views / total_views) * 100


# ============================================================================
# 사이드바
# ============================================================================

st.sidebar.title("🎯 YouTube Intelligence")
st.sidebar.markdown("---")

# 채널 목록
channels = load_channels()

if not channels:
    st.sidebar.error("채널 데이터가 없습니다. 먼저 데이터를 수집하세요.")
    st.stop()

channel_options = {ch['channel_name']: ch['channel_id'] for ch in channels}
selected_channel_name = st.sidebar.selectbox(
    "채널 선택",
    options=list(channel_options.keys()),
    index=0
)

selected_channel_id = channel_options[selected_channel_name]
selected_channel = next(ch for ch in channels if ch['channel_id'] == selected_channel_id)

# 기간 선택
days_range = st.sidebar.selectbox(
    "기간",
    options=[7, 14, 30, 90],
    format_func=lambda x: f"최근 {x}일",
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**마지막 업데이트**")
st.sidebar.markdown(f"{selected_channel['updated_at'][:10]}")

# 새로고침 버튼
if st.sidebar.button("🔄 데이터 새로고침"):
    st.cache_data.clear()
    st.rerun()


# ============================================================================
# 메인 화면
# ============================================================================

st.markdown(f'<div class="main-title">📊 {selected_channel_name}</div>', unsafe_allow_html=True)
st.markdown(f"**채널 ID:** {selected_channel_id}")

# ============================================================================
# 1. 핵심 지표 카드
# ============================================================================

st.markdown("### 📌 핵심 지표")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="구독자",
        value=f"{selected_channel['subscriber_count']:,}",
        delta=None
    )

with col2:
    st.metric(
        label="총 영상",
        value=f"{selected_channel['video_count']:,}",
        delta=None
    )

with col3:
    st.metric(
        label="총 조회수",
        value=f"{selected_channel['view_count']:,}",
        delta=None
    )

with col4:
    # 알고리즘 선택률 계산
    traffic_sources = load_traffic_sources_data(selected_channel_id, days_range)
    algorithm_score = calculate_algorithm_score(traffic_sources)

    st.metric(
        label="알고리즘 선택률",
        value=f"{algorithm_score:.1f}%",
        delta=None,
        help="추천 영상(RELATED_VIDEO) 비율"
    )

st.markdown("---")

# ============================================================================
# 2. 액션 필요 (긴급도 자동 분류)
# ============================================================================

st.markdown("### 🎯 액션 필요")

# 전체 영상 조회 (분석용)
all_videos = load_all_channel_videos(selected_channel_id, limit=100)

if all_videos and len(all_videos) >= 3:
    df_all = pd.DataFrame(all_videos)
    df_all['published_at'] = pd.to_datetime(df_all['published_at'])

    # 좋아요율 계산
    df_all['like_rate'] = (df_all['like_count'] / df_all['view_count'].replace(0, 1)) * 100

    # 평균 지표 계산
    avg_views = df_all['view_count'].mean()
    avg_like_rate = df_all['like_rate'].mean()

    # 최근 5개 영상
    recent_5 = df_all.nlargest(5, 'published_at')

    urgent_items = []
    warning_items = []
    success_items = []

    # 🚨 긴급: 최근 영상 조회수 급락
    now = pd.Timestamp.now(tz='UTC')
    for _, video in recent_5.iterrows():
        if video['view_count'] < avg_views * 0.3 and video['view_count'] < 1000:
            pub_at = video['published_at']
            if pub_at.tz is None:
                pub_at = pub_at.tz_localize('UTC')
            days_ago = (now - pub_at).days
            urgent_items.append({
                'type': '조회수 급락',
                'title': video['title'][:50],
                'detail': f"{video['view_count']:,}회 (평균 대비 {((video['view_count']/avg_views - 1) * 100):.0f}%) | {days_ago}일 전 업로드",
                'video_id': video['video_id']
            })

    # 🚨 긴급: 좋아요율 저조
    for _, video in recent_5.iterrows():
        if video['like_rate'] < avg_like_rate * 0.5 and video['view_count'] > 100:
            warning_items.append({
                'type': '좋아요율 저조',
                'title': video['title'][:50],
                'detail': f"{video['like_rate']:.2f}% (평균: {avg_like_rate:.2f}%)",
                'video_id': video['video_id']
            })

    # ✅ 성공: 알고리즘 선택 감지 (조회수가 평균의 2배 이상)
    for _, video in recent_5.iterrows():
        if video['view_count'] > avg_views * 2:
            success_items.append({
                'type': '성과 우수',
                'title': video['title'][:50],
                'detail': f"{video['view_count']:,}회 (평균 대비 +{((video['view_count']/avg_views - 1) * 100):.0f}%)",
                'video_id': video['video_id']
            })

    # ✅ 성공: 좋아요율 우수
    for _, video in recent_5.iterrows():
        if video['like_rate'] > avg_like_rate * 1.5 and video['view_count'] > 100:
            success_items.append({
                'type': '좋아요율 우수',
                'title': video['title'][:50],
                'detail': f"{video['like_rate']:.2f}% (평균: {avg_like_rate:.2f}%)",
                'video_id': video['video_id']
            })

    # 표시
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🚨 긴급")
        if urgent_items:
            for item in urgent_items[:3]:
                with st.expander(f"{item['type']}: {item['title']}", expanded=False):
                    st.markdown(f"**상세:** {item['detail']}")
                    st.markdown(f"[영상 보기](https://youtube.com/watch?v={item['video_id']})")
        else:
            st.info("긴급 이슈 없음")

    with col2:
        st.markdown("#### ⚠️ 주의")
        if warning_items:
            for item in warning_items[:3]:
                with st.expander(f"{item['type']}: {item['title']}", expanded=False):
                    st.markdown(f"**상세:** {item['detail']}")
                    st.markdown(f"[영상 보기](https://youtube.com/watch?v={item['video_id']})")
        else:
            st.info("주의 사항 없음")

    with col3:
        st.markdown("#### ✅ 성공")
        if success_items:
            for item in success_items[:3]:
                with st.expander(f"{item['type']}: {item['title']}", expanded=False):
                    st.markdown(f"**상세:** {item['detail']}")
                    st.markdown(f"[영상 보기](https://youtube.com/watch?v={item['video_id']})")
        else:
            st.info("특별한 성과 없음")

else:
    st.info("영상 데이터 부족 (최소 3개 필요)")

st.markdown("---")

# ============================================================================
# 3. 트래픽 소스 분석 (핵심!)
# ============================================================================

st.markdown("### 🚪 트래픽 소스 분석")

if traffic_sources:
    # 파이 차트
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
        fig_pie = px.pie(
            df_traffic,
            values='total_views',
            names='source_name_kr',
            title=f'트래픽 소스 분포 (최근 {days_range}일)'
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
        subscriber_pct = df_traffic[df_traffic['source_type'] == 'SUBSCRIBER']['percentage'].sum()

        if related_pct > 30:
            st.success(f"✅ 추천 영상 {related_pct:.1f}% - 알고리즘이 적극 선택!")
        elif related_pct > 15:
            st.info(f"📊 추천 영상 {related_pct:.1f}% - 양호한 수준")
        else:
            st.warning(f"⚠️ 추천 영상 {related_pct:.1f}% - 개선 필요 (목표: 20%+)")

        if search_pct > 40:
            st.success(f"✅ 검색 {search_pct:.1f}% - SEO 최적화 우수!")

        if subscriber_pct > 30:
            st.success(f"✅ 구독 피드 {subscriber_pct:.1f}% - 충성 팬층 탄탄!")

else:
    st.info("트래픽 소스 데이터가 없습니다.")

st.markdown("---")

# ============================================================================
# 3-1. 성공 패턴 분석
# ============================================================================

st.markdown("### 🏆 성공 패턴 분석")

if all_videos and len(all_videos) >= 10:
    df_all = pd.DataFrame(all_videos)
    df_all['published_at'] = pd.to_datetime(df_all['published_at'])
    df_all['like_rate'] = (df_all['like_count'] / df_all['view_count'].replace(0, 1)) * 100

    # 업로드 시간 추출
    df_all['upload_hour'] = df_all['published_at'].dt.hour
    df_all['upload_day'] = df_all['published_at'].dt.day_name()

    # 상위 20% 영상 = 성공 영상
    threshold = df_all['view_count'].quantile(0.8)
    top_videos = df_all[df_all['view_count'] >= threshold]
    normal_videos = df_all[df_all['view_count'] < threshold]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 성공 영상 vs 일반 영상")

        # 비교 데이터프레임
        comparison_data = {
            '지표': ['평균 조회수', '평균 좋아요율', '평균 길이'],
            '성공 영상 (상위 20%)': [
                f"{top_videos['view_count'].mean():,.0f}회",
                f"{top_videos['like_rate'].mean():.2f}%",
                f"{top_videos['duration_seconds'].mean() / 60:.1f}분"
            ],
            '일반 영상': [
                f"{normal_videos['view_count'].mean():,.0f}회",
                f"{normal_videos['like_rate'].mean():.2f}%",
                f"{normal_videos['duration_seconds'].mean() / 60:.1f}분"
            ]
        }

        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)

        # 인사이트
        st.markdown("**💡 인사이트**")

        avg_length_top = top_videos['duration_seconds'].mean() / 60
        avg_length_normal = normal_videos['duration_seconds'].mean() / 60

        if avg_length_top > avg_length_normal * 1.2:
            st.success(f"✅ 긴 영상이 더 잘됨 ({avg_length_top:.1f}분 vs {avg_length_normal:.1f}분)")
        elif avg_length_top < avg_length_normal * 0.8:
            st.success(f"✅ 짧은 영상이 더 잘됨 ({avg_length_top:.1f}분 vs {avg_length_normal:.1f}분)")
        else:
            st.info(f"📊 영상 길이 영향 적음 ({avg_length_top:.1f}분 vs {avg_length_normal:.1f}분)")

        like_rate_top = top_videos['like_rate'].mean()
        like_rate_normal = normal_videos['like_rate'].mean()

        if like_rate_top > like_rate_normal * 1.3:
            st.success(f"✅ 좋아요율 높을수록 성공 ({like_rate_top:.2f}% vs {like_rate_normal:.2f}%)")

    with col2:
        st.markdown("#### 📅 최적 업로드 타이밍")

        # 요일별 평균 조회수
        day_performance = df_all.groupby('upload_day')['view_count'].mean().sort_values(ascending=False)

        # 요일 순서 정리 (한국어)
        day_order_kr = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_names_kr = {
            'Monday': '월요일',
            'Tuesday': '화요일',
            'Wednesday': '수요일',
            'Thursday': '목요일',
            'Friday': '금요일',
            'Saturday': '토요일',
            'Sunday': '일요일'
        }

        if len(day_performance) > 0:
            best_day = day_performance.index[0]
            worst_day = day_performance.index[-1]

            st.markdown(f"**✅ 최고 요일**: {day_names_kr.get(best_day, best_day)}")
            st.markdown(f"   평균 {day_performance[best_day]:,.0f}회 조회")

            st.markdown(f"**❌ 최저 요일**: {day_names_kr.get(worst_day, worst_day)}")
            st.markdown(f"   평균 {day_performance[worst_day]:,.0f}회 조회")

            # 시간대별 분석
            hour_performance = df_all.groupby('upload_hour')['view_count'].mean().sort_values(ascending=False)

            if len(hour_performance) > 0:
                best_hour = hour_performance.index[0]
                st.markdown("---")
                st.markdown(f"**⏰ 최적 시간**: {best_hour}시")
                st.markdown(f"   평균 {hour_performance[best_hour]:,.0f}회 조회")

                # 추천
                st.markdown("---")
                st.markdown("**📌 추천 업로드 시간**")
                st.info(f"{day_names_kr.get(best_day, best_day)} {best_hour}시")

else:
    st.info("성공 패턴 분석에 최소 10개 영상 필요")

st.markdown("---")

# ============================================================================
# 4. 영상 목록
# ============================================================================

st.markdown("### 📹 영상 목록")

# 탭으로 분리: 최근 영상 vs 전체 영상
tab1, tab2 = st.tabs([f"최근 {days_range}일", "전체 영상 (최근 100개)"])

# Helper function for video display
def display_videos(videos_list):
    if not videos_list:
        return None

    df = pd.DataFrame(videos_list)
    df['published_at'] = pd.to_datetime(df['published_at'])
    df['published_date'] = df['published_at'].dt.strftime('%Y-%m-%d')
    df['duration_formatted'] = df['duration_seconds'].apply(
        lambda x: f"{x//60}:{x%60:02d}" if pd.notnull(x) else "-"
    )

    # 테이블 표시
    display_df = df[['title', 'published_date', 'view_count', 'like_count', 'comment_count', 'duration_formatted']].copy()
    display_df.columns = ['제목', '업로드', '조회수', '좋아요', '댓글', '길이']
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Top 3
    st.markdown("**🏆 조회수 Top 3**")
    top3 = df.nlargest(3, 'view_count')

    for idx, row in top3.iterrows():
        with st.expander(f"#{top3.index.get_loc(idx) + 1}: {row['title'][:80]}"):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("조회수", f"{row['view_count']:,}")
            col2.metric("좋아요", f"{row['like_count']:,}")
            col3.metric("댓글", f"{row['comment_count']:,}")
            col4.metric("길이", row['duration_formatted'])

            st.markdown("---")
            st.markdown(f"**업로드:** {row['published_date']}")
            st.markdown(f"**영상 ID:** `{row['video_id']}`")

            if row['view_count'] > 0:
                like_rate = (row['like_count'] / row['view_count']) * 100
                st.markdown(f"**좋아요율:** {like_rate:.2f}%")

            st.markdown(f"[YouTube에서 보기](https://youtube.com/watch?v={row['video_id']})")

    return df

with tab1:
    recent_videos = load_recent_videos(days=days_range)
    recent_videos_filtered = [v for v in recent_videos if v['channel_id'] == selected_channel_id]

    if not recent_videos_filtered:
        st.info(f"최근 {days_range}일 이내 업로드된 영상이 없습니다.")
        st.markdown("**💡 Tip:** '전체 영상' 탭을 확인하거나 사이드바에서 기간을 90일로 변경하세요.")
    else:
        display_videos(recent_videos_filtered)

with tab2:
    all_videos = load_all_channel_videos(selected_channel_id, limit=100)

    if not all_videos:
        st.info("영상이 없습니다.")
    else:
        st.markdown(f"**총 {len(all_videos)}개 영상**")
        display_videos(all_videos)

st.markdown("---")

# ============================================================================
# 5. 일별 성과 추이
# ============================================================================

st.markdown("### 📈 일별 성과 추이")

analytics_data = load_channel_analytics_data(selected_channel_id, days=days_range)

if analytics_data:
    df_analytics = pd.DataFrame(analytics_data)

    # 날짜 파싱
    df_analytics['date_parsed'] = pd.to_datetime(df_analytics['date'])

    # 그래프
    fig_trend = go.Figure()

    fig_trend.add_trace(go.Scatter(
        x=df_analytics['date_parsed'],
        y=df_analytics['views'],
        mode='lines+markers',
        name='조회수',
        line=dict(color='#1f77b4', width=2)
    ))

    fig_trend.update_layout(
        title=f'일별 조회수 추이 (최근 {days_range}일)',
        xaxis_title='날짜',
        yaxis_title='조회수',
        hovermode='x unified'
    )

    st.plotly_chart(fig_trend, use_container_width=True)

    # 요약 통계
    col1, col2, col3 = st.columns(3)

    total_views = df_analytics['views'].sum()
    avg_views = df_analytics['views'].mean()
    total_watch_time = df_analytics['estimated_minutes_watched'].sum()

    col1.metric("총 조회수", f"{total_views:,}")
    col2.metric("일 평균 조회수", f"{avg_views:,.0f}")
    col3.metric("총 시청 시간", f"{total_watch_time:,}분")

else:
    st.info("Analytics 데이터가 없습니다.")


# ============================================================================
# 푸터
# ============================================================================

st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: gray; font-size: 0.9em;">'
    'YouTube Intelligence Dashboard v1.0 (MVP) | '
    f'Generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    '</div>',
    unsafe_allow_html=True
)
