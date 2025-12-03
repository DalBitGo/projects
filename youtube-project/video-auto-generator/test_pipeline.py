"""
Test 5: 전체 파이프라인 통합 테스트
목적: CSV → 이미지 → TTS → 비디오 → 최종 쇼츠 생성
"""
import pandas as pd
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

OUTPUT_DIR = "output/pipeline"

def setup_output_dir():
    """출력 디렉토리 준비"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"✅ 출력 디렉토리: {OUTPUT_DIR}")

def step1_load_csv():
    """Step 1: CSV 데이터 로드"""
    print("\n" + "=" * 50)
    print("Step 1: CSV 데이터 로드")
    print("=" * 50)

    try:
        csv_path = 'data/test_ranking.csv'
        df = pd.read_csv(csv_path)
        print(f"✅ CSV 로드 성공: {len(df)}개 항목")
        print(f"\n데이터 미리보기:")
        print(df[['rank', 'title', 'score']].to_string(index=False))
        return df

    except Exception as e:
        print(f"❌ 에러: {e}")
        return None

def step2_generate_ranking_cards(df):
    """Step 2: 각 랭킹별 카드 이미지 생성"""
    print("\n" + "=" * 50)
    print("Step 2: 랭킹 카드 이미지 생성")
    print("=" * 50)

    try:
        card_paths = []

        for _, row in df.iterrows():
            rank = row['rank']
            title = row['title']
            score = row['score']
            emoji = row['emoji']

            # 카드 생성
            card_width, card_height = 1080, 1920
            card = Image.new('RGB', (card_width, card_height), color='#1a1a2e')

            draw = ImageDraw.Draw(card)

            # 폰트 로드
            try:
                font_rank = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 200)
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
                font_emoji = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 150)
            except:
                font_rank = ImageFont.load_default()
                font_title = ImageFont.load_default()
                font_emoji = ImageFont.load_default()

            # 배경 그라데이션 효과 (간단히 원으로)
            if rank == 1:
                color = '#FFD700'  # 금색
            elif rank == 2:
                color = '#C0C0C0'  # 은색
            elif rank == 3:
                color = '#CD7F32'  # 동색
            else:
                color = '#667eea'  # 보라

            # 중앙 원
            circle_bbox = [(card_width//2 - 300, 400),
                          (card_width//2 + 300, 1000)]
            draw.ellipse(circle_bbox, fill=color)

            # 랭킹 번호
            rank_text = f"#{rank}"
            bbox = draw.textbbox((0, 0), rank_text, font=font_rank)
            text_width = bbox[2] - bbox[0]
            rank_pos = ((card_width - text_width) // 2, 550)
            draw.text(rank_pos, rank_text, fill='white', font=font_rank, stroke_width=5, stroke_fill='black')

            # 이모지
            emoji_bbox = draw.textbbox((0, 0), emoji, font=font_emoji)
            emoji_width = emoji_bbox[2] - emoji_bbox[0]
            emoji_pos = ((card_width - emoji_width) // 2, 350)
            draw.text(emoji_pos, emoji, font=font_emoji)

            # 타이틀
            title_bbox = draw.textbbox((0, 0), title, font=font_title)
            title_width = title_bbox[2] - title_bbox[0]
            title_pos = ((card_width - title_width) // 2, 1200)
            draw.text(title_pos, title, fill='white', font=font_title)

            # 점수
            score_text = f"⭐ {score}"
            score_bbox = draw.textbbox((0, 0), score_text, font=font_title)
            score_width = score_bbox[2] - score_bbox[0]
            score_pos = ((card_width - score_width) // 2, 1350)
            draw.text(score_pos, score_text, fill='#FFD700', font=font_title)

            # 저장
            card_path = os.path.join(OUTPUT_DIR, f"card_{rank}.png")
            card.save(card_path)
            card_paths.append(card_path)

            print(f"  ✅ #{rank} 카드 생성: {card_path}")

        return card_paths

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return []

def step3_generate_narration(df):
    """Step 3: TTS 나레이션 생성"""
    print("\n" + "=" * 50)
    print("Step 3: TTS 나레이션 생성")
    print("=" * 50)

    try:
        audio_paths = []

        for _, row in df.iterrows():
            rank = row['rank']
            title = row['title']
            score = row['score']

            # 나레이션 텍스트
            text = f"{rank}위, {title}, 점수 {score}점"

            # TTS 생성
            tts = gTTS(text=text, lang='ko', slow=False)
            audio_path = os.path.join(OUTPUT_DIR, f"narration_{rank}.mp3")
            tts.save(audio_path)
            audio_paths.append(audio_path)

            print(f"  ✅ #{rank} 나레이션: {audio_path}")

        return audio_paths

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return []

def step4_create_video_clips(card_paths, audio_paths):
    """Step 4: 이미지+오디오 → 비디오 클립 생성"""
    print("\n" + "=" * 50)
    print("Step 4: 비디오 클립 생성")
    print("=" * 50)

    try:
        video_clips = []

        for i, (card_path, audio_path) in enumerate(zip(card_paths, audio_paths), 1):
            # 오디오 길이 확인
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
                capture_output=True,
                text=True
            )
            duration = float(result.stdout.strip())

            # 비디오 생성 (이미지 + 오디오)
            video_path = os.path.join(OUTPUT_DIR, f"clip_{i}.mp4")

            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', card_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-tune', 'stillimage',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                '-t', str(duration + 0.5),  # 약간 여유
                video_path
            ]

            result = subprocess.run(cmd, capture_output=True)

            if result.returncode == 0 and os.path.exists(video_path):
                size = os.path.getsize(video_path)
                print(f"  ✅ 클립 #{i}: {video_path} ({size:,} bytes)")
                video_clips.append(video_path)
            else:
                print(f"  ❌ 클립 #{i} 생성 실패")

        return video_clips

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return []

def step5_concat_clips(video_clips):
    """Step 5: 클립 연결하여 최종 쇼츠 생성"""
    print("\n" + "=" * 50)
    print("Step 5: 최종 쇼츠 생성 (클립 연결)")
    print("=" * 50)

    try:
        # concat 리스트 파일 생성
        concat_list_path = os.path.join(OUTPUT_DIR, "concat_list.txt")
        with open(concat_list_path, 'w') as f:
            for video_path in video_clips:
                # 상대 경로로 변경
                rel_path = os.path.basename(video_path)
                f.write(f"file '{rel_path}'\n")

        # 최종 쇼츠 경로
        final_output = os.path.join(OUTPUT_DIR, "final_shorts.mp4")

        # FFmpeg concat
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', 'concat_list.txt',  # cwd에서 상대 경로로
            '-c', 'copy',
            'final_shorts.mp4'  # cwd에서 상대 경로로
        ]

        result = subprocess.run(cmd, capture_output=True, cwd=OUTPUT_DIR)

        if result.returncode == 0 and os.path.exists(final_output):
            size = os.path.getsize(final_output)
            print(f"\n✅ 최종 쇼츠 생성 성공!")
            print(f"  📹 파일: {final_output}")
            print(f"  📦 크기: {size:,} bytes ({size / 1024 / 1024:.2f} MB)")

            # 비디오 정보 출력
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', final_output],
                capture_output=True,
                text=True
            )
            duration = float(result.stdout.strip())
            print(f"  ⏱️  길이: {duration:.2f}초")

            return final_output
        else:
            print("❌ 최종 쇼츠 생성 실패")
            print(f"stderr: {result.stderr.decode()}")
            print(f"stdout: {result.stdout.decode()}")
            return None

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return None

def print_summary():
    """테스트 요약"""
    print("\n" + "=" * 50)
    print("📊 파이프라인 테스트 완료")
    print("=" * 50)

    print(f"\n생성된 파일:")
    print(f"  - 카드 이미지: {OUTPUT_DIR}/card_*.png")
    print(f"  - 나레이션: {OUTPUT_DIR}/narration_*.mp3")
    print(f"  - 비디오 클립: {OUTPUT_DIR}/clip_*.mp4")
    print(f"  - 최종 쇼츠: {OUTPUT_DIR}/final_shorts.mp4")

    print(f"\n✅ 전체 워크플로우 검증 완료!")
    print(f"   CSV → 이미지 → TTS → 비디오 → 쇼츠")

if __name__ == "__main__":
    print("\n🎬 전체 파이프라인 통합 테스트\n")

    setup_output_dir()

    # Step 1: CSV 로드
    df = step1_load_csv()
    if df is None or df.empty:
        print("\n❌ CSV 로드 실패")
        exit(1)

    # Step 2: 카드 이미지 생성
    card_paths = step2_generate_ranking_cards(df)
    if not card_paths:
        print("\n❌ 카드 이미지 생성 실패")
        exit(1)

    # Step 3: TTS 나레이션 생성
    audio_paths = step3_generate_narration(df)
    if not audio_paths:
        print("\n❌ 나레이션 생성 실패")
        exit(1)

    # Step 4: 비디오 클립 생성
    video_clips = step4_create_video_clips(card_paths, audio_paths)
    if not video_clips:
        print("\n❌ 비디오 클립 생성 실패")
        exit(1)

    # Step 5: 최종 쇼츠 생성
    final_shorts = step5_concat_clips(video_clips)
    if not final_shorts:
        print("\n❌ 최종 쇼츠 생성 실패")
        exit(1)

    print_summary()
