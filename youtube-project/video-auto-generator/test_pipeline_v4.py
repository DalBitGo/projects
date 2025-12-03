"""
Step 1: 누적 표시 방식 구현
- 5→4→3→2→1 역순 재생
- 각 클립 재생 시 이전 항목들이 화면에 계속 표시됨
"""
import pandas as pd
import os
import subprocess
import re

OUTPUT_DIR = "output/pipeline_v4"

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

def step1_load_csv_reverse():
    """Step 1: CSV 데이터 로드 (역순 정렬)"""
    print("\n" + "=" * 50)
    print("Step 1: CSV 데이터 로드 (역순)")
    print("=" * 50)

    csv_path = 'data/ranking_with_clips.csv'
    df = pd.read_csv(csv_path)

    # 역순 정렬 (5 → 1)
    df = df.sort_values('rank', ascending=False).reset_index(drop=True)

    print(f"✅ CSV 로드 성공: {len(df)}개 항목")
    print(f"✅ 재생 순서: 5 → 4 → 3 → 2 → 1")
    print(f"\n데이터 미리보기:")
    print(df[['rank', 'title', 'clip_path']].to_string(index=False))
    return df

def step2_process_clips_cumulative(df):
    """Step 2: 누적 표시 방식으로 클립 처리"""
    print("\n" + "=" * 50)
    print("Step 2: 누적 표시 방식 클립 처리")
    print("=" * 50)

    processed_clips = []
    font_path = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

    # 전체 데이터를 딕셔너리로 저장 (rank 기준)
    all_items = {}
    for _, row in df.iterrows():
        all_items[row['rank']] = {
            'title': remove_emoji(row['title']),
            'clip_path': row['clip_path']
        }

    # 역순으로 처리 (5→1)
    for idx, row in df.iterrows():
        current_rank = row['rank']
        current_title = remove_emoji(row['title'])
        clip_path = row['clip_path']

        if not os.path.exists(clip_path):
            print(f"  ⚠️  클립 없음: {clip_path}")
            continue

        output_clip = os.path.join(OUTPUT_DIR, f"clip_{current_rank}_cumulative.mp4")

        print(f"\n  🎬 클립 #{current_rank} 처리 중...")

        # drawtext 필터 구성
        drawtext_filters = []

        # 1. 상단 제목
        drawtext_filters.append(
            f"drawtext=fontfile='{font_path}':text='Ranking Random':fontsize=50:fontcolor=white"
            f":x=50:y=30:borderw=3:bordercolor=black"
        )
        drawtext_filters.append(
            f"drawtext=fontfile='{font_path}':text='Impressive Moments':fontsize=50:fontcolor=yellow"
            f":x=50:y=90:borderw=3:bordercolor=black"
        )

        # 2. 누적 표시: 5부터 current_rank까지 표시 (제목도 모두 표시)
        y_start = 200
        y_gap = 90

        for display_rank in range(5, current_rank - 1, -1):  # 5→current_rank
            item = all_items[display_rank]

            # 색상 결정
            if display_rank == 1:
                color = "yellow"
            elif display_rank == 2:
                color = "silver"
            elif display_rank == 3:
                color = "orange"
            else:
                color = "white"

            # 현재 재생 중인 클립인지 확인
            is_current = (display_rank == current_rank)

            y_pos = y_start + (5 - display_rank) * y_gap

            # 번호 + 제목 모두 표시 (이전 항목도 제목 유지)
            safe_title = item['title'].replace("'", "\\'")

            # 번호 표시
            drawtext_filters.append(
                f"drawtext=fontfile='{font_path}':text='{display_rank}.':fontsize=60:fontcolor={color}"
                f":x=30:y={y_pos}:borderw=3:bordercolor=black"
            )

            # 제목 표시 (모든 항목)
            drawtext_filters.append(
                f"drawtext=fontfile='{font_path}':text='{safe_title}':fontsize=50:fontcolor={color}"
                f":x=120:y={y_pos}:borderw=3:bordercolor=black"
            )

            if is_current:
                print(f"    ✅ 표시: {display_rank}. {item['title']} (현재 재생 중)")
            else:
                print(f"    📌 표시: {display_rank}. {item['title']} (이전 항목, 제목 유지)")

        # FFmpeg 명령
        filter_string = ",".join(drawtext_filters)

        cmd = [
            'ffmpeg', '-y',
            '-i', clip_path,
            '-vf', filter_string,
            '-c:a', 'copy',
            '-t', '8',  # 각 클립 8초
            output_clip
        ]

        result = subprocess.run(cmd, capture_output=True)

        if result.returncode == 0 and os.path.exists(output_clip):
            size = os.path.getsize(output_clip)
            print(f"    ✅ 클립 #{current_rank} 완료: {size:,} bytes")
            processed_clips.append(output_clip)
        else:
            print(f"    ❌ 클립 #{current_rank} 실패")
            stderr = result.stderr.decode()
            if stderr:
                print(f"    오류: {stderr[:300]}")

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

    final_output = os.path.join(OUTPUT_DIR, "final_shorts_v4.mp4")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'concat_list.txt',
        '-c', 'copy',
        'final_shorts_v4.mp4'
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
        return None

def print_summary():
    print("\n" + "=" * 50)
    print("📊 Step 1 완료: 누적 표시 방식")
    print("=" * 50)
    print(f"\n✅ 재생 순서: 5 → 4 → 3 → 2 → 1")
    print(f"✅ 누적 표시:")
    print(f"   - 클립 5: '5' 만")
    print(f"   - 클립 4: '5' + '4'")
    print(f"   - 클립 3: '5' + '4' + '3'")
    print(f"   - 클립 2: '5' + '4' + '3' + '2'")
    print(f"   - 클립 1: '5' + '4' + '3' + '2' + '1'")

if __name__ == "__main__":
    print("\n🎬 Step 1: 누적 표시 방식 구현\n")

    setup_output_dir()

    # Step 1: CSV 로드 (역순)
    df = step1_load_csv_reverse()
    if df is None or df.empty:
        print("\n❌ CSV 로드 실패")
        exit(1)

    # Step 2: 누적 방식 클립 처리
    processed_clips = step2_process_clips_cumulative(df)
    if not processed_clips:
        print("\n❌ 클립 처리 실패")
        exit(1)

    # Step 3: 클립 연결
    final_shorts = step3_concat_clips(processed_clips)
    if not final_shorts:
        print("\n❌ 최종 쇼츠 생성 실패")
        exit(1)

    print_summary()
