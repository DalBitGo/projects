"""
Test 2: FFmpeg 비디오 합성 테스트
목적: 이미지→비디오 변환, 오디오 믹싱, 전환 효과 확인
"""
import subprocess
import os

def run_ffmpeg_command(cmd, description):
    """FFmpeg 명령 실행 헬퍼"""
    print(f"\n🔧 {description}")
    print(f"명령: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ 성공")
            return True
        else:
            print(f"❌ 실패")
            print(f"stderr: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ 에러: {e}")
        return False

def test_ffmpeg_installed():
    """FFmpeg 설치 확인"""
    print("=" * 50)
    print("Test 2-1: FFmpeg 설치 확인")
    print("=" * 50)

    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg 설치됨: {version_line}")
            return True
        else:
            print("❌ FFmpeg 실행 실패")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg가 설치되지 않음")
        print("설치 방법:")
        print("  Ubuntu: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ 에러: {e}")
        return False

def test_image_to_video():
    """이미지를 비디오로 변환 (3초)"""
    print("\n" + "=" * 50)
    print("Test 2-2: 이미지 → 비디오 변환")
    print("=" * 50)

    # 테스트 이미지가 있는지 확인
    if not os.path.exists("output/test_pillow.png"):
        print("❌ 테스트 이미지 없음. test_pillow.py를 먼저 실행하세요.")
        return False

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        'ffmpeg',
        '-y',  # 덮어쓰기
        '-loop', '1',  # 이미지 반복
        '-i', 'output/test_pillow.png',
        '-c:v', 'libx264',  # H.264 코덱
        '-t', '3',  # 3초
        '-pix_fmt', 'yuv420p',  # 호환성
        '-vf', 'scale=1080:1920',  # 쇼츠 해상도
        'output/test_image_video.mp4'
    ]

    return run_ffmpeg_command(cmd, "이미지 3초 비디오 생성")

def test_create_test_audio():
    """테스트용 오디오 생성 (무음 3초)"""
    print("\n" + "=" * 50)
    print("Test 2-3: 테스트 오디오 생성")
    print("=" * 50)

    cmd = [
        'ffmpeg',
        '-y',
        '-f', 'lavfi',
        '-i', 'anullsrc=r=44100:cl=stereo',
        '-t', '3',
        'output/test_audio.mp3'
    ]

    return run_ffmpeg_command(cmd, "무음 오디오 3초 생성")

def test_video_audio_merge():
    """비디오 + 오디오 병합"""
    print("\n" + "=" * 50)
    print("Test 2-4: 비디오 + 오디오 병합")
    print("=" * 50)

    if not os.path.exists("output/test_image_video.mp4"):
        print("❌ 비디오 파일 없음")
        return False

    if not os.path.exists("output/test_audio.mp3"):
        print("❌ 오디오 파일 없음")
        return False

    cmd = [
        'ffmpeg',
        '-y',
        '-i', 'output/test_image_video.mp4',
        '-i', 'output/test_audio.mp3',
        '-c:v', 'copy',  # 비디오 재인코딩 안함
        '-c:a', 'aac',  # 오디오 AAC 코덱
        '-shortest',  # 짧은 길이에 맞춤
        'output/test_final.mp4'
    ]

    return run_ffmpeg_command(cmd, "비디오+오디오 병합")

def test_multiple_images_concat():
    """여러 이미지를 이어붙이기 (concat)"""
    print("\n" + "=" * 50)
    print("Test 2-5: 여러 이미지 연결 (시퀀스)")
    print("=" * 50)

    # 랭킹 카드가 있는지 확인
    if not os.path.exists("output/test_ranking_card.png"):
        print("⚠️  랭킹 카드 이미지 없음, 스킵")
        return True

    # 각 이미지를 1초씩 비디오로 변환
    images = [
        ("output/test_pillow.png", "output/clip1.mp4"),
        ("output/test_ranking_card.png", "output/clip2.mp4"),
    ]

    for img_path, video_path in images:
        if not os.path.exists(img_path):
            continue

        cmd = [
            'ffmpeg',
            '-y',
            '-loop', '1',
            '-i', img_path,
            '-c:v', 'libx264',
            '-t', '1',  # 1초
            '-pix_fmt', 'yuv420p',
            '-vf', 'scale=1080:1920',
            video_path
        ]
        if not run_ffmpeg_command(cmd, f"클립 생성: {os.path.basename(video_path)}"):
            return False

    # concat 리스트 파일 생성
    concat_list_path = "output/concat_list.txt"
    with open(concat_list_path, 'w') as f:
        for _, video_path in images:
            if os.path.exists(video_path):
                f.write(f"file '{os.path.basename(video_path)}'\n")

    # concat 실행
    cmd = [
        'ffmpeg',
        '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_list_path,
        '-c', 'copy',
        'output/test_concat.mp4'
    ]

    return run_ffmpeg_command(cmd, "클립 연결 (concat)")

def test_check_output_files():
    """생성된 파일 확인"""
    print("\n" + "=" * 50)
    print("📊 생성된 파일 확인")
    print("=" * 50)

    files_to_check = [
        "output/test_image_video.mp4",
        "output/test_audio.mp3",
        "output/test_final.mp4",
        "output/test_concat.mp4"
    ]

    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {file_path} (없음)")

if __name__ == "__main__":
    print("\n🎬 FFmpeg 기능 테스트 시작\n")

    results = {}

    results['installed'] = test_ffmpeg_installed()
    if not results['installed']:
        print("\n❌ FFmpeg가 설치되지 않아 나머지 테스트를 건너뜁니다.")
        exit(1)

    results['image_to_video'] = test_image_to_video()
    results['create_audio'] = test_create_test_audio()
    results['merge'] = test_video_audio_merge()
    results['concat'] = test_multiple_images_concat()

    test_check_output_files()

    print("\n" + "=" * 50)
    print("📊 테스트 결과")
    print("=" * 50)
    print(f"FFmpeg 설치: {'✅ PASS' if results['installed'] else '❌ FAIL'}")
    print(f"이미지→비디오: {'✅ PASS' if results['image_to_video'] else '❌ FAIL'}")
    print(f"오디오 생성: {'✅ PASS' if results['create_audio'] else '❌ FAIL'}")
    print(f"비디오+오디오 병합: {'✅ PASS' if results['merge'] else '❌ FAIL'}")
    print(f"클립 연결: {'✅ PASS' if results['concat'] else '❌ FAIL'}")

    if all(results.values()):
        print("\n✅ 모든 FFmpeg 테스트 통과!")
    else:
        print("\n❌ 일부 테스트 실패")
