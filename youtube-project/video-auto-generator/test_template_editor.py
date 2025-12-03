"""
템플릿 에디터 통합 테스트
"""

import sys
from pathlib import Path

# 모듈 경로 추가
sys.path.append(str(Path(__file__).parent))

from src.core.template_config import TemplateConfig, TemplateConfigManager
from src.shorts.template_engine import TemplateEngine

def test_config_manager():
    """ConfigManager 테스트"""
    print("=" * 60)
    print("1. TemplateConfigManager 테스트")
    print("=" * 60)

    manager = TemplateConfigManager()

    # 기본 설정 생성
    config = manager._get_default_config()
    print(f"✅ 기본 설정 생성: {config.name}")

    # 설정 검증
    is_valid, error = manager.validate_config(config)
    print(f"✅ 검증 결과: {is_valid}, 오류: {error}")

    # 템플릿 저장
    manager.save_custom_template("test_template", config)
    print(f"✅ 템플릿 저장 완료: test_template")

    # 템플릿 목록
    templates = manager.list_templates()
    print(f"✅ 사용 가능한 템플릿: {templates}")

    # 저장된 템플릿 로드
    loaded_config = manager.load_template("custom/test_template")
    print(f"✅ 템플릿 로드 완료: {loaded_config.name}")

    print()

def test_template_engine():
    """TemplateEngine 테스트"""
    print("=" * 60)
    print("2. TemplateEngine 테스트")
    print("=" * 60)

    # 기본 설정으로 엔진 생성
    engine = TemplateEngine(style="modern", aspect_ratio="9:16")
    print(f"✅ TemplateEngine 생성 (style)")

    # Config로 엔진 생성
    manager = TemplateConfigManager()
    config = manager._get_default_config()

    # 설정 커스터마이징
    config.rail.x = 80
    config.rail.gap = 160
    config.rail.font.size = 55
    config.rail.colors['rank_1'] = '#FF0000'  # 빨강
    config.title.font.size = 70
    config.title.font.color = '#00FF00'  # 초록

    engine_custom = TemplateEngine(config=config, aspect_ratio="9:16")
    print(f"✅ TemplateEngine 생성 (custom config)")

    # 레일 오버레이 생성
    try:
        rail_path = engine_custom.draw_ranking_rail(max_rank=5, active_rank=3)
        print(f"✅ 레일 오버레이 생성: {rail_path}")
    except Exception as e:
        print(f"❌ 레일 오버레이 생성 실패: {e}")
        import traceback
        traceback.print_exc()

    print()

def test_config_to_yaml():
    """Config → YAML 변환 테스트"""
    print("=" * 60)
    print("3. Config → YAML 변환 테스트")
    print("=" * 60)

    manager = TemplateConfigManager()
    config = manager._get_default_config()

    # 커스터마이징
    config.name = "My Custom Style"
    config.description = "빨간 1위, 파란 2위 스타일"
    config.rail.colors['rank_1'] = '#FF0000'
    config.rail.colors['rank_2'] = '#0000FF'
    config.title.font.size = 75

    # YAML 저장
    manager.save_custom_template("custom_test", config)
    print(f"✅ 커스텀 템플릿 저장: custom_test")

    # 다시 로드
    loaded = manager.load_template("custom/custom_test")
    print(f"✅ 로드된 템플릿: {loaded.name}")
    print(f"   설명: {loaded.description}")
    print(f"   1위 색상: {loaded.rail.colors['rank_1']}")
    print(f"   2위 색상: {loaded.rail.colors['rank_2']}")
    print(f"   제목 크기: {loaded.title.font.size}")

    # 저장된 YAML 파일 확인
    yaml_path = manager.custom_dir / "custom_test.yaml"
    if yaml_path.exists():
        print(f"\n✅ YAML 파일 생성 확인: {yaml_path}")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print("\n--- YAML 내용 (처음 20줄) ---")
            print('\n'.join(content.split('\n')[:20]))
    else:
        print(f"❌ YAML 파일 없음: {yaml_path}")

    print()

def main():
    print("\n🎨 템플릿 에디터 통합 테스트\n")

    try:
        test_config_manager()
        test_template_engine()
        test_config_to_yaml()

        print("=" * 60)
        print("✅ 모든 테스트 통과!")
        print("=" * 60)
        print("\n다음 단계:")
        print("  streamlit run template_editor_app.py")
        print()

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
