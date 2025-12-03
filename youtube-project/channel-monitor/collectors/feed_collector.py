"""
구독 채널 피드 수집 Collector
"""

import sys
import re
import emoji
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from collectors.youtube_api import YouTubeAPI
from database.feed_operations import (
    add_or_update_subscribed_channel,
    get_all_subscribed_channels,
    add_or_update_feed_video,
    update_channel_last_collected,
    add_collection_history,
    get_last_collection_time,
    mark_old_videos_as_not_new
)


class FeedCollector:
    """구독 채널 피드 수집기"""

    def __init__(self, account_name: str = 'account1'):
        self.account_name = account_name
        self.api = YouTubeAPI(account_name)
        self.api_quota_used = 0

    def collect_subscriptions(self) -> int:
        """
        구독 채널 목록 수집

        Returns:
            수집한 채널 수
        """

        print(f"\n{'='*60}")
        print(f"📺 구독 채널 목록 수집 시작")
        print(f"{'='*60}\n")

        all_subscriptions = []
        next_page_token = None
        page_count = 0

        try:
            while True:
                page_count += 1
                print(f"📄 페이지 {page_count} 수집 중...")

                request_params = {
                    'part': 'snippet,contentDetails',
                    'mine': True,
                    'maxResults': 50
                }

                if next_page_token:
                    request_params['pageToken'] = next_page_token

                request = self.api.youtube.subscriptions().list(**request_params)
                response = request.execute()

                self.api_quota_used += 1  # subscriptions.list = 1 unit

                items = response.get('items', [])
                all_subscriptions.extend(items)

                print(f"   ✅ {len(items)}개 채널 수집")

                # 다음 페이지 확인
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

            print(f"\n✅ 총 {len(all_subscriptions)}개 구독 채널 발견")
            print(f"📊 API Quota 사용: {self.api_quota_used} units\n")

            # DB에 저장
            print("💾 데이터베이스에 저장 중...")

            for item in all_subscriptions:
                snippet = item['snippet']
                channel_id = snippet['resourceId']['channelId']
                channel_name = snippet['title']
                description = snippet.get('description', '')
                thumbnail_url = snippet.get('thumbnails', {}).get('default', {}).get('url')
                published_at = snippet.get('publishedAt')

                channel_data = {
                    'channel_id': channel_id,
                    'channel_name': channel_name,
                    'channel_description': description,
                    'thumbnail_url': thumbnail_url,
                    'subscribed_at': published_at,
                    'is_active': True  # 기본값: 전부 활성화
                }

                add_or_update_subscribed_channel(channel_data)

            print(f"   ✅ {len(all_subscriptions)}개 채널 저장 완료\n")

            return len(all_subscriptions)

        except Exception as e:
            print(f"\n❌ 에러 발생: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def parse_duration(self, duration_str: str) -> int:
        """
        ISO 8601 duration을 초로 변환

        예: PT1H2M10S -> 3730초
            PT15M33S -> 933초
            PT59S -> 59초
        """

        if not duration_str or duration_str == 'P0D':
            return 0

        # PT로 시작하지 않으면 0 반환
        if not duration_str.startswith('PT'):
            return 0

        # PT 제거
        duration_str = duration_str[2:]

        hours = 0
        minutes = 0
        seconds = 0

        # H, M, S로 분리
        if 'H' in duration_str:
            parts = duration_str.split('H')
            hours = int(parts[0])
            duration_str = parts[1]

        if 'M' in duration_str:
            parts = duration_str.split('M')
            minutes = int(parts[0])
            duration_str = parts[1]

        if 'S' in duration_str:
            duration_str = duration_str.replace('S', '')
            if duration_str:
                seconds = int(duration_str)

        return hours * 3600 + minutes * 60 + seconds

    def analyze_title(self, title: str) -> Dict:
        """
        제목 패턴 분석

        Returns:
            title_length, has_number, has_emoji
        """

        return {
            'title_length': len(title),
            'has_number': bool(re.search(r'\d+', title)),
            'has_emoji': bool(emoji.emoji_count(title))
        }

    def collect_feed_videos(self, max_videos_per_channel: int = 30) -> Dict:
        """
        피드 영상 수집 (활성화된 채널만)

        Args:
            max_videos_per_channel: 채널당 최대 수집 개수 (기본 30개)

        Returns:
            통계 딕셔너리
        """

        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"🎬 피드 영상 수집 시작")
        print(f"{'='*60}\n")

        # 활성화된 채널 조회
        active_channels = get_all_subscribed_channels(active_only=True)

        if not active_channels:
            print("❌ 활성화된 채널이 없습니다")
            return {}

        print(f"📺 수집 대상 채널: {len(active_channels)}개")
        print(f"📊 채널당 최대 영상: {max_videos_per_channel}개\n")

        # 마지막 수집 시간
        last_collected = get_last_collection_time()
        if last_collected:
            print(f"⏰ 마지막 수집: {last_collected}")
            print(f"   → 그 이후 영상만 수집 (증분 업데이트)\n")
        else:
            print(f"⭐ 첫 수집입니다\n")

        new_videos_count = 0
        updated_videos_count = 0
        total_videos_count = 0
        errors = []

        for i, channel in enumerate(active_channels, 1):
            channel_id = channel['channel_id']
            channel_name = channel['channel_name']

            print(f"[{i}/{len(active_channels)}] 📺 {channel_name}")

            try:
                # 1. 채널 정보 조회 (업로드 플레이리스트 ID)
                request = self.api.youtube.channels().list(
                    part='contentDetails',
                    id=channel_id
                )
                response = request.execute()
                self.api_quota_used += 1  # channels.list = 1 unit

                if not response.get('items'):
                    print(f"   ⚠️ 채널 정보를 찾을 수 없습니다")
                    continue

                uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

                # 2. 최신 영상 ID 목록 조회
                request = self.api.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=max_videos_per_channel
                )
                response = request.execute()
                self.api_quota_used += 1  # playlistItems.list = 1 unit

                video_ids = []
                for item in response.get('items', []):
                    video_id = item['snippet']['resourceId']['videoId']
                    video_ids.append(video_id)

                if not video_ids:
                    print(f"   ⚠️ 영상이 없습니다")
                    continue

                # 3. 영상 상세 정보 조회 (배치)
                request = self.api.youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(video_ids)
                )
                response = request.execute()
                self.api_quota_used += 1  # videos.list = 1 unit

                channel_new_videos = 0
                channel_updated_videos = 0

                for video_item in response.get('items', []):
                    video_id = video_item['id']
                    snippet = video_item['snippet']
                    statistics = video_item.get('statistics', {})
                    content_details = video_item.get('contentDetails', {})

                    # 영상 길이 파싱
                    duration_str = content_details.get('duration', 'PT0S')
                    duration_seconds = self.parse_duration(duration_str)

                    # 쇼츠 판별 (60초 이하)
                    is_short = duration_seconds > 0 and duration_seconds <= 60

                    # 제목 분석
                    title = snippet['title']
                    title_analysis = self.analyze_title(title)

                    # 영상 데이터
                    video_data = {
                        'video_id': video_id,
                        'channel_id': channel_id,
                        'title': title,
                        'description': snippet.get('description', ''),
                        'thumbnail_url': snippet.get('thumbnails', {}).get('medium', {}).get('url'),
                        'published_at': snippet['publishedAt'],
                        'duration': duration_seconds,
                        'is_short': is_short,
                        'view_count': int(statistics.get('viewCount', 0)),
                        'like_count': int(statistics.get('likeCount', 0)),
                        'comment_count': int(statistics.get('commentCount', 0)),
                        **title_analysis
                    }

                    # 증분 업데이트: 마지막 수집 이후 영상만
                    if last_collected:
                        published_at = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                        last_collected_dt = datetime.fromisoformat(last_collected.replace('Z', '+00:00'))

                        if published_at <= last_collected_dt:
                            # 이미 수집한 영상은 건너뛰기 (단, 통계는 업데이트)
                            is_new_video = add_or_update_feed_video(video_data)
                            if is_new_video:
                                channel_new_videos += 1
                            else:
                                channel_updated_videos += 1
                            continue

                    # 새 영상 저장
                    is_new_video = add_or_update_feed_video(video_data)

                    if is_new_video:
                        channel_new_videos += 1
                    else:
                        channel_updated_videos += 1

                    total_videos_count += 1

                new_videos_count += channel_new_videos
                updated_videos_count += channel_updated_videos

                print(f"   ✅ 영상 {len(video_ids)}개 수집 (새: {channel_new_videos}, 업데이트: {channel_updated_videos})")

                # 채널 마지막 수집 시간 업데이트
                update_channel_last_collected(channel_id)

            except Exception as e:
                error_msg = f"{channel_name}: {str(e)}"
                errors.append(error_msg)
                print(f"   ❌ 에러: {e}")

        # 오래된 영상의 is_new 플래그 제거
        print(f"\n🔄 오래된 영상 플래그 정리 중...")
        updated_flags = mark_old_videos_as_not_new(hours=24)
        print(f"   ✅ {updated_flags}개 영상의 '새' 표시 제거")

        # 수집 이력 저장
        duration_seconds = int(time.time() - start_time)

        history_data = {
            'channels_collected': len(active_channels),
            'new_videos_count': new_videos_count,
            'updated_videos_count': updated_videos_count,
            'total_videos_count': total_videos_count,
            'api_quota_used': self.api_quota_used,
            'duration_seconds': duration_seconds,
            'errors': ', '.join(errors) if errors else None
        }

        add_collection_history(history_data)

        # 결과 출력
        print(f"\n{'='*60}")
        print(f"✅ 피드 영상 수집 완료!")
        print(f"{'='*60}\n")
        print(f"📊 수집 통계:")
        print(f"   채널: {len(active_channels)}개")
        print(f"   새 영상: {new_videos_count}개")
        print(f"   업데이트: {updated_videos_count}개")
        print(f"   총 영상: {total_videos_count}개")
        print(f"\n📊 API Quota 사용: {self.api_quota_used} units")
        print(f"⏱️ 소요 시간: {duration_seconds}초\n")

        if errors:
            print(f"⚠️ 에러 발생 ({len(errors)}건):")
            for error in errors[:5]:  # 처음 5개만 표시
                print(f"   - {error}")
            if len(errors) > 5:
                print(f"   ... 외 {len(errors) - 5}건")
            print()

        return history_data


def main():
    """메인 실행 함수"""

    print("\n" + "="*60)
    print("🚀 구독 채널 피드 수집")
    print("="*60)

    collector = FeedCollector(account_name='account1')

    # 1. 구독 채널 목록 수집 (처음에만)
    subscribed_channels = get_all_subscribed_channels()

    if not subscribed_channels:
        print("\n📺 구독 채널 목록을 먼저 수집합니다...\n")
        collector.collect_subscriptions()
    else:
        print(f"\n✅ 구독 채널 {len(subscribed_channels)}개 이미 저장되어 있음")
        print(f"   (재수집하려면 DB에서 subscribed_channels 테이블 삭제)\n")

    # 2. 피드 영상 수집
    collector.collect_feed_videos(max_videos_per_channel=30)


if __name__ == "__main__":
    main()
