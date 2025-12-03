"""
Test 1: Pillow 이미지 생성 테스트
목적: 텍스트, 도형, 이미지 합성 기본 기능 확인
"""
from PIL import Image, ImageDraw, ImageFont
import os

def test_pillow_basic():
    """기본 이미지 생성 및 텍스트 렌더링"""
    print("=" * 50)
    print("Test 1: Pillow 이미지 생성")
    print("=" * 50)

    try:
        # 1. 빈 이미지 생성 (1080x1920, 세로 쇼츠 비율)
        width, height = 1080, 1920
        img = Image.new('RGB', (width, height), color='#667eea')
        print("✅ 빈 이미지 생성 성공 (1080x1920)")

        # 2. 그리기 객체 생성
        draw = ImageDraw.Draw(img)

        # 3. 도형 그리기 - 원
        circle_bbox = [(width//2 - 200, height//2 - 200),
                       (width//2 + 200, height//2 + 200)]
        draw.ellipse(circle_bbox, fill='#FFD700', outline='white', width=10)
        print("✅ 도형 그리기 성공 (원)")

        # 4. 텍스트 그리기
        try:
            # 시스템 폰트 사용 시도
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            # 기본 폰트 fallback
            font = ImageFont.load_default()
            print("⚠️  커스텀 폰트 로드 실패, 기본 폰트 사용")

        text = "TOP 10"
        # 텍스트 중앙 정렬
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_position = ((width - text_width) // 2, 200)
        draw.text(text_position, text, fill='white', font=font)
        print("✅ 텍스트 렌더링 성공")

        # 5. 저장
        output_path = "output/test_pillow.png"
        os.makedirs("output", exist_ok=True)
        img.save(output_path)
        print(f"✅ 이미지 저장 성공: {output_path}")

        # 6. 이미지 정보 출력
        print(f"\n📊 생성된 이미지 정보:")
        print(f"  - 크기: {img.size}")
        print(f"  - 모드: {img.mode}")
        print(f"  - 포맷: {img.format}")

        return True

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pillow_template():
    """템플릿 기반 이미지 생성 (랭킹 카드)"""
    print("\n" + "=" * 50)
    print("Test 1-2: 랭킹 카드 템플릿 생성")
    print("=" * 50)

    try:
        # 랭킹 카드 생성
        card_width, card_height = 1000, 300
        card = Image.new('RGBA', (card_width, card_height), color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(card)

        # 배경 (둥근 모서리 효과)
        draw.rounded_rectangle(
            [(20, 20), (card_width - 20, card_height - 20)],
            radius=30,
            fill='#2d3748',
            outline='#FFD700',
            width=5
        )

        # 랭킹 번호
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()

        draw.text((80, 80), "1", fill='#FFD700', font=font_large)
        draw.text((250, 120), "웃긴 고양이 영상", fill='white', font=font_medium)

        # 저장
        output_path = "output/test_ranking_card.png"
        card.save(output_path)
        print(f"✅ 랭킹 카드 생성 성공: {output_path}")

        return True

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🎨 Pillow 기능 테스트 시작\n")

    result1 = test_pillow_basic()
    result2 = test_pillow_template()

    print("\n" + "=" * 50)
    print("📊 테스트 결과")
    print("=" * 50)
    print(f"기본 이미지 생성: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"랭킹 카드 템플릿: {'✅ PASS' if result2 else '❌ FAIL'}")

    if result1 and result2:
        print("\n✅ 모든 Pillow 테스트 통과!")
    else:
        print("\n❌ 일부 테스트 실패")
