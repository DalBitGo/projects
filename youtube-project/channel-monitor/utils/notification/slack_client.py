"""
Slack Notification Client
"""

import requests
from typing import Dict, List, Optional


class SlackNotifier:
    """Slack 알림 클라이언트"""

    def __init__(self, webhook_url: str):
        """
        Args:
            webhook_url: Slack Incoming Webhook URL
        """
        self.webhook_url = webhook_url

    def send_message(self, blocks: List[Dict]) -> bool:
        """
        Slack 메시지 전송

        Args:
            blocks: Slack Block Kit 형식의 메시지

        Returns:
            bool: 성공 여부
        """
        payload = {"blocks": blocks}

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Slack 전송 실패: {e}")
            return False

    def send_urgent_alert(self, data: Dict) -> bool:
        """
        긴급 알림 전송

        Args:
            data: 알림 데이터
                - channel_name: 채널 이름
                - video_id: 영상 ID
                - title: 영상 제목
                - view_count: 조회수
                - avg_views: 평균 조회수
                - diff_percent: 차이 비율
                - algorithm_rate: 알고리즘 추천 비율 (선택)

        Returns:
            bool: 성공 여부
        """
        from .message_builder import build_urgent_alert
        blocks = build_urgent_alert(data)
        return self.send_message(blocks)

    def send_success_alert(self, data: Dict) -> bool:
        """
        성공 알림 전송

        Args:
            data: 알림 데이터
                - channel_name: 채널 이름
                - video_id: 영상 ID
                - title: 영상 제목
                - view_count: 조회수
                - avg_views: 평균 조회수
                - diff_percent: 차이 비율
                - algorithm_rate: 알고리즘 추천 비율
                - like_rate: 좋아요율
                - avg_like_rate: 평균 좋아요율

        Returns:
            bool: 성공 여부
        """
        from .message_builder import build_success_alert
        blocks = build_success_alert(data)
        return self.send_message(blocks)

    def send_daily_summary(self, data: Dict) -> bool:
        """
        일일 요약 전송

        Args:
            data: 요약 데이터
                - channel_name: 채널 이름
                - date: 날짜
                - total_views: 총 조회수
                - subscribers_gained: 구독자 증가
                - algorithm_rate: 알고리즘 선택률
                - new_videos: 신규 영상 목록

        Returns:
            bool: 성공 여부
        """
        from .message_builder import build_daily_summary
        blocks = build_daily_summary(data)
        return self.send_message(blocks)

    def send_weekly_report(self, data: Dict) -> bool:
        """
        주간 리포트 전송

        Args:
            data: 리포트 데이터
                - channel_name: 채널 이름
                - start_date: 시작 날짜
                - end_date: 종료 날짜
                - total_views: 총 조회수
                - total_views_diff: 전주 대비 차이
                - subscribers_gained: 구독자 증가
                - new_videos_count: 신규 영상 수
                - avg_views: 평균 조회수
                - top3_videos: Top 3 영상 목록
                - recommended_day: 추천 요일
                - recommended_hour: 추천 시간

        Returns:
            bool: 성공 여부
        """
        from .message_builder import build_weekly_report
        blocks = build_weekly_report(data)
        return self.send_message(blocks)
