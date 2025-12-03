"""
템플릿 스타일 미리보기 테스트 (빠른 버전)
- 이미지 오버레이만 생성하여 템플릿 확인
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from src.core.template_config import TemplateConfigManager
from src.shorts.template_engine import TemplateEngine

OUTPUT_DIR = "output/template_previews"


def test_template_preview(template_name: str):
    """템플릿 미리보기 생성"""
    print(f"\n{'='*60}")
    print(f"미리보기: {template_name.upper()}")
    print(f"{'='*60}")

    try:
        # TemplateEngine 생성
        engine = TemplateEngine(style=template_name, aspect_ratio="9:16")

        # 샘플 데이터
        titles = {
            1: "Amazing Shot",
            2: "Cool Move",
            3: "Epic Trick",
            4: "Great Play",
            5: "Nice Moment"
        }

        # 레일 오버레이 생성 (5위 활성화)
        rail_path = engine.draw_ranking_rail(
            max_rank=5,
            active_rank=3,  # 3위 활성화
            titles=titles
        )

        if os.path.exists(rail_path):
            size = os.path.getsize(rail_path)
            print(f"✅ {template_name.upper()} 미리보기 생성!")
            print(f"   파일: {rail_path}")
            print(f"   크기: {size:,} bytes")

            # 출력 디렉토리로 복사
            import shutil
            output_path = Path(OUTPUT_DIR) / f"{template_name}_preview.png"
            shutil.copy(rail_path, output_path)
            print(f"   복사: {output_path}")

            return True
        else:
            print(f"❌ {template_name.upper()} 미리보기 실패")
            return False

    except Exception as e:
        print(f"❌ {template_name.upper()} 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """모든 템플릿 미리보기 생성"""
    print(f"\n{'='*60}")
    print("🎨 템플릿 스타일 미리보기 테스트")
    print(f"{'='*60}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 템플릿 목록 확인
    manager = TemplateConfigManager()
    all_templates = manager.list_templates()

    print(f"\n사용 가능한 템플릿: {', '.join(all_templates)}")

    # 새로운 템플릿만 테스트
    test_templates = ["neon", "bubble", "retro"]
    results = []

    for template in test_templates:
        success = test_template_preview(template)
        results.append((template, success))

    # 결과 요약
    print(f"\n{'='*60}")
    print("📊 템플릿 미리보기 결과")
    print(f"{'='*60}")

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name.upper()}")

    success_count = sum(1 for _, r in results if r)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100

    print(f"\n총 {total_count}개 템플릿 중 {success_count}개 성공 ({success_rate:.0f}%)")

    if success_rate == 100:
        print("\n🎉 모든 템플릿 미리보기 생성 완료!")
        print(f"\n📁 미리보기 이미지: {OUTPUT_DIR}")
    else:
        print(f"\n⚠️  {total_count - success_count}개 템플릿 실패")


if __name__ == "__main__":
    main()
