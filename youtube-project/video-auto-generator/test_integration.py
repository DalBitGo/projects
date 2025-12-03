"""
통합 테스트: 전체 쇼츠 생성 파이프라인 테스트
- RankingShortsGenerator + TemplateConfig
- 실제 비디오 클립으로 전체 워크플로우 테스트
- 에지 케이스 처리 검증
"""

import os
import sys
import pandas as pd
from pathlib import Path

# 모듈 import
sys.path.append(str(Path(__file__).parent))
from src.shorts.ranking import RankingShortsGenerator
from src.core.template_config import TemplateConfigManager

OUTPUT_DIR = "output/integration_test"

def test_case_1_basic_csv():
    """테스트 1: 기본 CSV 생성 (템플릿 시스템 통합)"""
    print("\n" + "=" * 60)
    print("테스트 1: 기본 CSV 생성 (템플릿 시스템 통합)")
    print("=" * 60)

    # CSV 파일이 있는지 확인하고, 없으면 생성
    csv_path = "data/test_ranking_real.csv"

    # downloads/user_clips의 클립을 사용하여 CSV 생성
    clips_dir = Path("downloads/user_clips")
    clips = sorted(clips_dir.glob("clip_*.mp4"))[:5]

    if len(clips) < 5:
        print(f"❌ Not enough clips in {clips_dir}. Found {len(clips)}, need 5.")
        return False

    # CSV 생성
    data = []
    titles = [
        "Amazing Basketball Shot",
        "Incredible Dance Move",
        "Funny Cat Moment",
        "Epic Skateboard Trick",
        "Cute Dog Playing"
    ]

    for i, (clip, title) in enumerate(zip(clips, titles), 1):
        data.append({
            'rank': i,
            'title': title,
            'clip_path': str(clip),
            'emoji': ['🏀', '💃', '😺', '🛹', '🐕'][i-1],
            'score': 10.0 - (i-1) * 0.2
        })

    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV 생성: {csv_path}")
    print(df)

    # RankingShortsGenerator로 생성
    output_dir = f"{OUTPUT_DIR}/test1_basic"
    os.makedirs(output_dir, exist_ok=True)

    generator = RankingShortsGenerator(style="modern", aspect_ratio="9:16")

    try:
        final_video = generator.generate_from_csv(
            csv_path=csv_path,
            output_dir=output_dir,
            enable_rail=True,
            enable_intro=False  # 인트로는 비활성화 (간단한 테스트)
        )

        if os.path.exists(final_video):
            size = os.path.getsize(final_video)
            print(f"\n✅ 테스트 1 성공!")
            print(f"   출력: {final_video}")
            print(f"   크기: {size:,} bytes ({size/1024/1024:.2f} MB)")
            return True
        else:
            print(f"\n❌ 테스트 1 실패: 출력 파일이 생성되지 않음")
            return False

    except Exception as e:
        print(f"\n❌ 테스트 1 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_case_2_edge_cases():
    """테스트 2: 에지 케이스 처리 (긴 제목, 특수문자)"""
    print("\n" + "=" * 60)
    print("테스트 2: 에지 케이스 처리 (긴 제목, 특수문자)")
    print("=" * 60)

    csv_path = "data/test_edge_cases.csv"

    # downloads/user_clips의 클립 사용
    clips_dir = Path("downloads/user_clips")
    clips = sorted(clips_dir.glob("clip_*.mp4"))[:5]

    if len(clips) < 5:
        print(f"❌ Not enough clips. Found {len(clips)}, need 5.")
        return False

    # 에지 케이스 제목
    edge_case_titles = [
        "This is a very long title that might cause text overflow issues in the video overlay rendering system!!! 😱😱😱",
        "Special chars: <>&'\"\\|{}[]`~!@#$%^&*()",
        "한글 제목도 잘 표시되나요? 🇰🇷",
        "Émojis 🎉🎊🎈🎁🎀🎂 everywhere!",
        ""  # 빈 제목
    ]

    data = []
    for i, (clip, title) in enumerate(zip(clips, edge_case_titles), 1):
        data.append({
            'rank': i,
            'title': title if title else f"Untitled #{i}",
            'clip_path': str(clip),
            'emoji': '🔥',
            'score': 8.5
        })

    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    print(f"✅ 에지 케이스 CSV 생성: {csv_path}")
    print(df)

    # 생성
    output_dir = f"{OUTPUT_DIR}/test2_edge_cases"
    os.makedirs(output_dir, exist_ok=True)

    generator = RankingShortsGenerator(style="modern", aspect_ratio="9:16")

    try:
        final_video = generator.generate_from_csv(
            csv_path=csv_path,
            output_dir=output_dir,
            enable_rail=True,
            enable_intro=False
        )

        if os.path.exists(final_video):
            size = os.path.getsize(final_video)
            print(f"\n✅ 테스트 2 성공!")
            print(f"   출력: {final_video}")
            print(f"   크기: {size:,} bytes ({size/1024/1024:.2f} MB)")
            return True
        else:
            print(f"\n❌ 테스트 2 실패: 출력 파일이 생성되지 않음")
            return False

    except Exception as e:
        print(f"\n❌ 테스트 2 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_case_3_custom_template():
    """테스트 3: 커스텀 템플릿 사용"""
    print("\n" + "=" * 60)
    print("테스트 3: 커스텀 템플릿 사용")
    print("=" * 60)

    # 커스텀 템플릿이 있는지 확인
    custom_templates = list(Path("templates/ranking/custom").glob("*.yaml"))

    if not custom_templates:
        print("⚠️  커스텀 템플릿이 없습니다. 기본 템플릿 사용.")
        template_style = "modern"
    else:
        template_name = custom_templates[0].stem
        template_style = f"custom/{template_name}"
        print(f"✅ 커스텀 템플릿 사용: {template_style}")

    csv_path = "data/test_ranking_real.csv"

    # 테스트 1에서 생성한 CSV 재사용
    if not os.path.exists(csv_path):
        print(f"❌ CSV 파일 없음: {csv_path}")
        print("   테스트 1을 먼저 실행하세요.")
        return False

    output_dir = f"{OUTPUT_DIR}/test3_custom_template"
    os.makedirs(output_dir, exist_ok=True)

    generator = RankingShortsGenerator(style=template_style, aspect_ratio="9:16")

    try:
        final_video = generator.generate_from_csv(
            csv_path=csv_path,
            output_dir=output_dir,
            enable_rail=True,
            enable_intro=False
        )

        if os.path.exists(final_video):
            size = os.path.getsize(final_video)
            print(f"\n✅ 테스트 3 성공!")
            print(f"   템플릿: {template_style}")
            print(f"   출력: {final_video}")
            print(f"   크기: {size:,} bytes ({size/1024/1024:.2f} MB)")
            return True
        else:
            print(f"\n❌ 테스트 3 실패: 출력 파일이 생성되지 않음")
            return False

    except Exception as e:
        print(f"\n❌ 테스트 3 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_case_4_folder_mode():
    """테스트 4: 폴더 입력 모드 (이미 구현됨)"""
    print("\n" + "=" * 60)
    print("테스트 4: 폴더 입력 모드")
    print("=" * 60)

    input_dir = "downloads/user_clips"

    if not os.path.exists(input_dir):
        print(f"❌ 입력 폴더 없음: {input_dir}")
        return False

    output_dir = f"{OUTPUT_DIR}/test4_folder_mode"
    os.makedirs(output_dir, exist_ok=True)

    generator = RankingShortsGenerator(style="modern", aspect_ratio="9:16")

    try:
        final_video = generator.generate_from_dir(
            input_dir=input_dir,
            output_dir=output_dir,
            top=5,  # 상위 5개만
            order="desc",  # 5 → 1 카운트다운
            title_mode="local",  # 파일명에서 제목 추출
            enable_rail=True,
            enable_intro=False
        )

        if os.path.exists(final_video):
            size = os.path.getsize(final_video)
            print(f"\n✅ 테스트 4 성공!")
            print(f"   입력 폴더: {input_dir}")
            print(f"   출력: {final_video}")
            print(f"   크기: {size:,} bytes ({size/1024/1024:.2f} MB)")
            return True
        else:
            print(f"\n❌ 테스트 4 실패: 출력 파일이 생성되지 않음")
            return False

    except Exception as e:
        print(f"\n❌ 테스트 4 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """전체 통합 테스트 실행"""
    print("\n" + "=" * 60)
    print("🎬 전체 쇼츠 생성 파이프라인 통합 테스트")
    print("=" * 60)

    # 출력 디렉토리 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = []

    # 테스트 1: 기본 CSV 생성
    results.append(("기본 CSV 생성", test_case_1_basic_csv()))

    # 테스트 2: 에지 케이스
    results.append(("에지 케이스 처리", test_case_2_edge_cases()))

    # 테스트 3: 커스텀 템플릿
    results.append(("커스텀 템플릿", test_case_3_custom_template()))

    # 테스트 4: 폴더 모드
    results.append(("폴더 입력 모드", test_case_4_folder_mode()))

    # 결과 출력
    print("\n" + "=" * 60)
    print("📊 통합 테스트 결과")
    print("=" * 60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    # 전체 성공률
    success_count = sum(1 for _, r in results if r)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100

    print(f"\n총 {total_count}개 테스트 중 {success_count}개 성공 ({success_rate:.0f}%)")

    if success_rate == 100:
        print("\n🎉 모든 테스트 통과!")
    else:
        print(f"\n⚠️  {total_count - success_count}개 테스트 실패")

    print(f"\n출력 디렉토리: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
