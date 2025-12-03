#!/usr/bin/env python3
"""
tiktokapi 라이브러리로 TikTok 해시태그 검색 테스트
"""
import asyncio
from tiktokapi import TikTokApi

async def test_tiktokapi_hashtag():
    print("=" * 60)
    print("tiktokapi로 TikTok 해시태그 검색 테스트")
    print("=" * 60)

    keyword = "skills"
    print(f"\n해시태그: #{keyword}")
    print("데이터 가져오는 중...\n")

    try:
        api = TikTokApi()

        # 해시태그로 비디오 검색
        videos = await api.hashtag(name=keyword).videos(count=10)

        if videos:
            print(f"✓ 성공! {len(videos)}개 비디오 발견\n")

            for i, video in enumerate(videos[:3], 1):
                print(f"\n비디오 {i}:")
                print(f"  ID: {video.id}")
                print(f"  작성자: {video.author.username if hasattr(video, 'author') else 'N/A'}")
                print(f"  설명: {video.desc[:50] if hasattr(video, 'desc') else 'N/A'}...")
                if hasattr(video, 'stats'):
                    print(f"  조회수: {video.stats.get('playCount', 'N/A')}")
                    print(f"  좋아요: {video.stats.get('diggCount', 'N/A')}")

            return True
        else:
            print("✗ 실패: 비디오를 찾을 수 없습니다")
            return False

    except Exception as e:
        print(f"✗ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tiktokapi_hashtag())
    print("\n" + "=" * 60)
    if success:
        print("결과: tiktokapi로 TikTok 스크래핑 가능 ✓")
    else:
        print("결과: tiktokapi로 TikTok 스크래핑 불가능 ✗")
    print("=" * 60)
