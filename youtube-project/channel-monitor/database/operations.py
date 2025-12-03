"""
데이터베이스 CRUD 작업 헬퍼 함수
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
import json

from database.schema import get_connection


# ============================================================================
# Accounts
# ============================================================================

def add_account(account_name: str, email: str, token_file_path: str) -> int:
    """계정 추가"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO accounts (account_name, email, token_file_path, updated_at)
        VALUES (?, ?, ?, ?)
    """, (account_name, email, token_file_path, datetime.now()))

    account_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return account_id


def get_account(account_name: str) -> Optional[Dict]:
    """계정 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts WHERE account_name = ?", (account_name,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def get_all_accounts() -> List[Dict]:
    """모든 계정 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ============================================================================
# Channels
# ============================================================================

def add_or_update_channel(channel_data: Dict) -> int:
    """채널 추가 또는 업데이트"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO channels (
            channel_id, account_id, channel_name, description, published_at,
            thumbnail_url, subscriber_count, video_count, view_count,
            country, custom_url, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(channel_id) DO UPDATE SET
            channel_name = excluded.channel_name,
            description = excluded.description,
            thumbnail_url = excluded.thumbnail_url,
            subscriber_count = excluded.subscriber_count,
            video_count = excluded.video_count,
            view_count = excluded.view_count,
            updated_at = excluded.updated_at
    """, (
        channel_data['channel_id'],
        channel_data['account_id'],
        channel_data.get('channel_name'),
        channel_data.get('description'),
        channel_data.get('published_at'),
        channel_data.get('thumbnail_url'),
        channel_data.get('subscriber_count'),
        channel_data.get('video_count'),
        channel_data.get('view_count'),
        channel_data.get('country'),
        channel_data.get('custom_url'),
        datetime.now()
    ))

    conn.commit()
    channel_id = cursor.lastrowid
    conn.close()

    return channel_id


def get_channel(channel_id: str) -> Optional[Dict]:
    """채널 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM channels WHERE channel_id = ?", (channel_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def get_channels_by_account(account_id: int) -> List[Dict]:
    """계정별 채널 목록 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM channels WHERE account_id = ?", (account_id,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_all_channels() -> List[Dict]:
    """모든 채널 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM channels ORDER BY subscriber_count DESC")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ============================================================================
# Videos
# ============================================================================

def add_or_update_video(video_data: Dict) -> int:
    """영상 추가 또는 업데이트"""
    conn = get_connection()
    cursor = conn.cursor()

    # tags를 JSON 문자열로 변환
    tags_json = json.dumps(video_data.get('tags', []))

    cursor.execute("""
        INSERT INTO videos (
            video_id, channel_id, title, description, published_at,
            thumbnail_url, duration_seconds, category_id, tags,
            view_count, like_count, comment_count, privacy_status,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(video_id) DO UPDATE SET
            title = excluded.title,
            description = excluded.description,
            thumbnail_url = excluded.thumbnail_url,
            duration_seconds = excluded.duration_seconds,
            tags = excluded.tags,
            view_count = excluded.view_count,
            like_count = excluded.like_count,
            comment_count = excluded.comment_count,
            privacy_status = excluded.privacy_status,
            updated_at = excluded.updated_at
    """, (
        video_data['video_id'],
        video_data['channel_id'],
        video_data.get('title'),
        video_data.get('description'),
        video_data.get('published_at'),
        video_data.get('thumbnail_url'),
        video_data.get('duration_seconds'),
        video_data.get('category_id'),
        tags_json,
        video_data.get('view_count'),
        video_data.get('like_count'),
        video_data.get('comment_count'),
        video_data.get('privacy_status'),
        datetime.now()
    ))

    conn.commit()
    video_id = cursor.lastrowid
    conn.close()

    return video_id


def get_video(video_id: str) -> Optional[Dict]:
    """영상 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        video = dict(row)
        # JSON tags를 파싱
        if video.get('tags'):
            video['tags'] = json.loads(video['tags'])
        return video
    return None


def get_videos_by_channel(channel_id: str, limit: int = 100) -> List[Dict]:
    """채널별 영상 목록 조회 (최신순)"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM videos
        WHERE channel_id = ?
        ORDER BY published_at DESC
        LIMIT ?
    """, (channel_id, limit))

    rows = cursor.fetchall()
    conn.close()

    videos = []
    for row in rows:
        video = dict(row)
        if video.get('tags'):
            video['tags'] = json.loads(video['tags'])
        videos.append(video)

    return videos


def get_recent_videos(days: int = 7, limit: int = 50) -> List[Dict]:
    """최근 N일 이내 업로드된 영상 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM videos
        WHERE published_at >= date('now', '-' || ? || ' days')
        ORDER BY published_at DESC
        LIMIT ?
    """, (days, limit))

    rows = cursor.fetchall()
    conn.close()

    videos = []
    for row in rows:
        video = dict(row)
        if video.get('tags'):
            video['tags'] = json.loads(video['tags'])
        videos.append(video)

    return videos


# ============================================================================
# Video Snapshots
# ============================================================================

def add_video_snapshot(video_id: str, snapshot_date: date, view_count: int,
                      like_count: int, comment_count: int):
    """영상 스냅샷 추가 (일일 통계)"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO video_snapshots (
            video_id, snapshot_date, view_count, like_count, comment_count
        ) VALUES (?, ?, ?, ?, ?)
    """, (video_id, snapshot_date, view_count, like_count, comment_count))

    conn.commit()
    conn.close()


# ============================================================================
# Analytics - Video Daily
# ============================================================================

def add_video_analytics(video_id: str, date_value: date, analytics_data: Dict):
    """영상 Analytics 데이터 추가"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO video_analytics_daily (
            video_id, date, views, estimated_minutes_watched,
            average_view_duration_seconds, average_view_percentage,
            likes, comments, shares, subscribers_gained, subscribers_lost,
            card_clicks, card_impressions
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        video_id,
        date_value,
        analytics_data.get('views', 0),
        analytics_data.get('estimated_minutes_watched', 0),
        analytics_data.get('average_view_duration_seconds', 0),
        analytics_data.get('average_view_percentage', 0),
        analytics_data.get('likes', 0),
        analytics_data.get('comments', 0),
        analytics_data.get('shares', 0),
        analytics_data.get('subscribers_gained', 0),
        analytics_data.get('subscribers_lost', 0),
        analytics_data.get('card_clicks', 0),
        analytics_data.get('card_impressions', 0)
    ))

    conn.commit()
    conn.close()


def get_video_analytics(video_id: str, start_date: date, end_date: date) -> List[Dict]:
    """영상 Analytics 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM video_analytics_daily
        WHERE video_id = ? AND date BETWEEN ? AND ?
        ORDER BY date
    """, (video_id, start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ============================================================================
# Analytics - Channel Daily
# ============================================================================

def add_channel_analytics(channel_id: str, date_value: date, analytics_data: Dict):
    """채널 Analytics 데이터 추가"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO channel_analytics_daily (
            channel_id, date, views, estimated_minutes_watched,
            average_view_duration_seconds, likes, comments, shares,
            subscribers_gained, subscribers_lost
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        channel_id,
        date_value,
        analytics_data.get('views', 0),
        analytics_data.get('estimated_minutes_watched', 0),
        analytics_data.get('average_view_duration_seconds', 0),
        analytics_data.get('likes', 0),
        analytics_data.get('comments', 0),
        analytics_data.get('shares', 0),
        analytics_data.get('subscribers_gained', 0),
        analytics_data.get('subscribers_lost', 0)
    ))

    conn.commit()
    conn.close()


def get_channel_analytics(channel_id: str, start_date: date, end_date: date) -> List[Dict]:
    """채널 Analytics 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM channel_analytics_daily
        WHERE channel_id = ? AND date BETWEEN ? AND ?
        ORDER BY date
    """, (channel_id, start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ============================================================================
# Traffic Sources (핵심!)
# ============================================================================

def add_traffic_source(channel_id: str, date_value: date, source_type: str,
                      views: int, estimated_minutes_watched: int, video_id: Optional[str] = None):
    """트래픽 소스 데이터 추가"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO traffic_sources (
            video_id, channel_id, date, source_type, views, estimated_minutes_watched
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (video_id, channel_id, date_value, source_type, views, estimated_minutes_watched))

    conn.commit()
    conn.close()


def get_traffic_sources(channel_id: str, start_date: date, end_date: date,
                       video_id: Optional[str] = None) -> List[Dict]:
    """트래픽 소스 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    if video_id:
        cursor.execute("""
            SELECT * FROM traffic_sources
            WHERE channel_id = ? AND video_id = ? AND date BETWEEN ? AND ?
            ORDER BY date, views DESC
        """, (channel_id, video_id, start_date, end_date))
    else:
        cursor.execute("""
            SELECT * FROM traffic_sources
            WHERE channel_id = ? AND video_id IS NULL AND date BETWEEN ? AND ?
            ORDER BY date, views DESC
        """, (channel_id, start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_traffic_source_summary(channel_id: str, start_date: date, end_date: date) -> List[Dict]:
    """트래픽 소스 요약 (기간별 합산)"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            source_type,
            SUM(views) as total_views,
            SUM(estimated_minutes_watched) as total_watch_time
        FROM traffic_sources
        WHERE channel_id = ? AND video_id IS NULL AND date BETWEEN ? AND ?
        GROUP BY source_type
        ORDER BY total_views DESC
    """, (channel_id, start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_video_traffic_source_summary(video_id: str, start_date: date, end_date: date) -> List[Dict]:
    """영상별 트래픽 소스 요약"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            source_type,
            SUM(views) as total_views,
            SUM(estimated_minutes_watched) as total_watch_time
        FROM traffic_sources
        WHERE video_id = ? AND date BETWEEN ? AND ?
        GROUP BY source_type
        ORDER BY total_views DESC
    """, (video_id, start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ============================================================================
# Slack Settings
# ============================================================================

def add_or_update_slack_setting(channel_id: str, webhook_url: str,
                                 urgent_alerts: bool = True,
                                 success_alerts: bool = True,
                                 daily_summary: bool = True,
                                 weekly_report: bool = True,
                                 min_interval_minutes: int = 60) -> None:
    """Slack 설정 추가 또는 업데이트"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO slack_settings (
            channel_id, slack_webhook_url,
            urgent_alerts, success_alerts, daily_summary, weekly_report,
            min_interval_minutes, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (channel_id, webhook_url, urgent_alerts, success_alerts,
          daily_summary, weekly_report, min_interval_minutes))

    conn.commit()
    conn.close()


def get_slack_setting(channel_id: str) -> Optional[Dict]:
    """Slack 설정 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM slack_settings WHERE channel_id = ?", (channel_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def delete_slack_setting(channel_id: str) -> None:
    """Slack 설정 삭제"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM slack_settings WHERE channel_id = ?", (channel_id,))

    conn.commit()
    conn.close()


# ============================================================================
# Notification History
# ============================================================================

def log_notification(channel_id: str, notification_type: str,
                    video_id: Optional[str] = None,
                    message: Optional[str] = None) -> None:
    """알림 히스토리 기록"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notification_history (channel_id, notification_type, video_id, message)
        VALUES (?, ?, ?, ?)
    """, (channel_id, notification_type, video_id, message))

    conn.commit()
    conn.close()


def check_can_send_notification(channel_id: str, notification_type: str,
                                video_id: Optional[str] = None,
                                min_interval_minutes: int = 60) -> bool:
    """
    알림 전송 가능 여부 확인 (스팸 방지)

    Args:
        channel_id: 채널 ID
        notification_type: 알림 종류 (urgent/success/daily/weekly)
        video_id: 영상 ID (영상 관련 알림인 경우)
        min_interval_minutes: 최소 간격 (분)

    Returns:
        bool: 전송 가능 여부
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 같은 종류의 알림 중 가장 최근 알림 조회
    if video_id:
        # 영상 관련 알림: 같은 영상, 같은 종류
        cursor.execute("""
            SELECT sent_at FROM notification_history
            WHERE channel_id = ? AND notification_type = ? AND video_id = ?
            ORDER BY sent_at DESC LIMIT 1
        """, (channel_id, notification_type, video_id))
    else:
        # 채널 전체 알림: 같은 종류
        cursor.execute("""
            SELECT sent_at FROM notification_history
            WHERE channel_id = ? AND notification_type = ? AND video_id IS NULL
            ORDER BY sent_at DESC LIMIT 1
        """, (channel_id, notification_type))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return True  # 이전 알림 없음

    last_sent = datetime.fromisoformat(row[0])
    elapsed_minutes = (datetime.now() - last_sent).total_seconds() / 60

    return elapsed_minutes >= min_interval_minutes


def get_notification_history(channel_id: str, limit: int = 100) -> List[Dict]:
    """알림 히스토리 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM notification_history
        WHERE channel_id = ?
        ORDER BY sent_at DESC LIMIT ?
    """, (channel_id, limit))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
