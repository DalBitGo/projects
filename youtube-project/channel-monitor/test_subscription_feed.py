"""
구독 채널 피드 기능 테스트
- 구독 채널 목록 가져오기
- 최신 영상 수집
- Transcript 다운로드
- API quota 계산
"""

import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from collectors.youtube_api import YouTubeAPI

def test_subscriptions(account_name='account1'):
    """구독 채널 목록 가져오기 테스트"""
    print(f"\n{'='*60}")
    print(f"📺 구독 채널 목록 테스트")
    print(f"{'='*60}\n")

    try:
        api = YouTubeAPI(account_name)

        # 구독 채널 목록 가져오기
        request = api.youtube.subscriptions().list(
            part="snippet",
            mine=True,
            maxResults=50  # 최대 50개
        )
        response = request.execute()

        subscriptions = response.get('items', [])
        total = response.get('pageInfo', {}).get('totalResults', 0)

        print(f"✅ 구독 채널: {total}개")
        print(f"✅ 가져온 채널: {len(subscriptions)}개\n")

        print("📋 구독 채널 목록:")
        for i, item in enumerate(subscriptions[:10], 1):  # 처음 10개만 출력
            snippet = item['snippet']
            channel_title = snippet['title']
            channel_id = snippet['resourceId']['channelId']
            print(f"  {i}. {channel_title}")
            print(f"     ID: {channel_id}\n")

        if len(subscriptions) == 50 and total > 50:
            print(f"⚠️ 더 많은 채널이 있습니다 (총 {total}개)")
            print(f"   nextPageToken으로 페이지네이션 필요\n")

        # API quota 계산
        quota_used = 1  # subscriptions.list = 1 unit
        print(f"📊 API Quota 사용: {quota_used} units")

        return subscriptions

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return None


def test_channel_videos(channel_id, channel_title, account_name='account1'):
    """특정 채널의 최신 영상 가져오기"""
    print(f"\n{'='*60}")
    print(f"🎬 [{channel_title}] 최신 영상 테스트")
    print(f"{'='*60}\n")

    try:
        api = YouTubeAPI(account_name)

        # 채널의 업로드 플레이리스트 ID 가져오기
        request = api.youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = request.execute()

        if not response.get('items'):
            print(f"❌ 채널 정보를 찾을 수 없습니다")
            return None

        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # 최신 영상 10개 가져오기
        request = api.youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=10
        )
        response = request.execute()

        videos = response.get('items', [])

        print(f"✅ 최신 영상: {len(videos)}개\n")

        video_ids = []
        for i, item in enumerate(videos, 1):
            snippet = item['snippet']
            video_id = snippet['resourceId']['videoId']
            title = snippet['title']
            published_at = snippet['publishedAt']

            video_ids.append(video_id)

            print(f"  {i}. {title}")
            print(f"     ID: {video_id}")
            print(f"     업로드: {published_at}\n")

        # 영상 상세 정보 가져오기 (조회수, 좋아요 등)
        if video_ids:
            request = api.youtube.videos().list(
                part="statistics,contentDetails",
                id=",".join(video_ids[:5])  # 처음 5개만
            )
            response = request.execute()

            print(f"📊 상세 통계 (처음 5개):\n")
            for item in response.get('items', []):
                stats = item['statistics']
                details = item['contentDetails']
                video_id = item['id']

                view_count = int(stats.get('viewCount', 0))
                like_count = int(stats.get('likeCount', 0))
                comment_count = int(stats.get('commentCount', 0))
                duration = details.get('duration', '')

                print(f"  Video ID: {video_id}")
                print(f"    👁 조회수: {view_count:,}")
                print(f"    👍 좋아요: {like_count:,}")
                print(f"    💬 댓글: {comment_count:,}")
                print(f"    ⏱ 길이: {duration}\n")

        # API quota 계산
        quota_used = 1 + 1 + 1  # channels.list + playlistItems.list + videos.list = 3 units
        print(f"📊 API Quota 사용: {quota_used} units")

        return video_ids

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_transcript(video_id):
    """Transcript (자막) 가져오기 테스트"""
    print(f"\n{'='*60}")
    print(f"📝 Transcript 테스트 (비공식 API)")
    print(f"{'='*60}\n")

    try:
        # youtube-transcript-api 패키지 설치 필요
        from youtube_transcript_api import YouTubeTranscriptApi

        print(f"영상 ID: {video_id}\n")

        # 자막 가져오기 (한국어 우선, 없으면 영어)
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=['ko', 'en']
        )

        print(f"✅ Transcript 가져오기 성공!")
        print(f"   총 {len(transcript)}개 세그먼트\n")

        # 처음 10개 출력
        print("📋 Transcript 샘플 (처음 10개):\n")
        for i, entry in enumerate(transcript[:10], 1):
            text = entry['text']
            start = entry['start']
            duration = entry['duration']
            print(f"  {i}. [{start:.1f}s] {text}")

        print(f"\n✅ Transcript 전체 길이: {len(transcript)}개 세그먼트")

        # 전체 텍스트 합치기
        full_text = " ".join([entry['text'] for entry in transcript])
        print(f"   전체 텍스트 길이: {len(full_text)} 글자\n")

        # API quota 계산
        print(f"📊 API Quota 사용: 0 units (비공식 API, quota 안 먹음!)")

        return transcript

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        print(f"   (자막이 없거나, 비공개 설정일 수 있습니다)")
        print(f"\n💡 youtube-transcript-api 설치 필요:")
        print(f"   pip install youtube-transcript-api\n")
        return None


def test_official_captions(video_id, account_name='account1'):
    """공식 YouTube API로 자막 가져오기 테스트"""
    print(f"\n{'='*60}")
    print(f"📝 Captions 테스트 (공식 API)")
    print(f"{'='*60}\n")

    try:
        api = YouTubeAPI(account_name)

        # 자막 목록 가져오기
        request = api.youtube.captions().list(
            part="snippet",
            videoId=video_id
        )
        response = request.execute()

        captions = response.get('items', [])

        if not captions:
            print(f"❌ 자막이 없습니다\n")
            return None

        print(f"✅ 자막 트랙: {len(captions)}개\n")

        for i, item in enumerate(captions, 1):
            snippet = item['snippet']
            caption_id = item['id']
            language = snippet.get('language', 'unknown')
            name = snippet.get('name', '')
            track_kind = snippet.get('trackKind', '')

            print(f"  {i}. 언어: {language} ({name})")
            print(f"     ID: {caption_id}")
            print(f"     종류: {track_kind}\n")

        # 자막 다운로드 (첫 번째 트랙)
        print("⚠️ 자막 다운로드는 영상 소유자만 가능합니다")
        print("   (다른 채널 영상은 다운로드 불가)\n")

        # API quota 계산
        quota_used = 50  # captions.list = 50 units (비싸!)
        print(f"📊 API Quota 사용: {quota_used} units (비쌈!)")

        return captions

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return None


def calculate_daily_quota():
    """일일 API quota 계산"""
    print(f"\n{'='*60}")
    print(f"💰 API Quota 계산 (하루 1회 수집 가정)")
    print(f"{'='*60}\n")

    print("시나리오: 구독 채널 50개, 각 채널당 최신 10개 영상")
    print()

    # 구독 채널 목록
    quota_subscriptions = 1  # subscriptions.list = 1 unit
    print(f"1. 구독 채널 목록: {quota_subscriptions} units")

    # 채널당 영상 목록
    channels_count = 50
    quota_per_channel = 1 + 1 + 1  # channels.list + playlistItems.list + videos.list = 3 units
    quota_channels = channels_count * quota_per_channel
    print(f"2. 채널별 영상 수집 (50개): {channels_count} × {quota_per_channel} = {quota_channels} units")

    # Transcript (비공식 API 사용 시)
    quota_transcript = 0
    print(f"3. Transcript (비공식 API): {quota_transcript} units")

    total_quota = quota_subscriptions + quota_channels + quota_transcript
    daily_limit = 10000

    print(f"\n{'='*40}")
    print(f"📊 총 Quota 사용: {total_quota} / {daily_limit} units")
    print(f"   비율: {total_quota / daily_limit * 100:.1f}%")
    print(f"{'='*40}\n")

    if total_quota > daily_limit:
        print(f"⚠️ 일일 할당량 초과!")
        print(f"   해결책: 채널 수 줄이기 또는 수집 빈도 조절\n")
    else:
        print(f"✅ 일일 할당량 내 가능!")
        max_runs = daily_limit // total_quota
        print(f"   하루 최대 {max_runs}회 수집 가능\n")

    return total_quota


if __name__ == "__main__":
    print("🧪 YouTube 구독 채널 피드 기능 테스트\n")

    # 1. 구독 채널 목록 테스트
    subscriptions = test_subscriptions('account1')

    if subscriptions and len(subscriptions) > 0:
        # 2. 첫 번째 구독 채널의 영상 가져오기
        first_channel = subscriptions[0]
        channel_id = first_channel['snippet']['resourceId']['channelId']
        channel_title = first_channel['snippet']['title']

        video_ids = test_channel_videos(channel_id, channel_title, 'account1')

        if video_ids and len(video_ids) > 0:
            # 3. 첫 번째 영상의 Transcript 테스트
            first_video_id = video_ids[0]
            test_transcript(first_video_id)

    # 4. API quota 계산
    calculate_daily_quota()

    print(f"\n{'='*60}")
    print("✅ 테스트 완료!")
    print(f"{'='*60}\n")
