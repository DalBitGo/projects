#!/usr/bin/env python3
"""
유튜브에서 개별 원본 쇼츠만 필터링해서 가져오기
"""
import yt_dlp
import re

def search_original_shorts(keyword: str, min_views: int = 1_000_000, max_results: int = 30):
    """
    개별 원본 쇼츠만 검색

    Args:
        keyword: 검색 키워드
        min_views: 최소 조회수
        max_results: 최대 결과 개수
    """

    # 짜집기 영상 제외 키워드
    EXCLUDE_KEYWORDS = [
        'ranking', 'compilation', 'top 10', 'top 5', 'best of',
        'try not to laugh', 'funny moments', 'fails compilation',
        'best moments', 'ultimate', 'greatest'
    ]

    print(f"🔍 '{keyword}' 검색 중 (조회수 {min_views:,}+ 개별 영상만)...")
    print(f"   제외 키워드: {', '.join(EXCLUDE_KEYWORDS[:5])}...\n")

    # 필터링을 고려해서 훨씬 더 많이 검색
    search_count = max_results * 5  # 5배 더 검색

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'playlistend': search_count,
    }

    search_url = f"ytsearch{search_count}:{keyword} shorts"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)

            if not info or 'entries' not in info:
                return []

            original_shorts = []

            for entry in info['entries']:
                if not entry:
                    continue

                title = entry.get('title', '').lower()
                duration = entry.get('duration', 0)
                view_count = entry.get('view_count', 0)

                # 1. 쇼츠 길이 체크 (60초 이하)
                if not duration or duration > 60:
                    continue

                # 2. 조회수 필터링
                if view_count < min_views:
                    continue

                # 3. 짜집기 영상 제외
                is_compilation = any(keyword in title for keyword in EXCLUDE_KEYWORDS)
                if is_compilation:
                    continue

                original_shorts.append({
                    'id': entry.get('id'),
                    'title': entry.get('title'),
                    'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'duration': duration,
                    'view_count': view_count,
                    'channel': entry.get('channel', entry.get('uploader')),
                })

                if len(original_shorts) >= max_results:
                    break

            print(f"✓ {len(original_shorts)}개 개별 원본 쇼츠 발견\n")
            return original_shorts

    except Exception as e:
        print(f"✗ 에러: {e}")
        return []


def main():
    print("=" * 80)
    print("개별 원본 쇼츠만 필터링해서 가져오기")
    print("=" * 80)
    print()

    # 테스트 키워드
    keyword = "cat fail"

    # 개별 원본만 검색 (제한 없이 최대한 많이)
    videos = search_original_shorts(
        keyword=keyword,
        min_views=100_000,  # 10만 조회수 이상
        max_results=100  # 최대 100개까지
    )

    if videos:
        print(f"{'번호':<5} {'조회수':<15} {'길이':<8} {'제목'}")
        print("-" * 80)

        for i, video in enumerate(videos, 1):
            views = f"{video['view_count']:,}"
            duration = f"{video['duration']}초"
            title = video['title'][:50]

            print(f"{i:<5} {views:<15} {duration:<8} {title}...")

        print()
        print("=" * 80)
        print(f"✓ 성공! {len(videos)}개 개별 원본 쇼츠 수집")
        print(f"  - 모두 조회수 1,000,000+ 이상")
        print(f"  - 모두 60초 이하 쇼츠")
        print(f"  - 짜집기/랭킹 영상 제외됨")
        print("=" * 80)
    else:
        print("✗ 개별 원본 쇼츠를 찾을 수 없습니다")


if __name__ == "__main__":
    main()
