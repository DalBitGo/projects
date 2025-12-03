#!/usr/bin/env python3
"""
TikTok 스크래핑 테스트 스크립트
실제로 TikTok에서 데이터를 가져올 수 있는지 확인
"""
import yt_dlp

def test_tiktok_hashtag():
    """TikTok 해시태그 검색 테스트"""
    print("=" * 60)
    print("TikTok 해시태그 스크래핑 테스트")
    print("=" * 60)

    keyword = "skills"
    search_url = f"https://www.tiktok.com/tag/{keyword}"

    print(f"\n검색 URL: {search_url}")
    print("yt-dlp로 정보 추출 중...\n")

    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'extract_flat': True,
        'playlistend': 5,  # 처음 5개만
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)

            if info and 'entries' in info:
                print(f"✓ 성공! {len(info['entries'])}개 비디오 발견\n")

                for i, entry in enumerate(info['entries'][:5], 1):
                    if entry:
                        print(f"\n비디오 {i}:")
                        print(f"  ID: {entry.get('id', 'N/A')}")
                        print(f"  제목: {entry.get('title', 'N/A')}")
                        print(f"  작성자: {entry.get('uploader', 'N/A')}")
                        print(f"  조회수: {entry.get('view_count', 'N/A')}")
                        print(f"  좋아요: {entry.get('like_count', 'N/A')}")
                        print(f"  길이: {entry.get('duration', 'N/A')}초")

                return True
            else:
                print("✗ 실패: 비디오를 찾을 수 없습니다")
                return False

    except Exception as e:
        print(f"✗ 에러 발생: {e}")
        return False

if __name__ == "__main__":
    success = test_tiktok_hashtag()
    print("\n" + "=" * 60)
    if success:
        print("결과: TikTok 스크래핑 가능 ✓")
    else:
        print("결과: TikTok 스크래핑 불가능 ✗")
        print("\n대안: 더미 데이터로 시스템 테스트 진행 가능")
    print("=" * 60)
