"""
새로운 템플릿 스타일 테스트
- Neon, Bubble, Retro 템플릿 테스트
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from src.shorts.ranking import RankingShortsGenerator

OUTPUT_DIR = "output/template_styles"


def test_template(template_name: str):
    """템플릿 테스트"""
    print("\n" + "=" * 60)
    print(f"테스트: {template_name.upper()} 템플릿")
    print("=" * 60)

    csv_path = "data/test_ranking_real.csv"

    if not os.path.exists(csv_path):
        print(f"❌ CSV 파일 없음: {csv_path}")
        return False

    output_dir = f"{OUTPUT_DIR}/{template_name}"
    os.makedirs(output_dir, exist_ok=True)

    try:
        generator = RankingShortsGenerator(style=template_name, aspect_ratio="9:16")

        final_video = generator.generate_from_csv(
            csv_path=csv_path,
            output_dir=output_dir,
            enable_rail=True,
            enable_intro=False
        )

        if os.path.exists(final_video):
            size = os.path.getsize(final_video)
            print(f"\n✅ {template_name.upper()} 템플릿 성공!")
            print(f"   출력: {final_video}")
            print(f"   크기: {size:,} bytes ({size/1024/1024:.2f} MB)")
            return True
        else:
            print(f"\n❌ {template_name.upper()} 템플릿 실패: 출력 파일이 생성되지 않음")
            return False

    except Exception as e:
        print(f"\n❌ {template_name.upper()} 템플릿 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """모든 새 템플릿 테스트"""
    print("\n" + "=" * 60)
    print("🎨 새로운 템플릿 스타일 테스트")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    templates = ["neon", "bubble", "retro"]
    results = []

    for template in templates:
        success = test_template(template)
        results.append((template, success))

    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 템플릿 테스트 결과")
    print("=" * 60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name.upper()}")

    success_count = sum(1 for _, r in results if r)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100

    print(f"\n총 {total_count}개 템플릿 중 {success_count}개 성공 ({success_rate:.0f}%)")

    if success_rate == 100:
        print("\n🎉 모든 템플릿 테스트 통과!")
    else:
        print(f"\n⚠️  {total_count - success_count}개 템플릿 실패")

    print(f"\n출력 디렉토리: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
