#!/usr/bin/env python3
"""
유튜브 쇼츠 스크래핑 및 다운로드 테스트
"""
import yt_dlp
import re

def search_youtube_shorts(keyword: str, max_results: int = 10):
    """유튜브에서 쇼츠 검색"""
    print(f"🔍 유튜브에서 '{keyword}' 검색 중...")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # 메타데이터만
        'playlistend': max_results,
    }

    # 유튜브 검색 URL (쇼츠 필터)
    search_url = f"ytsearch{max_results}:{keyword} shorts"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)

            if info and 'entries' in info:
                videos = []
                for entry in info['entries']:
                    if entry:
                        # 쇼츠인지 확인 (60초 이하)
                        duration = entry.get('duration', 0)
                        if duration and duration <= 60:
                            videos.append({
                                'id': entry.get('id'),
                                'title': entry.get('title'),
                                'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                                'duration': duration,
                                'view_count': entry.get('view_count', 0),
                                'channel': entry.get('channel', entry.get('uploader')),
                            })

                print(f"✓ {len(videos)}개 쇼츠 발견\n")
                return videos

    except Exception as e:
        print(f"✗ 에러: {e}")
        return []

    return []


def extract_keywords_from_title(title: str):
    """제목에서 키워드 추출"""
    # 숫자와 특수문자 제거, 주요 단어만 추출
    keywords = re.sub(r'[^a-zA-Z\s]', '', title.lower())
    words = keywords.split()

    # 불용어 제거
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were'}
    keywords = [w for w in words if w not in stopwords and len(w) > 3]

    return ' '.join(keywords[:3])  # 최대 3개 단어


def download_youtube_video(video_url: str, output_path: str = "./downloads"):
    """유튜브 영상 다운로드"""
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{output_path}/%(id)s.%(ext)s',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            return True
    except Exception as e:
        print(f"다운로드 실패: {e}")
        return False


def main():
    print("=" * 70)
    print("유튜브 쇼츠 스크래핑 테스트")
    print("=" * 70)
    print()

    # 1단계: "랭킹 쇼츠" 검색
    print("📋 1단계: '랭킹 쇼츠' 검색")
    print("-" * 70)
    ranking_videos = search_youtube_shorts("ranking shorts", max_results=5)

    if not ranking_videos:
        print("랭킹 쇼츠를 찾을 수 없습니다.")
        return

    # 첫 번째 영상 정보 출력
    first_video = ranking_videos[0]
    print(f"\n첫 번째 영상:")
    print(f"  제목: {first_video['title']}")
    print(f"  URL: {first_video['url']}")
    print(f"  길이: {first_video['duration']}초")
    print(f"  조회수: {first_video['view_count']:,}")

    # 2단계: 제목에서 키워드 추출
    print(f"\n📋 2단계: 제목에서 키워드 추출")
    print("-" * 70)
    keywords = extract_keywords_from_title(first_video['title'])
    print(f"추출된 키워드: '{keywords}'")

    # 3단계: 추출한 키워드로 쇼츠 검색
    print(f"\n📋 3단계: '{keywords}' 키워드로 쇼츠 검색")
    print("-" * 70)
    target_videos = search_youtube_shorts(keywords, max_results=10)

    if target_videos:
        print(f"찾은 쇼츠 {len(target_videos)}개:\n")
        for i, video in enumerate(target_videos[:5], 1):
            print(f"{i}. {video['title'][:60]}...")
            print(f"   조회수: {video['view_count']:,} | 길이: {video['duration']}초")
            print(f"   URL: {video['url']}\n")

    print("=" * 70)
    print("✓ 유튜브 쇼츠 스크래핑 가능!")
    print("=" * 70)


if __name__ == "__main__":
    main()
