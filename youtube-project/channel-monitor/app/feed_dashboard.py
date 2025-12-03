"""
구독 채널 피드 대시보드
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.feed_operations import (
    get_all_subscribed_channels,
    get_feed_videos,
    get_feed_stats,
    update_channel_active_status
)
from collectors.feed_collector import FeedCollector


# 페이지 설정
st.set_page_config(
    page_title="구독 채널 피드",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 사이드바: 설정
# ============================================================

def render_sidebar():
    """사이드바 렌더링"""

    st.sidebar.title("⚙️ 설정")

    # 통계
    st.sidebar.subheader("📊 통계")
    stats = get_feed_stats()

    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("활성 채널", f"{stats['active_channels']}개")
        st.metric("쇼츠", f"{stats['shorts_count']}개")
    with col2:
        st.metric("전체 영상", f"{stats['total_videos']}개")
        st.metric("롱폼", f"{stats['longform_count']}개")

    if stats['new_videos']:
        st.sidebar.success(f"🆕 새 영상 {stats['new_videos']}개")

    # 마지막 수집 시간
    if stats['last_collected']:
        last_time = datetime.fromisoformat(stats['last_collected'])
        time_ago = datetime.now() - last_time
        hours_ago = int(time_ago.total_seconds() / 3600)

        if hours_ago < 1:
            minutes_ago = int(time_ago.total_seconds() / 60)
            st.sidebar.caption(f"⏰ 마지막 수집: {minutes_ago}분 전")
        elif hours_ago < 24:
            st.sidebar.caption(f"⏰ 마지막 수집: {hours_ago}시간 전")
        else:
            days_ago = int(time_ago.total_seconds() / 86400)
            st.sidebar.caption(f"⏰ 마지막 수집: {days_ago}일 전")

    st.sidebar.divider()

    # 새로고침 버튼
    st.sidebar.subheader("🔄 수집")

    if st.sidebar.button("🔄 지금 새로고침", type="primary", use_container_width=True):
        with st.spinner("영상 수집 중... (1-2분 소요)"):
            try:
                collector = FeedCollector(account_name='account1')
                result = collector.collect_feed_videos(max_videos_per_channel=30)

                st.sidebar.success(f"✅ 수집 완료!")
                st.sidebar.info(f"새 영상: {result['new_videos_count']}개")
                st.sidebar.info(f"API Quota: {result['api_quota_used']} units")

                # 페이지 새로고침
                time.sleep(1)
                st.rerun()

            except Exception as e:
                st.sidebar.error(f"❌ 에러: {e}")

    st.sidebar.caption("💡 하루 1회 자동 수집 권장")
    st.sidebar.caption("📊 예상 사용량: ~245 units (2.5%)")

    st.sidebar.divider()

    # 채널 관리
    with st.sidebar.expander("📺 채널 관리", expanded=False):
        st.caption("수집할 채널을 선택하세요")

        channels = get_all_subscribed_channels()

        # 전체 선택/해제
        col1, col2 = st.columns(2)
        with col1:
            if st.button("전체 선택", use_container_width=True):
                for channel in channels:
                    update_channel_active_status(channel['channel_id'], True)
                st.rerun()
        with col2:
            if st.button("전체 해제", use_container_width=True):
                for channel in channels:
                    update_channel_active_status(channel['channel_id'], False)
                st.rerun()

        st.divider()

        # 채널 목록
        for channel in channels:
            is_active = channel['is_active']
            new_active = st.checkbox(
                channel['channel_name'],
                value=bool(is_active),
                key=f"channel_{channel['channel_id']}"
            )

            if new_active != bool(is_active):
                update_channel_active_status(channel['channel_id'], new_active)
                # st.rerun()  # 너무 자주 리로드되면 불편하므로 제거


# ============================================================
# 메인: 피드 뷰
# ============================================================

def format_duration(seconds: int) -> str:
    """초를 MM:SS 또는 HH:MM:SS로 변환"""
    if seconds < 60:
        return f"0:{seconds:02d}"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"


def format_number(num: int) -> str:
    """숫자를 1.2K, 1.2M 형태로 변환"""
    if num < 1000:
        return str(num)
    elif num < 1000000:
        return f"{num/1000:.1f}K"
    else:
        return f"{num/1000000:.1f}M"


def format_time_ago(published_at_str: str) -> str:
    """업로드 시간을 '2시간 전' 형태로 변환"""
    try:
        published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
        now = datetime.now(published_at.tzinfo)
        delta = now - published_at

        if delta.days > 365:
            years = delta.days // 365
            return f"{years}년 전"
        elif delta.days > 30:
            months = delta.days // 30
            return f"{months}개월 전"
        elif delta.days > 0:
            return f"{delta.days}일 전"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours}시간 전"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes}분 전"
        else:
            return "방금 전"
    except:
        return ""


def render_video_card(video, channel_name, key_prefix=""):
    """영상 카드 렌더링"""

    # 썸네일 열 + 정보 열
    col1, col2 = st.columns([1, 3])

    with col1:
        # 썸네일
        if video['thumbnail_url']:
            st.image(video['thumbnail_url'], use_container_width=True)

    with col2:
        # 제목 + 배지
        title = video['title']
        badge = "📱 쇼츠" if video['is_short'] else "🎬 롱폼"

        st.markdown(f"**{title}** `{badge}`")

        # 채널명
        st.caption(f"📺 {channel_name}")

        # 통계
        view_count = format_number(video['view_count'])
        like_count = format_number(video['like_count'])
        comment_count = format_number(video['comment_count'])
        duration = format_duration(video['duration'])
        time_ago = format_time_ago(video['published_at'])

        stats_text = f"👁 {view_count} · 👍 {like_count} · 💬 {comment_count} · ⏱ {duration} · 🕐 {time_ago}"
        st.caption(stats_text)

        # 새 영상 표시
        if video['is_new']:
            st.caption("🆕 새 영상")

        # 버튼들
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            youtube_url = f"https://www.youtube.com/watch?v={video['video_id']}"
            st.link_button("▶️ YouTube에서 보기", youtube_url, use_container_width=True)
        with col_btn2:
            if st.button("📝 자막 다운로드", key=f"{key_prefix}_transcript_{video['video_id']}", use_container_width=True):
                st.info("자막 다운로드 기능은 곧 구현됩니다")


def render_feed():
    """피드 메인 뷰"""

    st.title("📺 구독 채널 피드")

    # 탭: 전체 / 롱폼 / 쇼츠
    tab1, tab2, tab3 = st.tabs(["🎬 롱폼", "📱 쇼츠", "📋 전체"])

    # 필터
    st.subheader("🔍 필터")

    col1, col2, col3 = st.columns(3)

    with col1:
        date_filter = st.selectbox(
            "기간",
            ["전체", "오늘", "어제", "지난 7일", "지난 30일"],
            index=2  # 기본: 어제
        )

    with col2:
        sort_by = st.selectbox(
            "정렬",
            ["최신순", "조회수순", "좋아요순", "댓글수순"],
            index=0  # 기본: 최신순
        )

    with col3:
        show_new_only = st.checkbox("🆕 새 영상만", value=False)

    st.divider()

    # 날짜 필터 변환
    days = None
    if date_filter == "오늘":
        days = 1
    elif date_filter == "어제":
        days = 2
    elif date_filter == "지난 7일":
        days = 7
    elif date_filter == "지난 30일":
        days = 30

    # 채널 정보 미리 로드 (조인용)
    channels = {ch['channel_id']: ch['channel_name'] for ch in get_all_subscribed_channels()}

    # 탭별 렌더링
    with tab1:
        # 롱폼
        st.subheader("🎬 롱폼 영상")

        videos = get_feed_videos(
            is_short=False,
            is_new=show_new_only if show_new_only else None,
            days=days,
            limit=100
        )

        if not videos:
            st.info("영상이 없습니다")
        else:
            st.caption(f"총 {len(videos)}개 영상")

            for video in videos:
                channel_name = channels.get(video['channel_id'], '알 수 없음')
                render_video_card(video, channel_name, key_prefix="longform")
                st.divider()

    with tab2:
        # 쇼츠
        st.subheader("📱 쇼츠")

        videos = get_feed_videos(
            is_short=True,
            is_new=show_new_only if show_new_only else None,
            days=days,
            limit=100
        )

        if not videos:
            st.info("영상이 없습니다")
        else:
            st.caption(f"총 {len(videos)}개 영상")

            for video in videos:
                channel_name = channels.get(video['channel_id'], '알 수 없음')
                render_video_card(video, channel_name, key_prefix="shorts")
                st.divider()

    with tab3:
        # 전체
        st.subheader("📋 전체 영상")

        videos = get_feed_videos(
            is_new=show_new_only if show_new_only else None,
            days=days,
            limit=100
        )

        if not videos:
            st.info("영상이 없습니다")
        else:
            st.caption(f"총 {len(videos)}개 영상")

            for video in videos:
                channel_name = channels.get(video['channel_id'], '알 수 없음')
                render_video_card(video, channel_name, key_prefix="all")
                st.divider()


# ============================================================
# 메인
# ============================================================

def main():
    """메인 함수"""

    # 사이드바
    render_sidebar()

    # 메인 피드
    render_feed()


if __name__ == "__main__":
    main()
