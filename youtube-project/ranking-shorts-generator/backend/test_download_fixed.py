#!/usr/bin/env python3
"""
mp4 포맷으로 제대로 다운로드하는 테스트
"""
import yt_dlp
import os

def download_youtube_shorts_proper(video_url: str, video_id: str, output_dir: str = "./test_downloads_fixed"):
    """제대로 된 mp4로 다운로드"""
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        # mp4 포맷 우선, ffmpeg 없어도 작동하도록
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'{output_dir}/{video_id}.%(ext)s',
        'quiet': False,
        'no_warnings': False,
    }

    try:
        print(f"⬇ 다운로드 중: {video_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)

            # 실제 저장된 파일 경로
            filename = ydl.prepare_filename(info)

            if os.path.exists(filename):
                file_size = os.path.getsize(filename) / (1024 * 1024)
                print(f"✓ 다운로드 완료: {filename} ({file_size:.1f}MB)")

                # 파일 타입 확인
                import subprocess
                result = subprocess.run(['file', filename], capture_output=True, text=True)
                print(f"  파일 타입: {result.stdout.strip()}")

                return filename
            else:
                print("✗ 파일이 생성되지 않았습니다.")
                return None

    except Exception as e:
        print(f"✗ 다운로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("=" * 80)
    print("제대로 된 MP4 다운로드 테스트")
    print("=" * 80)
    print()

    # 쇼츠 검색
    print("1. 쇼츠 검색 중...")
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'playlistend': 3,
    }

    search_url = "ytsearch3:ranking shorts"

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
                        })

            if videos:
                print(f"✓ {len(videos)}개 쇼츠 발견\n")

                # 첫 번째 영상 다운로드
                print("2. 첫 번째 쇼츠 다운로드")
                print("-" * 80)
                first = videos[0]
                print(f"제목: {first['title']}")
                print(f"URL: {first['url']}\n")

                result = download_youtube_shorts_proper(
                    first['url'],
                    first['id'],
                    output_dir="./test_downloads_fixed"
                )

                if result:
                    print("\n" + "=" * 80)
                    print("✓ 성공! 파일을 확인해보세요.")
                    print(f"위치: {result}")
                    print("=" * 80)
                else:
                    print("\n✗ 다운로드 실패")
            else:
                print("✗ 쇼츠를 찾을 수 없습니다")


if __name__ == "__main__":
    main()
