#!/usr/bin/env python3
"""
전체 플로우 테스트: 랭킹 쇼츠 검색 → 다운로드 → 키워드 추출 → 재검색 → 다운로드
"""
import yt_dlp
import re
import os
from pathlib import Path

def search_youtube_shorts(keyword: str, max_results: int = 10):
    """유튜브에서 쇼츠 검색"""
    print(f"🔍 '{keyword}' 검색 중...")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'playlistend': max_results,
    }

    search_url = f"ytsearch{max_results}:{keyword} shorts"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)

            if info and 'entries' in info:
                videos = []
                for entry in info['entries']:
                    if entry:
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

                print(f"✓ {len(videos)}개 쇼츠 발견")
                return videos

    except Exception as e:
        print(f"✗ 에러: {e}")
        return []

    return []


def download_youtube_video(video_url: str, video_id: str, output_dir: str = "./test_downloads"):
    """유튜브 영상 다운로드 (ffmpeg 자동 변환)"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # ffmpeg가 자동으로 변환
        'outtmpl': f'{output_dir}/{video_id}.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        print(f"  ⬇ 다운로드 중: {video_id}...", end=" ", flush=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)

        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"✓ ({file_size:.1f}MB)")
            return file_path
        else:
            print("✗ 파일 없음")
            return None
    except Exception as e:
        print(f"✗ 실패: {e}")
        return None


def extract_keywords_from_title(title: str):
    """제목에서 키워드 추출"""
    keywords = re.sub(r'[^a-zA-Z\s]', '', title.lower())
    words = keywords.split()
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were', 'that', 'this'}
    keywords = [w for w in words if w not in stopwords and len(w) > 3]
    return ' '.join(keywords[:3])


def main():
    print("=" * 80)
    print("전체 플로우 테스트: 유튜브 쇼츠 기반 랭킹 영상 생성")
    print("=" * 80)
    print()

    # ============================================================
    # 1단계: "랭킹 쇼츠" 검색
    # ============================================================
    print("📋 STEP 1: '랭킹 쇼츠' 검색")
    print("-" * 80)
    ranking_videos = search_youtube_shorts("ranking shorts", max_results=3)

    if not ranking_videos:
        print("✗ 랭킹 쇼츠를 찾을 수 없습니다.")
        return

    first_video = ranking_videos[0]
    print(f"\n선택된 영상:")
    print(f"  📺 제목: {first_video['title']}")
    print(f"  🔗 URL: {first_video['url']}")
    print(f"  ⏱ 길이: {first_video['duration']}초")
    print(f"  👁 조회수: {first_video['view_count']:,}")
    print()

    # ============================================================
    # 2단계: 첫 번째 영상 다운로드
    # ============================================================
    print("📋 STEP 2: 첫 번째 영상 다운로드")
    print("-" * 80)
    downloaded_file = download_youtube_video(
        first_video['url'],
        first_video['id'],
        output_dir="./test_downloads/step1"
    )

    if not downloaded_file:
        print("✗ 다운로드 실패")
        return

    print(f"✓ 저장 경로: {downloaded_file}")
    print()

    # ============================================================
    # 3단계: 제목에서 키워드 추출
    # ============================================================
    print("📋 STEP 3: 제목에서 키워드 추출")
    print("-" * 80)
    keywords = extract_keywords_from_title(first_video['title'])
    print(f"원본 제목: {first_video['title']}")
    print(f"추출된 키워드: '{keywords}'")
    print()

    # ============================================================
    # 4단계: 추출한 키워드로 쇼츠 재검색
    # ============================================================
    print("📋 STEP 4: 키워드로 쇼츠 재검색")
    print("-" * 80)
    target_videos = search_youtube_shorts(keywords, max_results=10)

    if not target_videos:
        print("✗ 쇼츠를 찾을 수 없습니다.")
        return

    print(f"\n찾은 쇼츠 {len(target_videos)}개:")
    for i, video in enumerate(target_videos[:5], 1):
        print(f"\n{i}. {video['title'][:70]}")
        print(f"   조회수: {video['view_count']:,} | 길이: {video['duration']}초")
    print()

    # ============================================================
    # 5단계: 상위 10개 쇼츠 다운로드
    # ============================================================
    print("📋 STEP 5: 상위 10개 쇼츠 다운로드")
    print("-" * 80)

    downloaded_videos = []
    for i, video in enumerate(target_videos[:10], 1):
        print(f"{i}/10.", end=" ")
        file_path = download_youtube_video(
            video['url'],
            video['id'],
            output_dir="./test_downloads/step2"
        )
        if file_path:
            downloaded_videos.append({
                'file_path': file_path,
                'title': video['title'],
                'views': video['view_count'],
                'duration': video['duration'],
            })

    print()
    print("=" * 80)
    print("✓ 전체 플로우 테스트 완료!")
    print("=" * 80)
    print(f"\n총 {len(downloaded_videos)}개 쇼츠 다운로드 성공")
    print(f"\n저장 위치:")
    print(f"  - STEP 1 영상: ./test_downloads/step1/")
    print(f"  - STEP 2 영상: ./test_downloads/step2/")
    print()

    # 다운로드된 파일 목록
    print("다운로드된 파일:")
    for i, video in enumerate(downloaded_videos, 1):
        print(f"  {i}. {Path(video['file_path']).name} - {video['title'][:50]}...")

    print()
    print("🎉 성공! 유튜브 쇼츠 기반 시스템 작동 확인됨!")


if __name__ == "__main__":
    main()
