# Slack 알림 시스템 설계

## 📋 요구사항

### 기본 요구사항
- 여러 YouTube 채널 지원
- 채널별로 다른 Slack 채널에 알림
- 알림 종류별 설정 (긴급만 / 모든 알림)
- 스팸 방지 (알림 빈도 제한)

### 알림 종류
1. **🚨 긴급 알림** (즉시)
   - 조회수 급락 (평균 대비 -70%)
   - 알고리즘 이탈 (추천 비율 5% 미만)

2. **✅ 성공 알림** (즉시)
   - 알고리즘 선택 (추천 비율 50% 이상)
   - 조회수 급증 (평균 대비 +200%)

3. **📊 일일 요약** (매일 오전 9시)
   - 어제 업로드된 영상 성과
   - 핵심 지표 요약

4. **📈 주간 리포트** (매주 월요일 오전 10시)
   - 지난 주 성과 요약
   - Top 3 영상
   - 다음 주 추천 업로드 시간

---

## 🏗 시스템 아키텍처

### 1. 설정 관리

#### DB 테이블 추가
```sql
-- Slack 설정 테이블
CREATE TABLE slack_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT NOT NULL,
    slack_webhook_url TEXT NOT NULL,

    -- 알림 설정
    urgent_alerts BOOLEAN DEFAULT 1,
    success_alerts BOOLEAN DEFAULT 1,
    daily_summary BOOLEAN DEFAULT 1,
    weekly_report BOOLEAN DEFAULT 1,

    -- 알림 빈도 제한
    min_interval_minutes INTEGER DEFAULT 60,  -- 같은 종류 알림 최소 간격

    -- 메타데이터
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(channel_id)
);

-- 알림 히스토리 (스팸 방지용)
CREATE TABLE notification_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT NOT NULL,
    notification_type TEXT NOT NULL,  -- urgent/success/daily/weekly
    video_id TEXT,  -- 영상 관련 알림인 경우
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT
);
```

#### 설정 파일 (대안)
```yaml
# config/slack_config.yaml
channels:
  UCmGKhWPtsKf-6pgso7PvDhQ:  # 세상발견 World Discovery
    webhook_url: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX"
    slack_channel: "#youtube-세상발견"
    alerts:
      urgent: true
      success: true
      daily_summary: true
      weekly_report: true
    rate_limit:
      min_interval_minutes: 60

  UCXXXXXXXXXXXXX:  # 다른 채널
    webhook_url: "https://hooks.slack.com/services/T00000000/B00000000/YYYYYYYYYYYY"
    slack_channel: "#youtube-channel2"
    alerts:
      urgent: true
      success: false  # 성공 알림 비활성화
      daily_summary: true
      weekly_report: false
```

---

## 📨 알림 메시지 포맷

### 1. 긴급 알림 (조회수 급락)
```python
{
    "blocks": [
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
                {"type": "mrkdwn", "text": "*채널:*\n세상발견 World Discovery"},
                {"type": "mrkdwn", "text": "*영상:*\n<https://youtube.com/watch?v=VIDEO_ID|영상 제목>"}
            ]
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*조회수:*\n5,000회"},
                {"type": "mrkdwn", "text": "*평균 대비:*\n-70% 😱"}
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*추천 조치:*\n• 제목/썸네일 수정 고려\n• 알고리즘 추천 비율: 5% (매우 낮음)"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "영상 보기"},
                    "url": "https://youtube.com/watch?v=VIDEO_ID"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "대시보드 열기"},
                    "url": "http://localhost:8503"
                }
            ]
        }
    ]
}
```

### 2. 성공 알림 (알고리즘 선택)
```python
{
    "blocks": [
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
                {"type": "mrkdwn", "text": "*채널:*\n세상발견 World Discovery"},
                {"type": "mrkdwn", "text": "*영상:*\n<https://youtube.com/watch?v=VIDEO_ID|영상 제목>"}
            ]
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*조회수:*\n50,000회"},
                {"type": "mrkdwn", "text": "*평균 대비:*\n+250% 🚀"}
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*성공 요인:*\n• 알고리즘 추천 비율: 70%\n• 좋아요율: 3.5% (평균: 2.0%)\n• 이 패턴을 다음 영상에 적용하세요!"
            }
        }
    ]
}
```

### 3. 일일 요약
```python
{
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 일일 요약 - 세상발견 World Discovery"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{datetime.now().strftime('%Y-%m-%d')} 성과*"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*총 조회수:*\n25,000회"},
                {"type": "mrkdwn", "text": "*구독자 증가:*\n+15명"},
                {"type": "mrkdwn", "text": "*알고리즘 선택률:*\n14.7%"},
                {"type": "mrkdwn", "text": "*신규 영상:*\n0개"}
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*어제 업로드된 영상:*\n없음"
            }
        }
    ]
}
```

### 4. 주간 리포트
```python
{
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📈 주간 리포트 - 세상발견 World Discovery"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*2025-10-15 ~ 2025-10-22*"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*총 조회수:*\n175,000회 (+12%)"},
                {"type": "mrkdwn", "text": "*구독자 증가:*\n+105명"},
                {"type": "mrkdwn", "text": "*신규 영상:*\n3개"},
                {"type": "mrkdwn", "text": "*평균 조회수:*\n58,333회"}
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🏆 Top 3 영상:*\n1. 영상 제목 1 - 80,000회\n2. 영상 제목 2 - 65,000회\n3. 영상 제목 3 - 30,000회"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*💡 다음 주 추천:*\n• 최적 업로드 시간: 월요일 18시\n• 추천 영상 길이: 12분 이상"
            }
        }
    ]
}
```

---

## 🔧 구현 파일 구조

```
utils/
  notification/
    __init__.py
    slack_client.py         # Slack API 클라이언트
    message_builder.py      # 메시지 포맷 생성
    rate_limiter.py         # 알림 빈도 제한

database/
  operations.py (추가)
    - add_slack_setting()
    - get_slack_setting()
    - log_notification()
    - check_can_send_notification()

config/
  slack_config.yaml         # Slack 설정 (선택)

collectors/
  alert_checker.py          # 알림 조건 체크
  daily_summary.py          # 일일 요약 생성
  weekly_report.py          # 주간 리포트 생성

scheduler/
  notification_scheduler.py # 스케줄링
```

---

## 💻 핵심 코드 예시

### 1. Slack 클라이언트
```python
# utils/notification/slack_client.py
import requests
from typing import Dict, List

class SlackNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_message(self, blocks: List[Dict]) -> bool:
        """Slack 메시지 전송"""
        payload = {"blocks": blocks}

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Slack 전송 실패: {e}")
            return False

    def send_urgent_alert(self, video_data: Dict):
        """긴급 알림 전송"""
        from .message_builder import build_urgent_alert
        blocks = build_urgent_alert(video_data)
        return self.send_message(blocks)

    def send_success_alert(self, video_data: Dict):
        """성공 알림 전송"""
        from .message_builder import build_success_alert
        blocks = build_success_alert(video_data)
        return self.send_message(blocks)
```

### 2. 알림 조건 체크
```python
# collectors/alert_checker.py
from datetime import datetime, timedelta
from database.operations import (
    get_videos_by_channel,
    get_slack_setting,
    check_can_send_notification,
    log_notification
)
from utils.notification.slack_client import SlackNotifier

def check_urgent_alerts(channel_id: str):
    """긴급 알림 체크"""
    # Slack 설정 조회
    slack_setting = get_slack_setting(channel_id)
    if not slack_setting or not slack_setting['urgent_alerts']:
        return

    # 영상 조회
    videos = get_videos_by_channel(channel_id, limit=10)
    if not videos:
        return

    # 평균 계산
    avg_views = sum(v['view_count'] for v in videos) / len(videos)

    # 최근 5개 영상 체크
    recent_videos = sorted(videos, key=lambda x: x['published_at'], reverse=True)[:5]

    for video in recent_videos:
        # 조회수 급락 감지
        if video['view_count'] < avg_views * 0.3:
            # 알림 빈도 체크
            if check_can_send_notification(
                channel_id,
                'urgent',
                video['video_id'],
                min_interval_minutes=slack_setting['min_interval_minutes']
            ):
                # Slack 전송
                notifier = SlackNotifier(slack_setting['slack_webhook_url'])
                notifier.send_urgent_alert({
                    'channel_name': '세상발견 World Discovery',
                    'video_id': video['video_id'],
                    'title': video['title'],
                    'view_count': video['view_count'],
                    'avg_views': avg_views,
                    'diff_percent': ((video['view_count'] / avg_views - 1) * 100)
                })

                # 히스토리 기록
                log_notification(channel_id, 'urgent', video['video_id'])

def run_daily_summary():
    """일일 요약 (스케줄러에서 호출)"""
    from database.operations import get_all_channels

    channels = get_all_channels()

    for channel in channels:
        slack_setting = get_slack_setting(channel['channel_id'])
        if not slack_setting or not slack_setting['daily_summary']:
            continue

        # 요약 데이터 생성
        summary_data = generate_daily_summary(channel['channel_id'])

        # Slack 전송
        notifier = SlackNotifier(slack_setting['slack_webhook_url'])
        notifier.send_daily_summary(summary_data)

        # 히스토리 기록
        log_notification(channel['channel_id'], 'daily', None)
```

### 3. 스케줄러
```python
# scheduler/notification_scheduler.py
import schedule
import time
from collectors.alert_checker import check_urgent_alerts, run_daily_summary
from collectors.weekly_report import run_weekly_report
from database.operations import get_all_channels

def check_all_channels():
    """모든 채널 긴급 알림 체크"""
    channels = get_all_channels()
    for channel in channels:
        check_urgent_alerts(channel['channel_id'])

def main():
    """스케줄러 메인"""
    # 긴급 알림: 10분마다
    schedule.every(10).minutes.do(check_all_channels)

    # 일일 요약: 매일 오전 9시
    schedule.every().day.at("09:00").do(run_daily_summary)

    # 주간 리포트: 매주 월요일 오전 10시
    schedule.every().monday.at("10:00").do(run_weekly_report)

    print("✅ Slack 알림 스케줄러 시작")

    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    main()
```

---

## 🚀 실행 방법

### 1. Slack Webhook URL 생성
1. https://api.slack.com/apps 접속
2. "Create New App" → "From scratch"
3. App 이름 입력 (예: YouTube Intelligence)
4. Workspace 선택
5. "Incoming Webhooks" 활성화
6. "Add New Webhook to Workspace"
7. 알림 받을 채널 선택 (#youtube-alerts)
8. Webhook URL 복사

### 2. 설정 추가
```bash
# config/slack_config.yaml 생성
channels:
  UCmGKhWPtsKf-6pgso7PvDhQ:
    webhook_url: "복사한 Webhook URL"
    slack_channel: "#youtube-세상발견"
    alerts:
      urgent: true
      success: true
      daily_summary: true
      weekly_report: true
```

### 3. 스케줄러 실행
```bash
# 백그라운드 실행
python scheduler/notification_scheduler.py &

# 또는 systemd 서비스 등록 (Linux)
```

---

## ⚠️ 주의사항

### 1. 알림 빈도 제한
- 같은 영상에 대한 중복 알림 방지
- 최소 간격: 60분 (설정 가능)

### 2. Webhook URL 보안
- 환경변수 사용 권장 (`SLACK_WEBHOOK_URL`)
- Git에 커밋하지 않기 (`.gitignore` 추가)

### 3. API 할당량
- 긴급 알림 체크 주기 조절 (10분 권장)
- 너무 자주 체크하면 YouTube API 할당량 초과

---

## 📊 예상 알림 빈도

### 채널 1개 기준
- 긴급 알림: 주 0-3회 (영상 성과에 따라)
- 성공 알림: 주 0-2회
- 일일 요약: 매일 1회 (오전 9시)
- 주간 리포트: 매주 1회 (월요일)

**총: 주 7-13회**

### 채널 3개 운영 시
**총: 주 21-39회**

---

## 🔄 다음 단계

1. **Phase 1** (1-2일): 기본 구현
   - Slack 클라이언트
   - 긴급/성공 알림
   - DB 테이블 추가

2. **Phase 2** (1-2일): 스케줄링
   - 일일 요약
   - 주간 리포트
   - 스케줄러 구현

3. **Phase 3** (1일): 설정 UI
   - Streamlit 설정 페이지
   - Webhook URL 입력
   - 알림 종류 ON/OFF

---

**이 설계로 구현하시겠습니까? 수정 사항이나 추가 요청이 있으면 말씀해주세요!**
