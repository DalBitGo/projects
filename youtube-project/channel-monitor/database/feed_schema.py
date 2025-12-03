"""
구독 채널 피드 관련 DB 스키마

기존 youtube.db에 테이블 추가
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "youtube.db"


def create_feed_tables():
    """피드 관련 테이블 생성"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("📊 구독 채널 피드 테이블 생성 중...\n")

    # 1. 구독 채널 테이블
    print("1️⃣ subscribed_channels 테이블 생성...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribed_channels (
            channel_id TEXT PRIMARY KEY,
            channel_name TEXT NOT NULL,
            channel_description TEXT,
            thumbnail_url TEXT,

            -- 구독 정보
            subscriber_count INTEGER,
            video_count INTEGER,
            view_count INTEGER,

            -- 피드 설정
            is_active BOOLEAN DEFAULT TRUE,  -- 수집 대상 여부
            category TEXT,  -- NULL 허용, 나중에 확장 가능

            -- 메타데이터
            subscribed_at TIMESTAMP,
            last_collected_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✅ 완료\n")

    # 2. 피드 영상 테이블
    print("2️⃣ feed_videos 테이블 생성...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feed_videos (
            video_id TEXT PRIMARY KEY,
            channel_id TEXT NOT NULL,

            -- 기본 정보
            title TEXT NOT NULL,
            description TEXT,
            thumbnail_url TEXT,
            published_at TIMESTAMP NOT NULL,

            -- 영상 정보
            duration INTEGER,  -- 초 단위
            is_short BOOLEAN DEFAULT FALSE,  -- 60초 이하면 쇼츠

            -- 통계
            view_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,

            -- 분석용 (제목 패턴)
            title_length INTEGER,
            has_number BOOLEAN DEFAULT FALSE,  -- 제목에 숫자 포함
            has_emoji BOOLEAN DEFAULT FALSE,   -- 이모지 포함

            -- 새 영상 표시
            is_new BOOLEAN DEFAULT TRUE,  -- 수집된지 24시간 이내

            -- 메타데이터
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (channel_id) REFERENCES subscribed_channels(channel_id)
        )
    """)
    print("   ✅ 완료\n")

    # 3. 수집 이력 테이블
    print("3️⃣ feed_collection_history 테이블 생성...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feed_collection_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            -- 통계
            channels_collected INTEGER,  -- 수집한 채널 수
            new_videos_count INTEGER,    -- 새로 추가된 영상 수
            updated_videos_count INTEGER, -- 업데이트된 영상 수
            total_videos_count INTEGER,   -- 전체 영상 수

            -- API quota
            api_quota_used INTEGER,

            -- 수집 소요 시간
            duration_seconds INTEGER,

            -- 에러 로그
            errors TEXT  -- JSON 형태로 에러 저장
        )
    """)
    print("   ✅ 완료\n")

    # 4. Transcript 메타데이터 (선택적)
    print("4️⃣ feed_transcripts 테이블 생성...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feed_transcripts (
            video_id TEXT PRIMARY KEY,
            file_path TEXT,  -- 다운로드한 파일 경로
            language TEXT,   -- ko, en 등
            format TEXT,     -- txt, json, srt
            word_count INTEGER,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (video_id) REFERENCES feed_videos(video_id)
        )
    """)
    print("   ✅ 완료\n")

    # 인덱스 생성
    print("5️⃣ 인덱스 생성...")

    # 피드 영상 인덱스
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_feed_videos_channel_id
        ON feed_videos(channel_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_feed_videos_published_at
        ON feed_videos(published_at DESC)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_feed_videos_is_short
        ON feed_videos(is_short)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_feed_videos_is_new
        ON feed_videos(is_new)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_feed_videos_view_count
        ON feed_videos(view_count DESC)
    """)

    # 구독 채널 인덱스
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscribed_channels_is_active
        ON subscribed_channels(is_active)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscribed_channels_category
        ON subscribed_channels(category)
    """)

    print("   ✅ 완료\n")

    conn.commit()
    conn.close()

    print("="*60)
    print("✅ 구독 채널 피드 테이블 생성 완료!")
    print("="*60)
    print()
    print("생성된 테이블:")
    print("  1. subscribed_channels      - 구독 채널 정보")
    print("  2. feed_videos               - 피드 영상 정보")
    print("  3. feed_collection_history   - 수집 이력")
    print("  4. feed_transcripts          - Transcript 메타데이터")
    print()
    print(f"데이터베이스 위치: {DB_PATH}")
    print()


def check_tables():
    """테이블 존재 확인"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)

    tables = cursor.fetchall()

    print("📋 현재 데이터베이스 테이블 목록:\n")
    for i, (table_name,) in enumerate(tables, 1):
        print(f"  {i}. {table_name}")

    print(f"\n총 {len(tables)}개 테이블")

    conn.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎬 구독 채널 피드 DB 초기화")
    print("="*60 + "\n")

    # 테이블 생성
    create_feed_tables()

    # 확인
    check_tables()
