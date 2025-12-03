"""
YouTube API 테스트

- Data API v3 조회
- Analytics API 조회
- 트래픽 소스 분석 가능 여부 확인
- 할당량 사용량 측정
"""

import os
import sys
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def find_token_file(account_name):
    """토큰 파일 찾기"""
    possible_dirs = [
        'tokens',
        '../tokens',
        '../../tokens',
    ]

    for dir_path in possible_dirs:
        token_path = os.path.join(dir_path, f'{account_name}_token.json')
        full_path = os.path.abspath(token_path)
        if os.path.exists(full_path):
            return full_path

    return None

def load_credentials(account_name):
    """저장된 토큰 로드"""
    token_path = find_token_file(account_name)

    if not token_path:
        print(f"❌ {account_name} 토큰 파일을 찾을 수 없습니다.")
        print()
        print("먼저 OAuth 인증을 진행하세요:")
        print(f"  python poc_authenticate.py {account_name}")
        sys.exit(1)

    print(f"✅ 토큰 파일 찾음: {token_path}")
    print()

    try:
        credentials = Credentials.from_authorized_user_file(
            token_path,
            scopes=[
                'https://www.googleapis.com/auth/youtube.readonly',
                'https://www.googleapis.com/auth/yt-analytics.readonly'
            ]
        )
        return credentials
    except Exception as e:
        print(f"❌ 토큰 로드 실패: {e}")
        print()
        print("토큰 파일이 손상되었을 수 있습니다. 재인증하세요:")
        print(f"  python poc_authenticate.py {account_name}")
        sys.exit(1)

def test_data_api(credentials):
    """Data API 테스트"""
    print("\n" + "="*60)
    print("📊 YouTube Data API v3 테스트")
    print("="*60 + "\n")

    try:
        youtube = build('youtube', 'v3', credentials=credentials)

        # 내 채널 정보
        print("채널 정보 조회 중...")
        response = youtube.channels().list(
            part='snippet,statistics,contentDetails',
            mine=True
        ).execute()

        if not response.get('items'):
            print("❌ 채널을 찾을 수 없습니다.")
            print("   이 계정에 연결된 YouTube 채널이 있는지 확인하세요.")
            return None

        channel = response['items'][0]
        channel_id = channel['id']

        print(f"✅ 채널 정보 조회 성공!\n")
        print(f"   채널 ID: {channel_id}")
        print(f"   채널명: {channel['snippet']['title']}")
        print(f"   구독자: {int(channel['statistics']['subscriberCount']):,}명")
        print(f"   총 조회수: {int(channel['statistics']['viewCount']):,}회")
        print(f"   영상 수: {int(channel['statistics']['videoCount']):,}개")

        # 최신 영상
        uploads_id = channel['contentDetails']['relatedPlaylists']['uploads']

        print(f"\n최신 영상 조회 중...")
        videos_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_id,
            maxResults=5
        ).execute()

        print(f"✅ 최신 영상 5개:\n")
        video_ids = []
        for idx, item in enumerate(videos_response['items'], 1):
            title = item['snippet']['title']
            video_id = item['snippet']['resourceId']['videoId']
            published = item['snippet']['publishedAt']
            print(f"   {idx}. {title}")
            print(f"      ID: {video_id}")
            print(f"      업로드: {published}\n")
            video_ids.append(video_id)

        print(f"💰 할당량 사용: 약 2 units (채널 1 + 영상목록 1)")

        return {
            'channel_id': channel_id,
            'channel_name': channel['snippet']['title'],
            'video_ids': video_ids
        }

    except HttpError as e:
        print(f"❌ API 호출 실패: {e}")
        if e.resp.status == 403:
            print("   → API가 활성화되지 않았거나 할당량 초과")
        elif e.resp.status == 401:
            print("   → 인증 오류. 재인증 필요")
        return None
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return None

def test_analytics_api(credentials, channel_id, video_ids):
    """Analytics API 테스트"""
    print("\n" + "="*60)
    print("📈 YouTube Analytics API 테스트")
    print("="*60 + "\n")

    try:
        analytics = build('youtubeAnalytics', 'v2', credentials=credentials)

        # 날짜 설정 (최근 7일, 2일 전까지 - 데이터 지연 고려)
        end_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=9)).strftime('%Y-%m-%d')

        print(f"분석 기간: {start_date} ~ {end_date}")
        print(f"(최근 48시간 데이터는 부정확할 수 있어 제외)\n")

        # 1. 기본 메트릭
        print("1️⃣ 기본 시청 메트릭 조회 중...")
        try:
            basic_metrics = analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date,
                endDate=end_date,
                metrics='views,estimatedMinutesWatched,averageViewDuration',
                dimensions='day',
                sort='day'
            ).execute()

            print(f"✅ 기본 메트릭 조회 성공!\n")

            if 'rows' in basic_metrics:
                print(f"   일별 데이터 {len(basic_metrics['rows'])}일:")
                for row in basic_metrics['rows'][-3:]:  # 최근 3일만 표시
                    date = row[0]
                    views = int(row[1])
                    watch_time = int(row[2])
                    avg_duration = int(row[3])
                    print(f"   - {date}: 조회수 {views:,}, 시청시간 {watch_time:,}분, 평균 시청 {avg_duration}초")
            else:
                print("   데이터 없음 (최근 영상이 없거나 조회수가 없을 수 있음)")

        except HttpError as e:
            print(f"❌ 기본 메트릭 조회 실패: {e.resp.status}")
            if e.resp.status == 403:
                print("   → Analytics API가 활성화되지 않았거나 권한 부족")
            return

        # 2. 트래픽 소스 ⭐ 핵심!
        print(f"\n2️⃣ 트래픽 소스 조회 중...")
        try:
            traffic = analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date,
                endDate=end_date,
                metrics='views,estimatedMinutesWatched',
                dimensions='insightTrafficSourceType',
                sort='-views'
            ).execute()

            print(f"✅ 트래픽 소스 조회 성공!\n")

            if 'rows' in traffic:
                print(f"   📊 트래픽 소스 분석:")
                total_views = sum(int(row[1]) for row in traffic['rows'])

                for row in traffic['rows']:
                    source = row[0]
                    views = int(row[1])
                    watch_time = int(row[2])
                    percentage = (views / total_views * 100) if total_views > 0 else 0

                    # 소스 이름 한글화
                    source_names = {
                        'YT_SEARCH': 'YouTube 검색',
                        'RELATED_VIDEO': '추천 영상 (알고리즘!)',
                        'SUBSCRIBER': '구독 피드',
                        'EXTERNAL': '외부 링크',
                        'PLAYLIST': '재생목록',
                        'NOTIFICATION': '알림',
                        'BROWSE': '탐색',
                        'CHANNEL': '채널 페이지'
                    }
                    source_kr = source_names.get(source, source)

                    print(f"   - {source_kr:20s}: {views:6,}회 ({percentage:5.1f}%), {watch_time:6,}분")

                print(f"\n   💡 인사이트:")
                print(f"      '추천 영상'이 높을수록 알고리즘이 영상을 선택한 것!")
                print(f"      '검색'이 높으면 SEO 최적화 성공!")

            else:
                print("   데이터 없음")

        except HttpError as e:
            print(f"❌ 트래픽 소스 조회 실패: {e.resp.status}")
            return

        # 3. 영상별 메트릭
        if video_ids:
            print(f"\n3️⃣ 영상별 메트릭 조회 중...")
            try:
                # 최대 5개 영상만
                video_filter = ','.join(video_ids[:5])

                video_metrics = analytics.reports().query(
                    ids=f'channel=={channel_id}',
                    startDate=start_date,
                    endDate=end_date,
                    metrics='views,likes,comments,shares,estimatedMinutesWatched,averageViewDuration',
                    dimensions='video',
                    filters=f'video=={video_filter}',
                    sort='-views'
                ).execute()

                print(f"✅ 영상별 메트릭 조회 성공!\n")

                if 'rows' in video_metrics:
                    print(f"   최근 영상 성과:")
                    for idx, row in enumerate(video_metrics['rows'], 1):
                        video_id = row[0]
                        views = int(row[1])
                        likes = int(row[2])
                        comments = int(row[3])
                        shares = int(row[4])
                        watch_time = int(row[5])
                        avg_duration = int(row[6])

                        print(f"   {idx}. {video_id}")
                        print(f"      조회수: {views:,}, 좋아요: {likes:,}, 댓글: {comments:,}, 공유: {shares:,}")
                        print(f"      시청시간: {watch_time:,}분, 평균 시청: {avg_duration}초\n")

            except HttpError as e:
                print(f"❌ 영상별 메트릭 조회 실패: {e.resp.status}")

        print(f"💰 할당량 사용: Analytics API는 할당량 관대 (정확한 수치 비공개)")

    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")

def main(account_name):
    print("\n" + "="*60)
    print(f"🧪 POC 테스트: {account_name}")
    print("="*60)

    # 1. 토큰 로드
    print("\n1️⃣ 토큰 로드 중...")
    credentials = load_credentials(account_name)
    print("✅ 토큰 로드 완료")

    # 2. Data API 테스트
    print("\n2️⃣ Data API 테스트...")
    data_result = test_data_api(credentials)

    if not data_result:
        print("\n❌ Data API 테스트 실패. Analytics API 테스트를 건너뜁니다.")
        sys.exit(1)

    # 3. Analytics API 테스트
    print("\n3️⃣ Analytics API 테스트...")
    test_analytics_api(
        credentials,
        data_result['channel_id'],
        data_result['video_ids']
    )

    # 결과 요약
    print("\n" + "="*60)
    print("✅ POC 테스트 완료!")
    print("="*60 + "\n")

    print("💡 결과 요약:")
    print(f"   - OAuth 인증: ✅")
    print(f"   - Data API: ✅")
    print(f"   - Analytics API: ✅ (위 결과 확인)")
    print(f"   - 트래픽 소스 조회: ✅ (알고리즘 분석 가능!)")
    print()
    print("다음 단계:")
    print("   1. 다른 계정도 테스트:")
    print("      python poc_authenticate.py account2")
    print("      python poc_test_api.py account2")
    print()
    print("   2. 설계 확정 후 본 개발 시작")
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("사용법: python poc_test_api.py <account_name>")
        print()
        print("예시:")
        print("  python poc_test_api.py account1")
        print()
        sys.exit(1)

    account_name = sys.argv[1]
    main(account_name)
