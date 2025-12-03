"""
AI 제목 생성 테스트
- OpenAI API를 사용한 제목 생성 테스트
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))


def test_ai_title_module():
    """AI 제목 생성 모듈 테스트"""
    print("\n" + "=" * 60)
    print("AI 제목 생성 모듈 테스트")
    print("=" * 60)

    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("\n⚠️  OPENAI_API_KEY가 환경변수에 설정되지 않았습니다.")
        print("\n.env 파일 생성 방법:")
        print("1. 프로젝트 루트에 .env 파일 생성")
        print("2. 다음 내용 추가:")
        print("   OPENAI_API_KEY=sk-your-api-key-here")
        print("\n테스트를 건너뜁니다.")
        return False

    print(f"✅ OpenAI API Key 확인: {api_key[:8]}...")

    # 테스트 비디오
    test_video = "downloads/user_clips/clip_1.mp4"

    if not os.path.exists(test_video):
        print(f"\n⚠️  테스트 비디오 없음: {test_video}")
        print("테스트를 건너뜁니다.")
        return False

    print(f"✅ 테스트 비디오: {test_video}")

    try:
        from src.utils.ai_title_generator import AITitleGenerator

        print("\n🤖 AI 제목 생성 시작...")
        generator = AITitleGenerator()

        title = generator.generate_title_from_video(
            test_video,
            max_length=15,
            language="korean"
        )

        print(f"\n✅ 생성된 제목: '{title}'")
        print(f"   길이: {len(title)}자")

        return True

    except ImportError as e:
        print(f"\n❌ Import 오류: {e}")
        print("   openai 패키지를 설치하세요: pip install openai python-dotenv")
        return False

    except Exception as e:
        print(f"\n❌ AI 제목 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_title_integration():
    """RankingShortsGenerator 통합 테스트"""
    print("\n" + "=" * 60)
    print("RankingShortsGenerator AI 모드 통합 테스트")
    print("=" * 60)

    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("\n⚠️  OPENAI_API_KEY가 설정되지 않아 통합 테스트를 건너뜁니다.")
        print("   대신 local 모드로 폴백되는지 테스트합니다.\n")

    from src.shorts.ranking import RankingShortsGenerator

    input_dir = "downloads/user_clips"

    if not os.path.exists(input_dir):
        print(f"❌ 입력 폴더 없음: {input_dir}")
        return False

    output_dir = "output/ai_title_test"
    os.makedirs(output_dir, exist_ok=True)

    generator = RankingShortsGenerator(style="modern", aspect_ratio="9:16")

    try:
        # AI 모드로 실행 (API 키 없으면 자동으로 local 모드로 폴백)
        print(f"\ntitle_mode='ai'로 generate_from_dir() 호출...\n")

        final_video = generator.generate_from_dir(
            input_dir=input_dir,
            output_dir=output_dir,
            top=3,  # 3개만 (빠른 테스트)
            order="desc",
            title_mode="ai",  # AI 모드
            enable_rail=True,
            enable_intro=False
        )

        if os.path.exists(final_video):
            size = os.path.getsize(final_video)
            print(f"\n✅ 통합 테스트 성공!")
            print(f"   출력: {final_video}")
            print(f"   크기: {size:,} bytes ({size/1024/1024:.2f} MB)")
            return True
        else:
            print(f"\n❌ 통합 테스트 실패: 출력 파일이 생성되지 않음")
            return False

    except Exception as e:
        print(f"\n❌ 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """전체 AI 제목 생성 테스트"""
    print("\n" + "=" * 60)
    print("🤖 AI 제목 생성 시스템 테스트")
    print("=" * 60)

    results = []

    # 테스트 1: AI 제목 생성 모듈
    result1 = test_ai_title_module()
    results.append(("AI 제목 생성 모듈", result1))

    # 테스트 2: 통합 테스트
    result2 = test_ai_title_integration()
    results.append(("RankingShortsGenerator 통합", result2))

    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 AI 제목 생성 테스트 결과")
    print("=" * 60)

    for name, result in results:
        if result is None:
            status = "⏭️  SKIP"
        elif result:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        print(f"{status} - {name}")

    print("\n" + "=" * 60)
    print("📝 참고사항")
    print("=" * 60)
    print("- AI 모드는 OpenAI API 키가 필요합니다")
    print("- API 키가 없으면 자동으로 'local' 모드로 폴백됩니다")
    print("- .env 파일에 OPENAI_API_KEY=sk-... 를 설정하세요")
    print("- pip install openai python-dotenv 필요")


if __name__ == "__main__":
    main()
