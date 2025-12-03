"""
CLI로 쇼츠 생성 (Web UI 없이)
전체 워크플로우 테스트
"""
import pandas as pd
import os
import subprocess
import yaml
import argparse

def remove_emoji(text):
    """텍스트에서 이모지 제거"""
    import re
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text).strip()

def load_template(template_name):
    """템플릿 로드"""
    template_path = f"templates/{template_name}.yaml"
    with open(template_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_shorts_cli(csv_path, template_name, output_dir):
    """CLI로 쇼츠 생성"""
    print("\n🎬 YouTube 쇼츠 생성기 (CLI)\n")

    os.makedirs(output_dir, exist_ok=True)

    # 1. CSV 로드
    print("=" * 50)
    print("1. CSV 데이터 로드")
    print("=" * 50)

    df = pd.read_csv(csv_path)
    print(f"✅ CSV 로드: {len(df)}개 항목\n")

    # 2. 템플릿 로드
    print("=" * 50)
    print("2. 템플릿 로드")
    print("=" * 50)

    template = load_template(template_name)
    print(f"✅ 템플릿: {template['name']}")
    print(f"   - 재생 순서: {template['playback']['order']}")
    print(f"   - 클립 길이: {template['playback']['clip_duration']}초\n")

    # 3. 정렬
    if template['playback']['order'] == "reverse":
        df = df.sort_values('rank', ascending=False).reset_index(drop=True)
    else:
        df = df.sort_values('rank', ascending=True).reset_index(drop=True)

    # 4. 전체 데이터 딕셔너리
    all_items = {}
    for _, row in df.iterrows():
        all_items[row['rank']] = {
            'title': remove_emoji(row['title']),
            'clip_path': row['clip_path']
        }

    # 5. 클립 처리
    print("=" * 50)
    print("3. 클립 처리")
    print("=" * 50)

    fonts = template['fonts']
    colors = template['colors']
    positions = template['positions']
    style = template['style']
    clip_duration = template['playback']['clip_duration']
    font_path = fonts['main']

    processed_clips = []

    for idx, (_, row) in enumerate(df.iterrows()):
        current_rank = row['rank']
        clip_path = row['clip_path']

        if not os.path.exists(clip_path):
            print(f"  ⚠️  클립 없음: {clip_path}")
            continue

        output_clip = os.path.join(output_dir, f"clip_{current_rank}.mp4")

        print(f"\n  🎬 클립 #{current_rank} 처리 중...")

        # drawtext 필터
        drawtext_filters = []

        # 제목
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

        # 모든 랭킹 번호 표시 (1~5, 1이 맨 위)
        for display_rank in range(1, 6):
            color = colors.get(f"rank{display_rank}", "white")

            # y 위치: 1이 맨 위, 5가 맨 밑
            y_pos = positions['ranking_start_y'] + (display_rank - 1) * positions['ranking_gap']

            # 번호는 항상 표시
            drawtext_filters.append(
                f"drawtext=fontfile='{font_path}':text='{display_rank}.'"
                f":fontsize={fonts['ranking_number_size']}:fontcolor={color}"
                f":x={positions['ranking_x']}:y={y_pos}"
                f":borderw={style['border_width']}:bordercolor={colors['border']}"
            )

            # 제목 누적 표시: 역순일 때는 5부터 current_rank까지 모두 표시
            should_show_title = False
            if template['playback']['order'] == "reverse":
                # 역순: 5→1, current_rank 이상만 제목 표시
                should_show_title = (display_rank >= current_rank)
            else:
                # 정순: 1→5, current_rank 이하만 제목 표시
                should_show_title = (display_rank <= current_rank)

            if should_show_title and display_rank in all_items:
                item = all_items[display_rank]
                safe_title = item['title'].replace("'", "\\'")

                drawtext_filters.append(
                    f"drawtext=fontfile='{font_path}':text='{safe_title}'"
                    f":fontsize={fonts['ranking_title_size']}:fontcolor={color}"
                    f":x={positions['ranking_title_x']}:y={y_pos}"
                    f":borderw={style['border_width']}:bordercolor={colors['border']}"
                )

        filter_string = ",".join(drawtext_filters)

        # 쇼츠 비율 (1080x1920) - 원본 비율로 전체 화면 채우기 (크롭)
        vf_with_scale = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,{filter_string}"

        cmd = [
            'ffmpeg', '-y',
            '-i', clip_path,
            '-vf', vf_with_scale,
            '-c:a', 'aac',  # 오디오 재인코딩
            '-b:a', '192k',
            '-t', str(clip_duration),
            output_clip
        ]

        result = subprocess.run(cmd, capture_output=True)

        if result.returncode == 0:
            print(f"    ✅ 완료")
            processed_clips.append(output_clip)
        else:
            print(f"    ❌ 실패")

    # 6. 클립 연결
    print("\n" + "=" * 50)
    print("4. 클립 연결")
    print("=" * 50)

    concat_list_path = os.path.join(output_dir, "concat_list.txt")
    with open(concat_list_path, 'w') as f:
        for clip in processed_clips:
            f.write(f"file '{os.path.basename(clip)}'\n")

    final_output = os.path.join(output_dir, "final_shorts.mp4")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'concat_list.txt',
        '-c', 'copy',
        'final_shorts.mp4'
    ]

    result = subprocess.run(cmd, capture_output=True, cwd=output_dir)

    if result.returncode == 0 and os.path.exists(final_output):
        size = os.path.getsize(final_output)

        # 길이
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
        print("❌ 생성 실패")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube 쇼츠 생성기 (CLI)")
    parser.add_argument("--csv", default="data/ranking_with_clips.csv", help="CSV 파일 경로")
    parser.add_argument("--template", default="default", choices=["default", "modern", "minimal"], help="템플릿 선택")
    parser.add_argument("--output", default="output/cli_test", help="출력 디렉토리")

    args = parser.parse_args()

    result = generate_shorts_cli(args.csv, args.template, args.output)

    if result:
        print(f"\n🎉 성공! 생성된 파일: {result}")
    else:
        print(f"\n❌ 실패")
