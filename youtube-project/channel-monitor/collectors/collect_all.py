"""
전체 데이터 수집 스크립트

모든 계정의 채널/영상/Analytics 데이터를 수집합니다.
"""

import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from collectors.youtube_api import YouTubeAPI
from database.operations import (
    add_account, get_all_accounts,
    add_or_update_channel, add_or_update_video,
    add_channel_analytics, add_traffic_source, add_video_analytics,
    add_video_snapshot
)


def collect_account_data(account_name: str):
    """특정 계정의 모든 데이터 수집"""

    print(f"\n{'='*60}")
    print(f"📊 {account_name} 데이터 수집 시작")
    print(f"{'='*60}\n")

    # 1. API 클라이언트 생성
    api = YouTubeAPI(account_name)

    # 2. 채널 정보 조회
    print("1️⃣ 채널 정보 조회 중...")
    channel_data = api.get_my_channel()

    if not channel_data:
        print(f"❌ {account_name}: 채널을 찾을 수 없습니다.")
        return

    channel_id = channel_data['channel_id']
    uploads_playlist_id = channel_data['uploads_playlist_id']

    print(f"✅ 채널: {channel_data['channel_name']}")
    print(f"   ID: {channel_id}")
    print(f"   구독자: {channel_data['subscriber_count']:,}명")
    print(f"   영상: {channel_data['video_count']:,}개\n")

    # 계정 정보 저장 (account_id 필요)
    token_file = str(project_root / "tokens" / f"{account_name}_token.json")
    account_id = add_account(account_name, "", token_file)

    # 채널 정보 저장
    channel_data['account_id'] = account_id
    add_or_update_channel(channel_data)

    # 3. 영상 목록 조회 (최근 100개)
    print("2️⃣ 영상 목록 조회 중...")
    video_ids = api.get_uploaded_videos(uploads_playlist_id, max_results=100)
    print(f"✅ 영상 {len(video_ids)}개 발견\n")

    if not video_ids:
        print("⚠️ 영상이 없습니다. Analytics 수집 건너뜀.\n")
        return

    # 4. 영상 상세 정보 조회
    print("3️⃣ 영상 상세 정보 조회 중...")
    videos = api.get_video_details(video_ids)

    for video in videos:
        video['channel_id'] = channel_id
        add_or_update_video(video)

        # 스냅샷 저장 (일일 통계)
        today = date.today()
        add_video_snapshot(
            video['video_id'],
            today,
            video['view_count'],
            video['like_count'],
            video['comment_count']
        )

    print(f"✅ 영상 {len(videos)}개 정보 저장\n")

    # 5. Analytics 데이터 수집 (최근 30일)
    print("4️⃣ Analytics 데이터 수집 중...")

    end_date = date.today() - timedelta(days=2)  # 2일 전까지 (데이터 지연 고려)
    start_date = end_date - timedelta(days=30)

    print(f"   기간: {start_date} ~ {end_date}\n")

    # 5-1. 채널 일별 Analytics
    print("   📊 채널 일별 Analytics...")
    channel_analytics = api.get_channel_analytics(
        channel_id,
        start_date,
        end_date,
        metrics='views,estimatedMinutesWatched,averageViewDuration,likes,comments,shares,subscribersGained,subscribersLost',
        dimensions='day'
    )

    for row in channel_analytics:
        analytics_date = datetime.strptime(row['day'], '%Y-%m-%d').date()
        analytics_data = {
            'views': int(row.get('views', 0)),
            'estimated_minutes_watched': int(row.get('estimatedMinutesWatched', 0)),
            'average_view_duration_seconds': int(row.get('averageViewDuration', 0)),
            'likes': int(row.get('likes', 0)),
            'comments': int(row.get('comments', 0)),
            'shares': int(row.get('shares', 0)),
            'subscribers_gained': int(row.get('subscribersGained', 0)),
            'subscribers_lost': int(row.get('subscribersLost', 0))
        }
        add_channel_analytics(channel_id, analytics_date, analytics_data)

    print(f"   ✅ {len(channel_analytics)}일 데이터 저장\n")

    # 5-2. 트래픽 소스 (채널 전체)
    print("   🚪 트래픽 소스 (채널 전체)...")
    traffic_sources = api.get_traffic_sources(channel_id, start_date, end_date)

    for source in traffic_sources:
        add_traffic_source(
            channel_id,
            end_date,  # 기간 전체 합산이므로 end_date로 저장
            source['source_type'],
            source['views'],
            source['estimated_minutes_watched'],
            video_id=None
        )

    print(f"   ✅ {len(traffic_sources)}개 소스 저장\n")

    # 5-3. 최근 10개 영상의 Analytics
    print("   📹 최근 10개 영상 Analytics...")
    recent_video_ids = video_ids[:10]
    video_analytics = api.get_video_analytics(channel_id, recent_video_ids, start_date, end_date)

    for va in video_analytics:
        analytics_data = {
            'views': va['views'],
            'estimated_minutes_watched': va['estimated_minutes_watched'],
            'average_view_duration_seconds': va['average_view_duration'],
            'likes': va['likes'],
            'comments': va['comments'],
            'shares': va['shares']
        }
        add_video_analytics(va['video_id'], end_date, analytics_data)

    print(f"   ✅ {len(video_analytics)}개 영상 Analytics 저장\n")

    # 5-4. 최근 5개 영상의 트래픽 소스
    print("   🚪 최근 5개 영상 트래픽 소스...")
    for video_id in video_ids[:5]:
        video_traffic = api.get_video_traffic_sources(video_id, start_date, end_date)

        for source in video_traffic:
            add_traffic_source(
                channel_id,
                end_date,
                source['source_type'],
                source['views'],
                source['estimated_minutes_watched'],
                video_id=video_id
            )

        if video_traffic:
            print(f"   ✅ {video_id}: {len(video_traffic)}개 소스")

    print()
    print(f"{'='*60}")
    print(f"✅ {account_name} 데이터 수집 완료!")
    print(f"{'='*60}\n")


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("📊 YouTube Intelligence - 전체 데이터 수집")
    print("="*60)
    print(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 수집할 계정 목록 (하드코딩 또는 DB에서 조회)
    accounts_to_collect = ['account1', 'account2']

    for account_name in accounts_to_collect:
        try:
            collect_account_data(account_name)
        except Exception as e:
            print(f"❌ {account_name} 수집 중 오류: {e}\n")
            continue

    print("\n" + "="*60)
    print("✅ 전체 데이터 수집 완료!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
