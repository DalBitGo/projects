#!/usr/bin/env python3
"""
Playwright 네트워크 가로채기로 TikTok 해시태그 검색 테스트
AI가 제안한 방법 검증
"""
from playwright.sync_api import sync_playwright
import json
import time

TARGET_HASHTAG = "skills"
MAX_ITEMS = 30
TIME_LIMIT_SEC = 25

def scrape_hashtag(hashtag: str = TARGET_HASHTAG) -> list:
    results = []

    def is_hashtag_api(url: str) -> bool:
        # 해시태그 페이지에서 나는 XHR들 중 "challenge/..." 또는 "search/..." 계열만 필터
        return ("/api/challenge/item_list/" in url) or ("/api/search/" in url)

    def on_response(resp):
        try:
            url = resp.url
            # 모든 API 호출 로깅
            if "/api/" in url:
                print(f"  API 호출 감지: {url[:100]}... [Status: {resp.status}]")

            if is_hashtag_api(url) and resp.status == 200:
                content_type = resp.headers.get("content-type", "")
                print(f"  → Content-Type: {content_type}")

                if "application/json" in content_type:
                    try:
                        data = resp.json()
                        print(f"  → JSON 파싱 성공, 키: {list(data.keys())[:10]}")
                    except Exception as json_err:
                        print(f"  → JSON 파싱 실패: {json_err}")
                        text = resp.text()
                        print(f"  → 응답 텍스트 일부: {text[:200]}")
                        return

                    # 엔드포인트마다 구조가 다르므로 안전하게 common 필드만 추려보기
                    candidates = (
                        data.get("itemList") or
                        data.get("item_list") or
                        data.get("aweme_list") or
                        data.get("items") or
                        []
                    )

                    print(f"  ✓ API 응답 발견: {len(candidates)}개 항목")

                    for it in candidates:
                        # 키 이름은 변동 가능. 가장 흔한 맵핑을 시도
                        vid = it.get("id") or it.get("aweme_id") or it.get("video", {}).get("id")
                        stats = it.get("stats") or it.get("statistics") or {}
                        author = it.get("author", {}) or it.get("authorInfo", {})
                        video = it.get("video", {})

                        row = {
                            "tiktok_id": vid,
                            "author": author.get("uniqueId") or author.get("nickname") or author.get("id"),
                            "description": it.get("desc") or it.get("description"),
                            "duration": (video.get("duration") or video.get("duration_sec") or it.get("duration") or 0),
                            "views": stats.get("playCount") or stats.get("play_count") or stats.get("viewCount"),
                            "likes": stats.get("diggCount") or stats.get("like_count"),
                            "comments": stats.get("commentCount") or stats.get("comment_count"),
                            "shares": stats.get("shareCount") or stats.get("share_count"),
                            "download_url": (video.get("downloadAddr") or video.get("download_addr") or video.get("playAddr")),
                            "cover_url": (video.get("cover") or video.get("coverUrl") or video.get("originCover")),
                            "created_at": it.get("createTime") or it.get("create_time"),
                        }
                        # 최소 필수값 보장
                        if row["tiktok_id"] and row not in results:
                            results.append(row)
                            print(f"  - 비디오 추가: {row['tiktok_id'][:20]}... (조회수: {row['views']})")
        except Exception as e:
            print(f"  ✗ 응답 파싱 실패: {e}")

    print("=" * 60)
    print("Playwright 네트워크 가로채기 테스트")
    print("=" * 60)
    print(f"\n해시태그: #{hashtag}")
    print("브라우저 시작 중...\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled"
        ])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1920, "height": 1080},
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }
        )
        # 자동화 탐지 우회
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

        page = context.new_page()
        page.on("response", on_response)

        # 해시태그 페이지로 이동
        print(f"페이지 로딩: https://www.tiktok.com/tag/{hashtag}")
        page.goto(f"https://www.tiktok.com/tag/{hashtag}", timeout=60000, wait_until="domcontentloaded")

        # 무한 스크롤식 로딩
        print(f"\n스크롤하며 데이터 수집 중 (최대 {TIME_LIMIT_SEC}초)...")
        t0 = time.time()
        last_len = 0
        scroll_count = 0

        while (time.time() - t0) < TIME_LIMIT_SEC and len(results) < MAX_ITEMS:
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            page.wait_for_timeout(1200)
            scroll_count += 1

            # 더 안 늘어나면 한 번 더 흔들고 탈출
            if len(results) == last_len:
                page.wait_for_timeout(1000)
                if len(results) == last_len:  # 여전히 안 늘어나면 종료
                    print(f"  데이터가 더 이상 증가하지 않음 (스크롤 {scroll_count}회)")
                    break
            last_len = len(results)

            if scroll_count % 3 == 0:
                print(f"  스크롤 {scroll_count}회 - 현재 {len(results)}개 수집됨")

        browser.close()

    # 중복 제거
    dedup = {r["tiktok_id"]: r for r in results if r.get("tiktok_id")}
    out = list(dedup.values())[:MAX_ITEMS]

    print(f"\n최종 수집: {len(out)}개 비디오")
    return out


if __name__ == "__main__":
    try:
        videos = scrape_hashtag()

        print("\n" + "=" * 60)
        if videos:
            print(f"✓ 성공! {len(videos)}개 비디오 수집")
            print("\n처음 3개 샘플:")
            for i, v in enumerate(videos[:3], 1):
                print(f"\n{i}. ID: {v['tiktok_id']}")
                print(f"   작성자: {v['author']}")
                print(f"   조회수: {v['views']:,}")
                print(f"   좋아요: {v['likes']:,}")
                print(f"   길이: {v['duration']}초")
                print(f"   설명: {v['description'][:50] if v['description'] else 'N/A'}...")

            # JSON으로 저장
            with open("test_result.json", "w", encoding="utf-8") as f:
                json.dump(videos, f, ensure_ascii=False, indent=2)
            print(f"\n전체 결과를 test_result.json에 저장했습니다")
        else:
            print("✗ 실패: 비디오를 찾을 수 없습니다")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
