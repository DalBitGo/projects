"""
구독 채널 피드 DB 작업 함수들
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = Path(__file__).parent.parent / "data" / "youtube.db"


# ============================================================
# 구독 채널 관련
# ============================================================

def add_or_update_subscribed_channel(channel_data: dict):
    """구독 채널 추가 또는 업데이트"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO subscribed_channels (
            channel_id, channel_name, channel_description, thumbnail_url,
            subscriber_count, video_count, view_count,
            is_active, subscribed_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(channel_id) DO UPDATE SET
            channel_name = excluded.channel_name,
            channel_description = excluded.channel_description,
            thumbnail_url = excluded.thumbnail_url,
            subscriber_count = excluded.subscriber_count,
            video_count = excluded.video_count,
            view_count = excluded.view_count,
            updated_at = excluded.updated_at
    """, (
        channel_data['channel_id'],
        channel_data['channel_name'],
        channel_data.get('channel_description'),
        channel_data.get('thumbnail_url'),
        channel_data.get('subscriber_count', 0),
        channel_data.get('video_count', 0),
        channel_data.get('view_count', 0),
        channel_data.get('is_active', True),
        channel_data.get('subscribed_at'),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_all_subscribed_channels(active_only: bool = False) -> List[Dict]:
    """모든 구독 채널 조회"""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if active_only:
        cursor.execute("""
            SELECT * FROM subscribed_channels
            WHERE is_active = 1
            ORDER BY channel_name
        """)
    else:
        cursor.execute("""
            SELECT * FROM subscribed_channels
            ORDER BY channel_name
        """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def update_channel_active_status(channel_id: str, is_active: bool):
    """채널 활성화 상태 변경"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE subscribed_channels
        SET is_active = ?, updated_at = ?
        WHERE channel_id = ?
    """, (is_active, datetime.now().isoformat(), channel_id))

    conn.commit()
    conn.close()


def update_channel_last_collected(channel_id: str):
    """채널 마지막 수집 시간 업데이트"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE subscribed_channels
        SET last_collected_at = ?, updated_at = ?
        WHERE channel_id = ?
    """, (datetime.now().isoformat(), datetime.now().isoformat(), channel_id))

    conn.commit()
    conn.close()


# ============================================================
# 피드 영상 관련
# ============================================================

def add_or_update_feed_video(video_data: dict):
    """피드 영상 추가 또는 업데이트"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # is_new 계산: 처음 추가되는 영상만 True
    cursor.execute("SELECT video_id FROM feed_videos WHERE video_id = ?", (video_data['video_id'],))
    exists = cursor.fetchone() is not None
    is_new = not exists

    cursor.execute("""
        INSERT INTO feed_videos (
            video_id, channel_id, title, description, thumbnail_url,
            published_at, duration, is_short,
            view_count, like_count, comment_count,
            title_length, has_number, has_emoji,
            is_new, collected_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(video_id) DO UPDATE SET
            title = excluded.title,
            description = excluded.description,
            view_count = excluded.view_count,
            like_count = excluded.like_count,
            comment_count = excluded.comment_count,
            updated_at = excluded.updated_at
    """, (
        video_data['video_id'],
        video_data['channel_id'],
        video_data['title'],
        video_data.get('description'),
        video_data.get('thumbnail_url'),
        video_data['published_at'],
        video_data.get('duration', 0),
        video_data.get('is_short', False),
        video_data.get('view_count', 0),
        video_data.get('like_count', 0),
        video_data.get('comment_count', 0),
        video_data.get('title_length', 0),
        video_data.get('has_number', False),
        video_data.get('has_emoji', False),
        is_new,
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    return is_new


def get_feed_videos(
    channel_id: Optional[str] = None,
    is_short: Optional[bool] = None,
    is_new: Optional[bool] = None,
    days: Optional[int] = None,
    limit: int = 100
) -> List[Dict]:
    """피드 영상 조회"""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM feed_videos WHERE 1=1"
    params = []

    if channel_id:
        query += " AND channel_id = ?"
        params.append(channel_id)

    if is_short is not None:
        query += " AND is_short = ?"
        params.append(is_short)

    if is_new is not None:
        query += " AND is_new = ?"
        params.append(is_new)

    if days:
        query += " AND published_at >= datetime('now', '-' || ? || ' days')"
        params.append(days)

    query += " ORDER BY published_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def mark_old_videos_as_not_new(hours: int = 24):
    """오래된 영상의 is_new 플래그 제거"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE feed_videos
        SET is_new = 0
        WHERE collected_at < datetime('now', '-' || ? || ' hours')
        AND is_new = 1
    """, (hours,))

    updated = cursor.rowcount
    conn.commit()
    conn.close()

    return updated


# ============================================================
# 수집 이력 관련
# ============================================================

def add_collection_history(history_data: dict):
    """수집 이력 추가"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feed_collection_history (
            collected_at, channels_collected, new_videos_count,
            updated_videos_count, total_videos_count,
            api_quota_used, duration_seconds, errors
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        history_data.get('channels_collected', 0),
        history_data.get('new_videos_count', 0),
        history_data.get('updated_videos_count', 0),
        history_data.get('total_videos_count', 0),
        history_data.get('api_quota_used', 0),
        history_data.get('duration_seconds', 0),
        history_data.get('errors')
    ))

    conn.commit()
    conn.close()


def get_last_collection_time() -> Optional[str]:
    """마지막 수집 시간 조회"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT collected_at FROM feed_collection_history
        ORDER BY collected_at DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None


# ============================================================
# Transcript 관련
# ============================================================

def add_transcript_record(video_id: str, file_path: str, language: str, format: str, word_count: int):
    """Transcript 다운로드 기록 추가"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feed_transcripts (
            video_id, file_path, language, format, word_count, downloaded_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(video_id) DO UPDATE SET
            file_path = excluded.file_path,
            language = excluded.language,
            format = excluded.format,
            word_count = excluded.word_count,
            downloaded_at = excluded.downloaded_at
    """, (
        video_id,
        file_path,
        language,
        format,
        word_count,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_transcript_record(video_id: str) -> Optional[Dict]:
    """Transcript 다운로드 기록 조회"""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM feed_transcripts
        WHERE video_id = ?
    """, (video_id,))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


# ============================================================
# 통계 함수
# ============================================================

def get_feed_stats() -> Dict:
    """피드 통계 조회"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 전체 통계
    cursor.execute("SELECT COUNT(*) FROM subscribed_channels WHERE is_active = 1")
    active_channels = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feed_videos")
    total_videos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feed_videos WHERE is_short = 1")
    shorts_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feed_videos WHERE is_short = 0")
    longform_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feed_videos WHERE is_new = 1")
    new_videos = cursor.fetchone()[0]

    # 마지막 수집 시간
    cursor.execute("SELECT MAX(collected_at) FROM feed_videos")
    last_collected = cursor.fetchone()[0]

    conn.close()

    return {
        'active_channels': active_channels,
        'total_videos': total_videos,
        'shorts_count': shorts_count,
        'longform_count': longform_count,
        'new_videos': new_videos,
        'last_collected': last_collected
    }
