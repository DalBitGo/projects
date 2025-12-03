"""
전체 파이프라인 V2 - 샘플 이미지 스타일
왼쪽에 랭킹 1~5 세로 나열 (심플)
"""
import pandas as pd
import os
import subprocess
import re
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

OUTPUT_DIR = "output/pipeline_v2"

def remove_emoji(text):
    """텍스트에서 이모지 제거 (한글 보호)"""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        # u"\U000024C2-\U0001F251"  # 한글 범위와 겹쳐서 제외
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text).strip()

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
        print(df[['rank', 'title', 'emoji']].to_string(index=False))
        return df

    except Exception as e:
        print(f"❌ 에러: {e}")
        return None

def step2_generate_full_ranking_image(df):
    """Step 2: 전체 랭킹을 한 장의 이미지에 표시 (왼쪽 정렬)"""
    print("\n" + "=" * 50)
    print("Step 2: 전체 랭킹 이미지 생성 (왼쪽 정렬)")
    print("=" * 50)

    try:
        # 쇼츠 크기
        width, height = 1080, 1920
        img = Image.new('RGB', (width, height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)

        # 폰트 로드 (한글 지원)
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", 80)
            font_ranking = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", 70)
        except:
            # fallback
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
                font_ranking = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
            except:
                font_title = ImageFont.load_default()
                font_ranking = ImageFont.load_default()

        # 상단 제목
        title_text = "Ranking Random"
        subtitle_text = "Impressive Moments"

        draw.text((50, 80), title_text, fill='white', font=font_title,
                 stroke_width=3, stroke_fill='black')
        draw.text((50, 180), subtitle_text, fill='#FFD700', font=font_title,
                 stroke_width=3, stroke_fill='black')

        # 랭킹 목록 (왼쪽 정렬, 세로로 나열)
        start_y = 350
        line_height = 120

        for _, row in df.iterrows():
            rank = row['rank']
            title = row['title']

            # 제목에서 이모지 제거
            title_clean = remove_emoji(title)

            # 랭킹 텍스트 (번호 + 제목만)
            ranking_text = f"{rank}. {title_clean}"

            # 왼쪽 정렬로 그리기
            y_pos = start_y + (rank - 1) * line_height

            # 랭킹별 색상
            if rank == 1:
                color = '#FFD700'  # 금색
            elif rank == 2:
                color = '#C0C0C0'  # 은색
            elif rank == 3:
                color = '#CD7F32'  # 동색
            else:
                color = 'white'

            draw.text((50, y_pos), ranking_text, fill=color, font=font_ranking,
                     stroke_width=3, stroke_fill='black')

        # 저장
        output_path = os.path.join(OUTPUT_DIR, "full_ranking.png")
        img.save(output_path)
        print(f"✅ 전체 랭킹 이미지 생성: {output_path}")

        return output_path

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return None

def step3_generate_narration(df):
    """Step 3: TTS 나레이션 생성 (전체)"""
    print("\n" + "=" * 50)
    print("Step 3: TTS 나레이션 생성")
    print("=" * 50)

    try:
        # 전체 나레이션 텍스트
        narration_parts = []
        for _, row in df.iterrows():
            rank = row['rank']
            title = row['title']
            narration_parts.append(f"{rank}위, {title}")

        full_text = ". ".join(narration_parts)

        # TTS 생성
        tts = gTTS(text=full_text, lang='ko', slow=False)
        audio_path = os.path.join(OUTPUT_DIR, "full_narration.mp3")
        tts.save(audio_path)

        print(f"✅ 나레이션 생성: {audio_path}")
        print(f"   텍스트: {full_text[:100]}...")

        return audio_path

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return None

def step4_create_final_video(image_path, audio_path):
    """Step 4: 이미지 + 오디오 → 최종 쇼츠 생성"""
    print("\n" + "=" * 50)
    print("Step 4: 최종 쇼츠 생성")
    print("=" * 50)

    try:
        # 오디오 길이 확인
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
            capture_output=True,
            text=True
        )
        duration = float(result.stdout.strip())
        print(f"  오디오 길이: {duration:.2f}초")

        # 최종 비디오 생성
        final_output = os.path.join(OUTPUT_DIR, "final_shorts_v2.mp4")

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            '-t', str(duration + 0.5),
            final_output
        ]

        result = subprocess.run(cmd, capture_output=True)

        if result.returncode == 0 and os.path.exists(final_output):
            size = os.path.getsize(final_output)
            print(f"\n✅ 최종 쇼츠 생성 성공!")
            print(f"  📹 파일: {final_output}")
            print(f"  📦 크기: {size:,} bytes ({size / 1024 / 1024:.2f} MB)")
            print(f"  ⏱️  길이: {duration:.2f}초")

            return final_output
        else:
            print("❌ 비디오 생성 실패")
            return None

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return None

def print_summary():
    """테스트 요약"""
    print("\n" + "=" * 50)
    print("📊 파이프라인 V2 완료")
    print("=" * 50)

    print(f"\n생성된 파일:")
    print(f"  - 전체 랭킹 이미지: {OUTPUT_DIR}/full_ranking.png")
    print(f"  - 나레이션: {OUTPUT_DIR}/full_narration.mp3")
    print(f"  - 최종 쇼츠: {OUTPUT_DIR}/final_shorts_v2.mp4")

    print(f"\n✅ 샘플 이미지 스타일로 생성 완료!")
    print(f"   왼쪽 정렬 + 1~5 세로 나열")

if __name__ == "__main__":
    print("\n🎬 파이프라인 V2 테스트 (샘플 스타일)\n")

    setup_output_dir()

    # Step 1: CSV 로드
    df = step1_load_csv()
    if df is None or df.empty:
        print("\n❌ CSV 로드 실패")
        exit(1)

    # Step 2: 전체 랭킹 이미지 생성
    image_path = step2_generate_full_ranking_image(df)
    if not image_path:
        print("\n❌ 이미지 생성 실패")
        exit(1)

    # Step 3: 나레이션 생성
    audio_path = step3_generate_narration(df)
    if not audio_path:
        print("\n❌ 나레이션 생성 실패")
        exit(1)

    # Step 4: 최종 쇼츠 생성
    final_shorts = step4_create_final_video(image_path, audio_path)
    if not final_shorts:
        print("\n❌ 최종 쇼츠 생성 실패")
        exit(1)

    print_summary()
