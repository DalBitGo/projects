"""
Slack 알림 테스트 스크립트

사용법:
1. Slack Incoming Webhook URL 생성
   - https://api.slack.com/apps
   - "Create New App" → "From scratch"
   - "Incoming Webhooks" 활성화
   - Webhook URL 복사

2. 이 스크립트 실행:
   python test_slack_notification.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.operations import (
    get_all_channels,
    add_or_update_slack_setting,
    get_slack_setting
)
from utils.notification.slack_client import SlackNotifier


def setup_slack_webhook():
    """Slack Webhook URL 설정"""
    print("=" * 60)
    print("📱 Slack 알림 설정")
    print("=" * 60)

    # 채널 목록 조회
    channels = get_all_channels()

    if not channels:
        print("❌ 채널 데이터가 없습니다. 먼저 데이터를 수집하세요.")
        print("   python collectors/collect_all.py")
        return None

    print("\n사용 가능한 채널:")
    for i, channel in enumerate(channels, 1):
        print(f"{i}. {channel['channel_name']} ({channel['channel_id']})")

    # 채널 선택
    choice = input("\n채널 번호 선택: ").strip()
    try:
        channel_idx = int(choice) - 1
        if channel_idx < 0 or channel_idx >= len(channels):
            raise ValueError
        selected_channel = channels[channel_idx]
    except:
        print("❌ 잘못된 선택입니다.")
        return None

    channel_id = selected_channel['channel_id']
    channel_name = selected_channel['channel_name']

    print(f"\n선택한 채널: {channel_name}")

    # 기존 설정 확인
    existing_setting = get_slack_setting(channel_id)
    if existing_setting:
        print(f"\n기존 Webhook URL: {existing_setting['slack_webhook_url'][:50]}...")
        update = input("업데이트하시겠습니까? (y/n): ").strip().lower()
        if update != 'y':
            return channel_id

    # Webhook URL 입력
    print("\n" + "=" * 60)
    print("Slack Incoming Webhook URL을 입력하세요.")
    print("예: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX")
    print("=" * 60)

    webhook_url = input("\nWebhook URL: ").strip()

    if not webhook_url.startswith("https://hooks.slack.com/"):
        print("❌ 올바른 Webhook URL이 아닙니다.")
        return None

    # 설정 저장
    add_or_update_slack_setting(
        channel_id=channel_id,
        webhook_url=webhook_url,
        urgent_alerts=True,
        success_alerts=True,
        daily_summary=False,  # 테스트에서는 비활성화
        weekly_report=False,
        min_interval_minutes=1  # 테스트용 짧은 간격
    )

    print(f"\n✅ Slack 설정 저장 완료: {channel_name}")
    return channel_id


def test_slack_messages(channel_id: str):
    """Slack 메시지 테스트"""
    print("\n" + "=" * 60)
    print("🧪 Slack 메시지 테스트")
    print("=" * 60)

    # Slack 설정 조회
    slack_setting = get_slack_setting(channel_id)
    if not slack_setting:
        print("❌ Slack 설정이 없습니다.")
        return

    notifier = SlackNotifier(slack_setting['slack_webhook_url'])

    # 채널 정보
    channels = get_all_channels()
    channel = next((ch for ch in channels if ch['channel_id'] == channel_id), None)
    channel_name = channel['channel_name'] if channel else 'Test Channel'

    print("\n테스트할 알림 종류:")
    print("1. 긴급 알림 (조회수 급락)")
    print("2. 성공 알림 (알고리즘 선택)")
    print("3. 일일 요약")
    print("4. 주간 리포트")
    print("5. 모두 테스트")

    choice = input("\n선택 (1-5): ").strip()

    if choice in ['1', '5']:
        print("\n📤 긴급 알림 전송 중...")
        success = notifier.send_urgent_alert({
            'channel_name': channel_name,
            'video_id': 'dQw4w9WgXcQ',
            'title': '[테스트] 조회수가 급락한 영상입니다',
            'view_count': 500,
            'avg_views': 10000,
            'diff_percent': -95,
            'algorithm_rate': 3.5
        })
        print("✅ 긴급 알림 전송 완료" if success else "❌ 긴급 알림 전송 실패")

    if choice in ['2', '5']:
        print("\n📤 성공 알림 전송 중...")
        success = notifier.send_success_alert({
            'channel_name': channel_name,
            'video_id': 'dQw4w9WgXcQ',
            'title': '[테스트] 알고리즘이 선택한 영상입니다',
            'view_count': 50000,
            'avg_views': 10000,
            'diff_percent': 400,
            'algorithm_rate': 70,
            'like_rate': 3.5,
            'avg_like_rate': 2.0
        })
        print("✅ 성공 알림 전송 완료" if success else "❌ 성공 알림 전송 실패")

    if choice in ['3', '5']:
        print("\n📤 일일 요약 전송 중...")
        success = notifier.send_daily_summary({
            'channel_name': channel_name,
            'date': '2025-10-22',
            'total_views': 25000,
            'subscribers_gained': 15,
            'algorithm_rate': 14.7,
            'new_videos': [
                {'video_id': 'test1', 'title': '[테스트] 새 영상 1', 'view_count': 5000},
                {'video_id': 'test2', 'title': '[테스트] 새 영상 2', 'view_count': 3000}
            ]
        })
        print("✅ 일일 요약 전송 완료" if success else "❌ 일일 요약 전송 실패")

    if choice in ['4', '5']:
        print("\n📤 주간 리포트 전송 중...")
        success = notifier.send_weekly_report({
            'channel_name': channel_name,
            'start_date': '2025-10-15',
            'end_date': '2025-10-22',
            'total_views': 175000,
            'total_views_diff': 12,
            'subscribers_gained': 105,
            'new_videos_count': 3,
            'avg_views': 58333,
            'top3_videos': [
                {'video_id': 'test1', 'title': '[테스트] Top 1 영상', 'view_count': 80000},
                {'video_id': 'test2', 'title': '[테스트] Top 2 영상', 'view_count': 65000},
                {'video_id': 'test3', 'title': '[테스트] Top 3 영상', 'view_count': 30000}
            ],
            'recommended_day': '월요일',
            'recommended_hour': 18,
            'recommended_length': 12
        })
        print("✅ 주간 리포트 전송 완료" if success else "❌ 주간 리포트 전송 실패")


def main():
    """메인 함수"""
    print("\n🎯 YouTube Intelligence - Slack 알림 테스트\n")

    # 1. Webhook URL 설정
    channel_id = setup_slack_webhook()

    if not channel_id:
        print("\n❌ 설정 실패")
        return

    # 2. 메시지 테스트
    test_slack_messages(channel_id)

    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)
    print("\nSlack 채널을 확인하세요.")
    print("\n다음 단계:")
    print("1. 알림 체커 실행: python collectors/alert_checker.py")
    print("2. 스케줄러 설정 (향후)")


if __name__ == "__main__":
    main()
