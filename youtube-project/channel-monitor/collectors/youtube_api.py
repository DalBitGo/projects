"""
YouTube API Wrapper

Data API v3 + Analytics API를 쉽게 사용하기 위한 래퍼 클래스
"""

from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import isodate
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.auth import load_credentials


class YouTubeAPI:
    """YouTube Data API + Analytics API Wrapper"""

    def __init__(self, account_name: str):
        """
        Args:
            account_name: 계정 이름 (예: account1, account2)
        """
        self.account_name = account_name
        credentials = load_credentials(account_name)

        # API 클라이언트 생성
        self.youtube = build('youtube', 'v3', credentials=credentials)
        self.analytics = build('youtubeAnalytics', 'v2', credentials=credentials)

    # ========================================================================
    # Data API v3
    # ========================================================================

    def get_my_channel(self) -> Optional[Dict]:
        """내 채널 정보 조회"""
        try:
            response = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                mine=True
            ).execute()

            if not response.get('items'):
                return None

            channel = response['items'][0]

            return {
                'channel_id': channel['id'],
                'channel_name': channel['snippet']['title'],
                'description': channel['snippet'].get('description'),
                'published_at': channel['snippet']['publishedAt'],
                'thumbnail_url': channel['snippet']['thumbnails']['default']['url'],
                'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
                'video_count': int(channel['statistics'].get('videoCount', 0)),
                'view_count': int(channel['statistics'].get('viewCount', 0)),
                'country': channel['snippet'].get('country'),
                'custom_url': channel['snippet'].get('customUrl'),
                'uploads_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads']
            }

        except HttpError as e:
            print(f"❌ 채널 정보 조회 실패: {e}")
            return None

    def get_uploaded_videos(self, uploads_playlist_id: str, max_results: int = 50) -> List[str]:
        """업로드된 영상 ID 목록 조회"""
        video_ids = []

        try:
            # 플레이리스트에서 영상 목록 가져오기
            request = self.youtube.playlistItems().list(
                part='contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=min(max_results, 50)  # API 제한
            )

            while request and len(video_ids) < max_results:
                response = request.execute()

                for item in response['items']:
                    video_ids.append(item['contentDetails']['videoId'])

                # 다음 페이지
                request = self.youtube.playlistItems().list_next(request, response)
                if not request:
                    break

            return video_ids[:max_results]

        except HttpError as e:
            print(f"❌ 영상 목록 조회 실패: {e}")
            return []

    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """영상 상세 정보 조회 (최대 50개씩)"""
        if not video_ids:
            return []

        videos = []

        try:
            # 최대 50개씩 배치 처리
            for i in range(0, len(video_ids), 50):
                batch = video_ids[i:i+50]

                response = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails,status',
                    id=','.join(batch)
                ).execute()

                for item in response.get('items', []):
                    # duration을 초로 변환 (ISO 8601 형식)
                    duration = isodate.parse_duration(item['contentDetails']['duration'])
                    duration_seconds = int(duration.total_seconds())

                    video_data = {
                        'video_id': item['id'],
                        'title': item['snippet']['title'],
                        'description': item['snippet'].get('description'),
                        'published_at': item['snippet']['publishedAt'],
                        'thumbnail_url': item['snippet']['thumbnails']['default']['url'],
                        'duration_seconds': duration_seconds,
                        'category_id': item['snippet'].get('categoryId'),
                        'tags': item['snippet'].get('tags', []),
                        'view_count': int(item['statistics'].get('viewCount', 0)),
                        'like_count': int(item['statistics'].get('likeCount', 0)),
                        'comment_count': int(item['statistics'].get('commentCount', 0)),
                        'privacy_status': item['status']['privacyStatus']
                    }

                    videos.append(video_data)

            return videos

        except HttpError as e:
            print(f"❌ 영상 상세 정보 조회 실패: {e}")
            return []

    # ========================================================================
    # Analytics API
    # ========================================================================

    def get_channel_analytics(self, channel_id: str, start_date: date, end_date: date,
                              metrics: str = 'views,estimatedMinutesWatched,averageViewDuration',
                              dimensions: str = 'day') -> List[Dict]:
        """채널 Analytics 데이터 조회"""
        try:
            response = self.analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date.strftime('%Y-%m-%d'),
                endDate=end_date.strftime('%Y-%m-%d'),
                metrics=metrics,
                dimensions=dimensions,
                sort='day'
            ).execute()

            if 'rows' not in response:
                return []

            # 결과 파싱
            headers = [col['name'] for col in response['columnHeaders']]
            results = []

            for row in response['rows']:
                result = dict(zip(headers, row))
                results.append(result)

            return results

        except HttpError as e:
            print(f"❌ Analytics 조회 실패: {e}")
            return []

    def get_traffic_sources(self, channel_id: str, start_date: date, end_date: date,
                           video_id: Optional[str] = None) -> List[Dict]:
        """트래픽 소스 조회 (핵심!)"""
        try:
            filters_str = f'channel=={channel_id}'
            if video_id:
                filters_str = f'video=={video_id}'

            response = self.analytics.reports().query(
                ids=filters_str,
                startDate=start_date.strftime('%Y-%m-%d'),
                endDate=end_date.strftime('%Y-%m-%d'),
                metrics='views,estimatedMinutesWatched',
                dimensions='insightTrafficSourceType',
                sort='-views'
            ).execute()

            if 'rows' not in response:
                return []

            # 결과 파싱
            results = []
            for row in response['rows']:
                source_type = row[0]
                views = int(row[1])
                watch_time = int(row[2])

                results.append({
                    'source_type': source_type,
                    'views': views,
                    'estimated_minutes_watched': watch_time
                })

            return results

        except HttpError as e:
            print(f"❌ 트래픽 소스 조회 실패: {e}")
            return []

    def get_video_analytics(self, channel_id: str, video_ids: List[str],
                           start_date: date, end_date: date) -> List[Dict]:
        """영상별 Analytics 조회"""
        if not video_ids:
            return []

        try:
            # 최대 500개 video filter 제한
            video_filter = ','.join(video_ids[:500])

            response = self.analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date.strftime('%Y-%m-%d'),
                endDate=end_date.strftime('%Y-%m-%d'),
                metrics='views,likes,comments,shares,estimatedMinutesWatched,averageViewDuration',
                dimensions='video',
                filters=f'video=={video_filter}',
                sort='-views'
            ).execute()

            if 'rows' not in response:
                return []

            # 결과 파싱
            results = []
            for row in response['rows']:
                results.append({
                    'video_id': row[0],
                    'views': int(row[1]),
                    'likes': int(row[2]),
                    'comments': int(row[3]),
                    'shares': int(row[4]),
                    'estimated_minutes_watched': int(row[5]),
                    'average_view_duration': int(row[6])
                })

            return results

        except HttpError as e:
            print(f"❌ 영상 Analytics 조회 실패: {e}")
            return []

    def get_video_traffic_sources(self, video_id: str, start_date: date, end_date: date) -> List[Dict]:
        """특정 영상의 트래픽 소스 조회"""
        return self.get_traffic_sources(None, start_date, end_date, video_id=video_id)


# ============================================================================
# 편의 함수
# ============================================================================

def parse_iso_duration(duration_str: str) -> int:
    """ISO 8601 duration을 초로 변환"""
    duration = isodate.parse_duration(duration_str)
    return int(duration.total_seconds())
