"""
Step 2: 템플릿 시스템 구현
- YAML 템플릿 파일 로드
- 폰트, 색상, 위치, 재생 순서 등 커스터마이징
"""
import pandas as pd
import os
import subprocess
import re
import yaml

OUTPUT_DIR = "output/pipeline_v5"

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

def load_template(template_name="default"):
    """템플릿 YAML 파일 로드"""
    print("\n" + "=" * 50)
    print("템플릿 로드")
    print("=" * 50)

    template_path = f"templates/{template_name}.yaml"

    if not os.path.exists(template_path):
        print(f"❌ 템플릿 파일 없음: {template_path}")
        print(f"기본 템플릿 사용")
        template_path = "templates/default.yaml"

    with open(template_path, 'r', encoding='utf-8') as f:
        template = yaml.safe_load(f)

    print(f"✅ 템플릿 로드: {template['name']}")
    print(f"   설명: {template['description']}")
    print(f"   재생 순서: {template['playback']['order']}")
    print(f"   클립 길이: {template['playback']['clip_duration']}초")

    return template

def setup_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"✅ 출력 디렉토리: {OUTPUT_DIR}")

def step1_load_csv(template):
    """Step 1: CSV 데이터 로드 (템플릿에 따라 정렬)"""
    print("\n" + "=" * 50)
    print("Step 1: CSV 데이터 로드")
    print("=" * 50)

    csv_path = 'data/ranking_with_clips.csv'
    df = pd.read_csv(csv_path)

    # 재생 순서에 따라 정렬
    order = template['playback']['order']
    if order == "reverse":
        df = df.sort_values('rank', ascending=False).reset_index(drop=True)
        print(f"✅ 재생 순서: 5 → 4 → 3 → 2 → 1 (역순)")
    else:
        df = df.sort_values('rank', ascending=True).reset_index(drop=True)
        print(f"✅ 재생 순서: 1 → 2 → 3 → 4 → 5 (정순)")

    print(f"✅ CSV 로드 성공: {len(df)}개 항목")
    return df

def step2_process_clips_with_template(df, template):
    """Step 2: 템플릿을 적용하여 클립 처리"""
    print("\n" + "=" * 50)
    print("Step 2: 템플릿 적용 클립 처리")
    print("=" * 50)

    processed_clips = []

    # 템플릿 설정 추출
    fonts = template['fonts']
    colors = template['colors']
    positions = template['positions']
    style = template['style']
    clip_duration = template['playback']['clip_duration']

    font_path = fonts['main']

    # 전체 데이터를 딕셔너리로 저장
    all_items = {}
    for _, row in df.iterrows():
        all_items[row['rank']] = {
            'title': remove_emoji(row['title']),
            'clip_path': row['clip_path']
        }

    # 순서대로 처리
    for idx, row in df.iterrows():
        current_rank = row['rank']
        current_title = remove_emoji(row['title'])
        clip_path = row['clip_path']

        if not os.path.exists(clip_path):
            print(f"  ⚠️  클립 없음: {clip_path}")
            continue

        output_clip = os.path.join(OUTPUT_DIR, f"clip_{current_rank}_template.mp4")

        print(f"\n  🎬 클립 #{current_rank} 처리 중...")

        # drawtext 필터 구성
        drawtext_filters = []

        # 1. 상단 제목
        drawtext_filters.append(
            f"drawtext=fontfile='{font_path}':text='Ranking Random'"
            f":fontsize={fonts['title_size']}:fontcolor={colors['title']}"
            f":x={positions['title_x']}:y={positions['title_y']}"
            f":borderw={style['border_width']}:bordercolor={colors['border']}"
        )
        drawtext_filters.append(
            f"drawtext=fontfile='{font_path}':text='Impressive Moments'"
            f":fontsize={fonts['subtitle_size']}:fontcolor={colors['subtitle']}"
            f":x={positions['subtitle_x']}:y={positions['subtitle_y']}"
            f":borderw={style['border_width']}:bordercolor={colors['border']}"
        )

        # 2. 누적 표시: 재생 순서에 따라 결정
        if template['playback']['order'] == "reverse":
            # 역순: 5부터 current_rank까지
            display_ranks = range(5, current_rank - 1, -1)
        else:
            # 정순: 1부터 current_rank까지
            display_ranks = range(1, current_rank + 1)

        for display_rank in display_ranks:
            item = all_items[display_rank]

            # 색상 결정 (템플릿에서)
            color_key = f"rank{display_rank}"
            color = colors.get(color_key, "white")

            # 현재 재생 중인 클립인지 확인
            is_current = (display_rank == current_rank)

            # y 위치 계산
            if template['playback']['order'] == "reverse":
                y_pos = positions['ranking_start_y'] + (5 - display_rank) * positions['ranking_gap']
            else:
                y_pos = positions['ranking_start_y'] + (display_rank - 1) * positions['ranking_gap']

            # 번호 + 제목 표시
            safe_title = item['title'].replace("'", "\\'")

            # 번호
            drawtext_filters.append(
                f"drawtext=fontfile='{font_path}':text='{display_rank}.'"
                f":fontsize={fonts['ranking_number_size']}:fontcolor={color}"
                f":x={positions['ranking_x']}:y={y_pos}"
                f":borderw={style['border_width']}:bordercolor={colors['border']}"
            )

            # 제목
            drawtext_filters.append(
                f"drawtext=fontfile='{font_path}':text='{safe_title}'"
                f":fontsize={fonts['ranking_title_size']}:fontcolor={color}"
                f":x={positions['ranking_title_x']}:y={y_pos}"
                f":borderw={style['border_width']}:bordercolor={colors['border']}"
            )

            if is_current:
                print(f"    ✅ 표시: {display_rank}. {item['title']} (현재 재생 중)")
            else:
                print(f"    📌 표시: {display_rank}. {item['title']} (유지)")

        # FFmpeg 명령
        filter_string = ",".join(drawtext_filters)

        cmd = [
            'ffmpeg', '-y',
            '-i', clip_path,
            '-vf', filter_string,
            '-c:a', 'copy',
            '-t', str(clip_duration),
            output_clip
        ]

        result = subprocess.run(cmd, capture_output=True)

        if result.returncode == 0 and os.path.exists(output_clip):
            size = os.path.getsize(output_clip)
            print(f"    ✅ 클립 #{current_rank} 완료: {size:,} bytes")
            processed_clips.append(output_clip)
        else:
            print(f"    ❌ 클립 #{current_rank} 실패")

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

    final_output = os.path.join(OUTPUT_DIR, "final_shorts_v5.mp4")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'concat_list.txt',
        '-c', 'copy',
        'final_shorts_v5.mp4'
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

def print_summary(template):
    print("\n" + "=" * 50)
    print("📊 Step 2 완료: 템플릿 시스템")
    print("=" * 50)
    print(f"\n✅ 사용된 템플릿: {template['name']}")
    print(f"✅ 커스터마이징:")
    print(f"   - 폰트 크기: 제목 {template['fonts']['title_size']}, 랭킹 {template['fonts']['ranking_number_size']}")
    print(f"   - 색상: 1위 {template['colors']['rank1']}, 2위 {template['colors']['rank2']}, 3위 {template['colors']['rank3']}")
    print(f"   - 재생 순서: {template['playback']['order']}")
    print(f"   - 클립 길이: {template['playback']['clip_duration']}초")

if __name__ == "__main__":
    import sys

    # 명령줄 인자로 템플릿 선택 가능
    template_name = sys.argv[1] if len(sys.argv) > 1 else "default"

    print(f"\n🎬 Step 2: 템플릿 시스템 구현\n")

    setup_output_dir()

    # 템플릿 로드
    template = load_template(template_name)

    # Step 1: CSV 로드
    df = step1_load_csv(template)
    if df is None or df.empty:
        print("\n❌ CSV 로드 실패")
        exit(1)

    # Step 2: 템플릿 적용 클립 처리
    processed_clips = step2_process_clips_with_template(df, template)
    if not processed_clips:
        print("\n❌ 클립 처리 실패")
        exit(1)

    # Step 3: 클립 연결
    final_shorts = step3_concat_clips(processed_clips)
    if not final_shorts:
        print("\n❌ 최종 쇼츠 생성 실패")
        exit(1)

    print_summary(template)
