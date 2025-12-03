"""
알림 조건 체크 및 Slack 전송
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.operations import (
    get_all_channels,
    get_videos_by_channel,
    get_slack_setting,
    check_can_send_notification,
    log_notification
)
from utils.notification.slack_client import SlackNotifier


def check_urgent_alerts(channel_id: str) -> None:
    """
    긴급 알림 체크 (조회수 급락)

    Args:
        channel_id: 채널 ID
    """
    # Slack 설정 조회
    slack_setting = get_slack_setting(channel_id)
    if not slack_setting or not slack_setting['urgent_alerts']:
        return

    # 영상 조회
    videos = get_videos_by_channel(channel_id, limit=20)
    if not videos or len(videos) < 3:
        return

    # 평균 계산
    avg_views = sum(v['view_count'] for v in videos) / len(videos)

    # 최근 5개 영상 체크
    recent_videos = sorted(videos, key=lambda x: x['published_at'], reverse=True)[:5]

    for video in recent_videos:
        # 조회수 급락 감지 (평균 대비 -70% & 1000회 미만)
        if video['view_count'] < avg_views * 0.3 and video['view_count'] < 1000:
            # 알림 빈도 체크
            if check_can_send_notification(
                channel_id,
                'urgent',
                video['video_id'],
                slack_setting['min_interval_minutes']
            ):
                # Slack 전송
                notifier = SlackNotifier(slack_setting['slack_webhook_url'])

                # 채널 이름 가져오기
                from database.operations import get_all_channels
                channels = get_all_channels()
                channel = next((ch for ch in channels if ch['channel_id'] == channel_id), None)
                channel_name = channel['channel_name'] if channel else 'Unknown'

                success = notifier.send_urgent_alert({
                    'channel_name': channel_name,
                    'video_id': video['video_id'],
                    'title': video['title'],
                    'view_count': video['view_count'],
                    'avg_views': avg_views,
                    'diff_percent': ((video['view_count'] / avg_views - 1) * 100)
                })

                if success:
                    # 히스토리 기록
                    log_notification(channel_id, 'urgent', video['video_id'], f"조회수 급락: {video['title']}")
                    print(f"✅ 긴급 알림 전송: {video['title']}")


def check_success_alerts(channel_id: str) -> None:
    """
    성공 알림 체크 (알고리즘 선택, 조회수 급증)

    Args:
        channel_id: 채널 ID
    """
    # Slack 설정 조회
    slack_setting = get_slack_setting(channel_id)
    if not slack_setting or not slack_setting['success_alerts']:
        return

    # 영상 조회
    videos = get_videos_by_channel(channel_id, limit=20)
    if not videos or len(videos) < 3:
        return

    # 평균 계산
    avg_views = sum(v['view_count'] for v in videos) / len(videos)
    total_likes = sum(v['like_count'] for v in videos)
    total_views = sum(v['view_count'] for v in videos)
    avg_like_rate = (total_likes / total_views * 100) if total_views > 0 else 0

    # 최근 5개 영상 체크
    recent_videos = sorted(videos, key=lambda x: x['published_at'], reverse=True)[:5]

    for video in recent_videos:
        # 조회수 급증 감지 (평균 대비 +200%)
        if video['view_count'] > avg_views * 2:
            # 알림 빈도 체크
            if check_can_send_notification(
                channel_id,
                'success',
                video['video_id'],
                slack_setting['min_interval_minutes']
            ):
                # Slack 전송
                notifier = SlackNotifier(slack_setting['slack_webhook_url'])

                # 채널 이름 가져오기
                from database.operations import get_all_channels
                channels = get_all_channels()
                channel = next((ch for ch in channels if ch['channel_id'] == channel_id), None)
                channel_name = channel['channel_name'] if channel else 'Unknown'

                # 좋아요율 계산
                like_rate = (video['like_count'] / video['view_count'] * 100) if video['view_count'] > 0 else 0

                success = notifier.send_success_alert({
                    'channel_name': channel_name,
                    'video_id': video['video_id'],
                    'title': video['title'],
                    'view_count': video['view_count'],
                    'avg_views': avg_views,
                    'diff_percent': ((video['view_count'] / avg_views - 1) * 100),
                    'like_rate': like_rate,
                    'avg_like_rate': avg_like_rate
                })

                if success:
                    # 히스토리 기록
                    log_notification(channel_id, 'success', video['video_id'], f"성과 우수: {video['title']}")
                    print(f"✅ 성공 알림 전송: {video['title']}")


def check_all_channels() -> None:
    """모든 채널의 긴급/성공 알림 체크"""
    channels = get_all_channels()

    for channel in channels:
        channel_id = channel['channel_id']
        print(f"\n📊 채널 체크: {channel['channel_name']}")

        try:
            check_urgent_alerts(channel_id)
            check_success_alerts(channel_id)
        except Exception as e:
            print(f"❌ {channel['channel_name']} 알림 체크 중 오류: {e}")


if __name__ == "__main__":
    """테스트 실행"""
    print("🚀 알림 체커 시작\n")
    check_all_channels()
    print("\n✅ 알림 체커 완료")
