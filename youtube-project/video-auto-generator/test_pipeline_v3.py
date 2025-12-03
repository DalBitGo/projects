"""
전체 파이프라인 V3 - 원본 스타일 (실제 비디오 클립 사용)
- 배경: 실제 비디오 클립 재생
- 왼쪽: 1~5 번호 세로 나열
- 강조: 현재 클립의 번호와 제목만 표시
"""
import pandas as pd
import os
import subprocess
import re
from gtts import gTTS

OUTPUT_DIR = "output/pipeline_v3"

def remove_emoji(text):
    """텍스트에서 이모지 제거"""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text).strip()

def setup_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"✅ 출력 디렉토리: {OUTPUT_DIR}")

def step1_load_csv():
    """Step 1: CSV 데이터 로드"""
    print("\n" + "=" * 50)
    print("Step 1: CSV 데이터 로드")
    print("=" * 50)

    csv_path = 'data/ranking_with_clips.csv'
    df = pd.read_csv(csv_path)
    print(f"✅ CSV 로드 성공: {len(df)}개 항목")
    print(f"\n데이터 미리보기:")
    print(df[['rank', 'title', 'clip_path']].to_string(index=False))
    return df

def step2_process_clips_with_overlay(df):
    """Step 2: 각 클립에 오버레이 추가 (FFmpeg drawtext)"""
    print("\n" + "=" * 50)
    print("Step 2: 클립에 오버레이 추가")
    print("=" * 50)

    processed_clips = []

    # 폰트 경로
    font_path = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

    for _, row in df.iterrows():
        rank = row['rank']
        title = remove_emoji(row['title'])
        clip_path = row['clip_path']

        if not os.path.exists(clip_path):
            print(f"  ⚠️  클립 없음: {clip_path}")
            continue

        # 출력 파일명
        output_clip = os.path.join(OUTPUT_DIR, f"clip_{rank}_overlay.mp4")

        # 랭킹별 색상
        if rank == 1:
            rank_color = "yellow"
        elif rank == 2:
            rank_color = "silver"
        elif rank == 3:
            rank_color = "orange"
        else:
            rank_color = "white"

        # FFmpeg drawtext 필터 (복잡한 오버레이)
        # 1. 상단 제목 "Ranking Random"
        # 2. 상단 부제목 "Impressive Moments" (노란색)
        # 3. 왼쪽 번호 1~5 (세로 나열)
        # 4. 현재 클립의 번호와 제목 강조

        drawtext_filter = (
            # 상단 제목
            f"drawtext=fontfile='{font_path}':text='Ranking Random':fontsize=50:fontcolor=white"
            f":x=50:y=30:borderw=3:bordercolor=black,"

            # 상단 부제목 (노란색)
            f"drawtext=fontfile='{font_path}':text='Impressive Moments':fontsize=50:fontcolor=yellow"
            f":x=50:y=90:borderw=3:bordercolor=black,"

            # 왼쪽 번호 1~5 (세로)
            f"drawtext=fontfile='{font_path}':text='1.':fontsize=60:fontcolor={'yellow' if rank==1 else 'white'}"
            f":x=30:y=200:borderw=3:bordercolor=black,"
            f"drawtext=fontfile='{font_path}':text='2.':fontsize=60:fontcolor={'silver' if rank==2 else 'white'}"
            f":x=30:y=290:borderw=3:bordercolor=black,"
            f"drawtext=fontfile='{font_path}':text='3.':fontsize=60:fontcolor={'orange' if rank==3 else 'white'}"
            f":x=30:y=380:borderw=3:bordercolor=black,"
            f"drawtext=fontfile='{font_path}':text='4.':fontsize=60:fontcolor={'white' if rank==4 else 'white'}"
            f":x=30:y=470:borderw=3:bordercolor=black,"
            f"drawtext=fontfile='{font_path}':text='5.':fontsize=60:fontcolor={'white' if rank==5 else 'white'}"
            f":x=30:y=560:borderw=3:bordercolor=black"
        )

        # 현재 클립의 제목 추가 (해당 번호 옆에)
        if rank == 5:
            # 5번은 하단에 큰 텍스트로
            y_pos = 560
            drawtext_filter += (
                f",drawtext=fontfile='{font_path}':text='{title}':fontsize=50:fontcolor={rank_color}"
                f":x=120:y={y_pos}:borderw=3:bordercolor=black"
            )
        else:
            # 1~4번은 해당 번호 옆에
            y_pos = 200 + (rank - 1) * 90
            drawtext_filter += (
                f",drawtext=fontfile='{font_path}':text='{title}':fontsize=40:fontcolor={rank_color}"
                f":x=120:y={y_pos}:borderw=3:bordercolor=black"
            )

        # FFmpeg 명령
        cmd = [
            'ffmpeg', '-y',
            '-i', clip_path,
            '-vf', drawtext_filter,
            '-c:a', 'copy',
            '-t', '8',  # 각 클립 최대 8초
            output_clip
        ]

        result = subprocess.run(cmd, capture_output=True)

        if result.returncode == 0 and os.path.exists(output_clip):
            size = os.path.getsize(output_clip)
            print(f"  ✅ 클립 #{rank} 처리 완료: {output_clip} ({size:,} bytes)")
            processed_clips.append(output_clip)
        else:
            print(f"  ❌ 클립 #{rank} 처리 실패")
            print(f"  stderr: {result.stderr.decode()[:200]}")

    return processed_clips

def step3_concat_clips(clips):
    """Step 3: 클립 연결"""
    print("\n" + "=" * 50)
    print("Step 3: 클립 연결")
    print("=" * 50)

    if not clips:
        print("❌ 처리된 클립이 없음")
        return None

    # concat 리스트
    concat_list_path = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(concat_list_path, 'w') as f:
        for clip in clips:
            rel_path = os.path.basename(clip)
            f.write(f"file '{rel_path}'\n")

    final_output = os.path.join(OUTPUT_DIR, "final_shorts_v3.mp4")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'concat_list.txt',
        '-c', 'copy',
        'final_shorts_v3.mp4'
    ]

    result = subprocess.run(cmd, capture_output=True, cwd=OUTPUT_DIR)

    if result.returncode == 0 and os.path.exists(final_output):
        size = os.path.getsize(final_output)

        # 길이 확인
        duration_result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', final_output],
            capture_output=True, text=True
        )
        duration = float(duration_result.stdout.strip())

        print(f"\n✅ 최종 쇼츠 생성 성공!")
        print(f"  📹 파일: {final_output}")
        print(f"  📦 크기: {size:,} bytes ({size / 1024 / 1024:.2f} MB)")
        print(f"  ⏱️  길이: {duration:.2f}초")

        return final_output
    else:
        print("❌ 클립 연결 실패")
        print(f"stderr: {result.stderr.decode()[:300]}")
        return None

def print_summary():
    print("\n" + "=" * 50)
    print("📊 파이프라인 V3 완료 (원본 스타일)")
    print("=" * 50)
    print(f"\n✅ 실제 비디오 클립 사용")
    print(f"   각 클립마다 랭킹 오버레이 추가")

if __name__ == "__main__":
    print("\n🎬 파이프라인 V3 (원본 스타일 - 실제 클립)\n")

    setup_output_dir()

    # Step 1: CSV 로드
    df = step1_load_csv()
    if df is None or df.empty:
        print("\n❌ CSV 로드 실패")
        exit(1)

    # Step 2: 클립 처리 (오버레이)
    processed_clips = step2_process_clips_with_overlay(df)
    if not processed_clips:
        print("\n❌ 클립 처리 실패")
        exit(1)

    # Step 3: 클립 연결
    final_shorts = step3_concat_clips(processed_clips)
    if not final_shorts:
        print("\n❌ 최종 쇼츠 생성 실패")
        exit(1)

    print_summary()
