"""
Slack Message Builder (Block Kit)
"""

from typing import Dict, List
from datetime import datetime


def build_urgent_alert(data: Dict) -> List[Dict]:
    """
    긴급 알림 메시지 생성

    Args:
        data: 알림 데이터

    Returns:
        List[Dict]: Slack Block Kit 형식
    """
    video_url = f"https://youtube.com/watch?v={data['video_id']}"
    dashboard_url = "http://localhost:8503"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚨 긴급: 조회수 급락 감지"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*채널:*\n{data['channel_name']}"},
                {"type": "mrkdwn", "text": f"*영상:*\n<{video_url}|{data['title'][:60]}...>"}
            ]
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*조회수:*\n{data['view_count']:,}회"},
                {"type": "mrkdwn", "text": f"*평균 대비:*\n{data['diff_percent']:.0f}% 😱"}
            ]
        }
    ]

    # 추천 조치
    recommendations = ["• 제목/썸네일 수정 고려"]
    if 'algorithm_rate' in data and data['algorithm_rate'] < 10:
        recommendations.append(f"• 알고리즘 추천 비율: {data['algorithm_rate']:.1f}% (매우 낮음)")

    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*추천 조치:*\n" + "\n".join(recommendations)
        }
    })

    # 버튼
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "영상 보기"},
                "url": video_url
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "대시보드 열기"},
                "url": dashboard_url
            }
        ]
    })

    return blocks


def build_success_alert(data: Dict) -> List[Dict]:
    """
    성공 알림 메시지 생성

    Args:
        data: 알림 데이터

    Returns:
        List[Dict]: Slack Block Kit 형식
    """
    video_url = f"https://youtube.com/watch?v={data['video_id']}"
    dashboard_url = "http://localhost:8503"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "✅ 축하합니다! 알고리즘이 영상을 선택했습니다! 🎉"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*채널:*\n{data['channel_name']}"},
                {"type": "mrkdwn", "text": f"*영상:*\n<{video_url}|{data['title'][:60]}...>"}
            ]
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*조회수:*\n{data['view_count']:,}회"},
                {"type": "mrkdwn", "text": f"*평균 대비:*\n+{data['diff_percent']:.0f}% 🚀"}
            ]
        }
    ]

    # 성공 요인
    success_factors = []
    if 'algorithm_rate' in data:
        success_factors.append(f"• 알고리즘 추천 비율: {data['algorithm_rate']:.1f}%")
    if 'like_rate' in data and 'avg_like_rate' in data:
        success_factors.append(f"• 좋아요율: {data['like_rate']:.2f}% (평균: {data['avg_like_rate']:.2f}%)")
    success_factors.append("• 이 패턴을 다음 영상에 적용하세요!")

    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*성공 요인:*\n" + "\n".join(success_factors)
        }
    })

    # 버튼
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "영상 보기"},
                "url": video_url
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "대시보드 열기"},
                "url": dashboard_url
            }
        ]
    })

    return blocks


def build_daily_summary(data: Dict) -> List[Dict]:
    """
    일일 요약 메시지 생성

    Args:
        data: 요약 데이터

    Returns:
        List[Dict]: Slack Block Kit 형식
    """
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 일일 요약 - {data['channel_name']}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{data['date']} 성과*"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*총 조회수:*\n{data['total_views']:,}회"},
                {"type": "mrkdwn", "text": f"*구독자 증가:*\n+{data['subscribers_gained']}명"},
                {"type": "mrkdwn", "text": f"*알고리즘 선택률:*\n{data['algorithm_rate']:.1f}%"},
                {"type": "mrkdwn", "text": f"*신규 영상:*\n{len(data.get('new_videos', []))}개"}
            ]
        }
    ]

    # 신규 영상 목록
    new_videos = data.get('new_videos', [])
    if new_videos:
        video_list = "\n".join([
            f"• <https://youtube.com/watch?v={v['video_id']}|{v['title'][:50]}...> - {v['view_count']:,}회"
            for v in new_videos[:3]
        ])
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*어제 업로드된 영상:*\n{video_list}"
            }
        })
    else:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*어제 업로드된 영상:*\n없음"
            }
        })

    return blocks


def build_weekly_report(data: Dict) -> List[Dict]:
    """
    주간 리포트 메시지 생성

    Args:
        data: 리포트 데이터

    Returns:
        List[Dict]: Slack Block Kit 형식
    """
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📈 주간 리포트 - {data['channel_name']}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{data['start_date']} ~ {data['end_date']}*"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*총 조회수:*\n{data['total_views']:,}회 ({data['total_views_diff']:+.0f}%)"
                },
                {"type": "mrkdwn", "text": f"*구독자 증가:*\n+{data['subscribers_gained']}명"},
                {"type": "mrkdwn", "text": f"*신규 영상:*\n{data['new_videos_count']}개"},
                {"type": "mrkdwn", "text": f"*평균 조회수:*\n{data['avg_views']:,.0f}회"}
            ]
        }
    ]

    # Top 3 영상
    top3 = data.get('top3_videos', [])
    if top3:
        top3_text = "\n".join([
            f"{i+1}. <https://youtube.com/watch?v={v['video_id']}|{v['title'][:40]}...> - {v['view_count']:,}회"
            for i, v in enumerate(top3)
        ])
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🏆 Top 3 영상:*\n{top3_text}"
            }
        })

    # 다음 주 추천
    recommendations = []
    if 'recommended_day' in data and 'recommended_hour' in data:
        recommendations.append(f"• 최적 업로드 시간: {data['recommended_day']} {data['recommended_hour']}시")
    if 'recommended_length' in data:
        recommendations.append(f"• 추천 영상 길이: {data['recommended_length']:.0f}분 이상")

    if recommendations:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*💡 다음 주 추천:*\n" + "\n".join(recommendations)
            }
        })

    return blocks
