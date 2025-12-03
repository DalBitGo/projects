"""
YouTube Intelligence Database Schema

SQLite 데이터베이스 스키마 정의
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "data" / "youtube.db"


def get_connection():
    """데이터베이스 연결"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # dict-like access
    return conn


def init_database():
    """데이터베이스 초기화 및 테이블 생성"""

    conn = get_connection()
    cursor = conn.cursor()

    # 1. accounts 테이블 - OAuth 계정 정보
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT UNIQUE NOT NULL,  -- 예: account1, account2
            email TEXT,                          -- YouTube 계정 이메일
            token_file_path TEXT NOT NULL,       -- 토큰 파일 경로
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. channels 테이블 - 채널 정보
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT UNIQUE NOT NULL,     -- YouTube 채널 ID
            account_id INTEGER NOT NULL,         -- accounts 테이블 FK
            channel_name TEXT,                   -- 채널명
            description TEXT,                    -- 채널 설명
            published_at TIMESTAMP,              -- 개설일
            thumbnail_url TEXT,                  -- 프로필 이미지

            -- 통계 (주기적으로 업데이트)
            subscriber_count INTEGER,
            video_count INTEGER,
            view_count INTEGER,

            -- 메타데이터
            country TEXT,                        -- 국가
            custom_url TEXT,                     -- 커스텀 URL

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
    """)

    # 3. videos 테이블 - 영상 정보
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT UNIQUE NOT NULL,       -- YouTube 영상 ID
            channel_id TEXT NOT NULL,            -- channels 테이블 FK

            -- 기본 정보
            title TEXT,
            description TEXT,
            published_at TIMESTAMP,
            thumbnail_url TEXT,

            -- 콘텐츠 정보
            duration_seconds INTEGER,            -- 영상 길이 (초)
            category_id TEXT,
            tags TEXT,                           -- JSON array as text

            -- 통계 (Data API - 주기적 업데이트)
            view_count INTEGER,
            like_count INTEGER,
            comment_count INTEGER,

            -- 상태
            privacy_status TEXT,                 -- public, private, unlisted

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
        )
    """)

    # 4. video_snapshots 테이블 - 영상 통계 스냅샷 (시계열)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            snapshot_date DATE NOT NULL,         -- 스냅샷 날짜

            -- Data API 통계
            view_count INTEGER,
            like_count INTEGER,
            comment_count INTEGER,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (video_id) REFERENCES videos(video_id),
            UNIQUE(video_id, snapshot_date)
        )
    """)

    # 5. video_analytics_daily 테이블 - 영상별 일일 Analytics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_analytics_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            date DATE NOT NULL,

            -- 조회 관련
            views INTEGER DEFAULT 0,
            estimated_minutes_watched INTEGER DEFAULT 0,
            average_view_duration_seconds INTEGER DEFAULT 0,
            average_view_percentage REAL DEFAULT 0,

            -- 참여도
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            subscribers_gained INTEGER DEFAULT 0,
            subscribers_lost INTEGER DEFAULT 0,

            -- CTR (Click-Through Rate)
            card_clicks INTEGER DEFAULT 0,
            card_impressions INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (video_id) REFERENCES videos(video_id),
            UNIQUE(video_id, date)
        )
    """)

    # 6. channel_analytics_daily 테이블 - 채널별 일일 Analytics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channel_analytics_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL,
            date DATE NOT NULL,

            -- 조회 관련
            views INTEGER DEFAULT 0,
            estimated_minutes_watched INTEGER DEFAULT 0,
            average_view_duration_seconds INTEGER DEFAULT 0,

            -- 참여도
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            subscribers_gained INTEGER DEFAULT 0,
            subscribers_lost INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
            UNIQUE(channel_id, date)
        )
    """)

    # 7. traffic_sources 테이블 - 트래픽 소스 (핵심!)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traffic_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,                       -- NULL이면 채널 전체
            channel_id TEXT NOT NULL,
            date DATE NOT NULL,

            source_type TEXT NOT NULL,           -- YT_SEARCH, RELATED_VIDEO, 등

            -- 메트릭
            views INTEGER DEFAULT 0,
            estimated_minutes_watched INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (video_id) REFERENCES videos(video_id),
            FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
            UNIQUE(video_id, channel_id, date, source_type)
        )
    """)

    # 8. slack_settings 테이블 - Slack 알림 설정
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS slack_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL UNIQUE,
            slack_webhook_url TEXT NOT NULL,

            -- 알림 설정
            urgent_alerts BOOLEAN DEFAULT 1,
            success_alerts BOOLEAN DEFAULT 1,
            daily_summary BOOLEAN DEFAULT 1,
            weekly_report BOOLEAN DEFAULT 1,

            -- 알림 빈도 제한 (분)
            min_interval_minutes INTEGER DEFAULT 60,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
        )
    """)

    # 9. notification_history 테이블 - 알림 히스토리 (스팸 방지)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL,
            notification_type TEXT NOT NULL,  -- urgent/success/daily/weekly
            video_id TEXT,                     -- NULL이면 채널 전체 알림
            message TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
            FOREIGN KEY (video_id) REFERENCES videos(video_id)
        )
    """)

    # 인덱스 생성 (쿼리 성능 향상)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_channel ON videos(channel_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_published ON videos(published_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_video_snapshots_date ON video_snapshots(snapshot_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_video_analytics_date ON video_analytics_daily(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_channel_analytics_date ON channel_analytics_daily(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traffic_sources_date ON traffic_sources(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traffic_sources_type ON traffic_sources(source_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notification_history_channel ON notification_history(channel_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notification_history_sent_at ON notification_history(sent_at)")

    conn.commit()
    conn.close()

    print(f"✅ 데이터베이스 초기화 완료: {DATABASE_PATH}")


def reset_database():
    """데이터베이스 완전 초기화 (모든 데이터 삭제)"""
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
        print(f"🗑️  기존 데이터베이스 삭제: {DATABASE_PATH}")

    init_database()


if __name__ == "__main__":
    # 테스트: 데이터베이스 초기화
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_database()
    else:
        init_database()
