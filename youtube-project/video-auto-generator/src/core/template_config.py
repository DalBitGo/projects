"""
Template Configuration Management
Handles template config loading, validation, and customization
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Tuple, Dict, List, Any
from pathlib import Path
import yaml
import re
import os


@dataclass
class FontConfig:
    """폰트 설정"""
    family: str = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    size: int = 60
    color: str = "#FFFFFF"


@dataclass
class PositionConfig:
    """위치 설정"""
    x: int = 540
    y: int = 1650
    alignment: str = "center"  # left, center, right
    max_width: Optional[int] = None


@dataclass
class BackgroundConfig:
    """배경 설정"""
    enabled: bool = False
    color: str = "#000000"
    opacity: float = 0.7
    border_radius: int = 20
    padding: Tuple[int, int, int, int] = (20, 40, 20, 40)  # top, right, bottom, left


@dataclass
class EffectsConfig:
    """효과 설정"""
    border_width: int = 2
    border_color: str = "#000000"
    shadow_enabled: bool = False
    shadow_color: str = "#00000080"
    shadow_offset: Tuple[int, int] = (2, 2)
    glow_enabled: bool = False
    glow_color: str = "#FFFFFF"
    glow_radius: int = 10


@dataclass
class RailConfig:
    """숫자 레일 설정"""
    enabled: bool = True
    x: int = 60
    y_start: int = 300
    gap: int = 150
    alignment: str = "left"
    font: FontConfig = field(default_factory=lambda: FontConfig(size=48))
    colors: Dict[str, str] = field(default_factory=lambda: {
        'rank_1': '#FFD700',
        'rank_2': '#C0C0C0',
        'rank_3': '#CD7F32',
        'default': '#667eea'
    })
    effects: EffectsConfig = field(default_factory=EffectsConfig)
    active_highlight: Dict[str, Any] = field(default_factory=lambda: {
        'opacity': 1.0,
        'scale': 1.0,
        'glow_enabled': True,
        'glow_color': '#FFFFFF',
        'glow_radius': 10
    })
    inactive_opacity: float = 0.3
    active_stroke: int = 4
    # 제목 관련 설정
    title_enabled: bool = True
    title_offset_x: int = 100  # 숫자로부터 제목까지 거리
    title_font_size: int = 40  # 제목 폰트 크기


@dataclass
class TitleConfig:
    """제목 설정"""
    enabled: bool = True
    font: FontConfig = field(default_factory=lambda: FontConfig(size=60))
    position: PositionConfig = field(default_factory=lambda: PositionConfig(x=540, y=1650))
    background: BackgroundConfig = field(default_factory=lambda: BackgroundConfig(enabled=True))
    effects: EffectsConfig = field(default_factory=EffectsConfig)


@dataclass
class HeaderConfig:
    """헤더 설정"""
    enabled: bool = True
    main_title: Dict[str, Any] = field(default_factory=lambda: {
        'text': 'Ranking Random',
        'font_size': 56,
        'color': '#FFFFFF',
        'position': [540, 80],
        'alignment': 'center',
        'stroke_width': 0,
        'stroke_color': '#000000'
    })
    subtitle: Dict[str, Any] = field(default_factory=lambda: {
        'text': 'Impressive Moments',
        'font_size': 36,
        'color': '#CCCCCC',
        'position': [540, 150],
        'alignment': 'center',
        'stroke_width': 0,
        'stroke_color': '#000000'
    })
    background: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': False,
        'color': '#000000',
        'opacity': 0.5
    })


@dataclass
class GlobalConfig:
    """전역 설정"""
    resolution: Dict[str, int] = field(default_factory=lambda: {'width': 1080, 'height': 1920})
    background: Dict[str, Any] = field(default_factory=lambda: {
        'blur_strength': 50,
        'vignette_enabled': True,
        'vignette_opacity': 0.3,
        'color_overlay': '#00000000'
    })
    safe_area: Dict[str, int] = field(default_factory=lambda: {'horizontal': 60, 'vertical': 100})
    clip_area: Dict[str, Any] = field(default_factory=lambda: {
        'width': 900,
        'height': 1600,
        'position': 'center'
    })


@dataclass
class PlaybackConfig:
    """재생 설정"""
    order: str = "reverse"  # reverse (5→1), forward (1→5)
    clip_duration: int = 8


@dataclass
class TemplateConfig:
    """전체 템플릿 설정"""
    name: str = "Custom Template"
    description: str = "User customized template"
    aspect_ratio: str = "9:16"
    rail: RailConfig = field(default_factory=RailConfig)
    title: TitleConfig = field(default_factory=TitleConfig)
    header: HeaderConfig = field(default_factory=HeaderConfig)
    global_settings: GlobalConfig = field(default_factory=GlobalConfig)
    playback: PlaybackConfig = field(default_factory=PlaybackConfig)


class TemplateConfigManager:
    """템플릿 설정 관리자"""

    def __init__(self):
        self.templates_dir = Path("templates/ranking")
        self.custom_dir = self.templates_dir / "custom"
        self.custom_dir.mkdir(parents=True, exist_ok=True)

    def load_template(self, name: str) -> TemplateConfig:
        """
        템플릿 로드 (YAML → dataclass)

        Args:
            name: 템플릿 이름 (예: modern, custom/my_style, neon)

        Returns:
            TemplateConfig 객체
        """
        # 경로 탐색 우선순위:
        # 1. custom/{name}.yaml
        # 2. templates/ranking/{name}/config.yaml
        # 3. templates/{name}.yaml (루트 템플릿)

        yaml_path = None

        if name.startswith("custom/"):
            yaml_path = self.custom_dir / f"{name[7:]}.yaml"
        else:
            # 폴더 기반 템플릿 (templates/ranking/{name}/config.yaml)
            path1 = self.templates_dir / name / "config.yaml"
            # 루트 템플릿 (templates/{name}.yaml)
            path2 = Path("templates") / f"{name}.yaml"

            if path1.exists():
                yaml_path = path1
            elif path2.exists():
                yaml_path = path2

        if yaml_path is None or not yaml_path.exists():
            print(f"⚠️ Template not found: {name}, using default")
            return self._get_default_config()

        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return self._dict_to_config(data)
        except Exception as e:
            print(f"⚠️ Failed to load template: {e}, using default")
            return self._get_default_config()

    def save_custom_template(self, name: str, config: TemplateConfig):
        """
        커스텀 템플릿 저장 (dataclass → YAML)

        Args:
            name: 저장할 템플릿 이름
            config: TemplateConfig 객체
        """
        # 파일명 정리 (공백, 특수문자 제거)
        safe_name = re.sub(r'[^\w\-]', '_', name)
        yaml_path = self.custom_dir / f"{safe_name}.yaml"

        data = self._config_to_dict(config)

        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        print(f"✅ Template saved: {yaml_path}")

    def list_templates(self) -> List[str]:
        """사용 가능한 템플릿 목록 반환"""
        templates = []

        # 기본 템플릿 (폴더 기반: templates/ranking/{name}/config.yaml)
        if self.templates_dir.exists():
            for folder in self.templates_dir.iterdir():
                if folder.is_dir() and folder.name != "custom":
                    config_file = folder / "config.yaml"
                    if config_file.exists():
                        templates.append(folder.name)

        # 루트 템플릿 (templates/{name}.yaml)
        templates_root = Path("templates")
        if templates_root.exists():
            for file in templates_root.glob("*.yaml"):
                if file.stem not in templates:  # 중복 방지
                    templates.append(file.stem)

        # 커스텀 템플릿
        if self.custom_dir.exists():
            for file in self.custom_dir.glob("*.yaml"):
                templates.append(f"custom/{file.stem}")

        return sorted(templates)

    def validate_config(self, config: TemplateConfig) -> Tuple[bool, str]:
        """
        설정 검증

        Args:
            config: TemplateConfig 객체

        Returns:
            (검증 성공 여부, 에러 메시지)
        """
        # 색상 형식 체크
        if not self._is_valid_color(config.title.font.color):
            return False, f"Invalid title color: {config.title.font.color}"

        for color_key, color_value in config.rail.colors.items():
            if not self._is_valid_color(color_value):
                return False, f"Invalid rail color ({color_key}): {color_value}"

        # 범위 체크
        if not (20 <= config.title.font.size <= 120):
            return False, f"Title font size out of range: {config.title.font.size}"

        if not (20 <= config.rail.font.size <= 120):
            return False, f"Rail font size out of range: {config.rail.font.size}"

        if not (0 <= config.rail.x <= 500):
            return False, f"Rail X position out of range: {config.rail.x}"

        # 해상도 체크
        width = config.global_settings.resolution['width']
        height = config.global_settings.resolution['height']
        if width < 100 or height < 100 or width > 4000 or height > 4000:
            return False, f"Invalid resolution: {width}x{height}"

        return True, ""

    def _is_valid_color(self, color: str) -> bool:
        """
        색상 형식 검증 (#RRGGBB or #RRGGBBAA)

        Args:
            color: 색상 문자열

        Returns:
            유효 여부
        """
        return bool(re.match(r'^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$', color))

    def _dict_to_config(self, data: Dict) -> TemplateConfig:
        """
        YAML dict → dataclass 변환

        Args:
            data: YAML에서 로드한 dict

        Returns:
            TemplateConfig 객체
        """
        # 기본값으로 시작
        config = self._get_default_config()

        # 이름/설명
        config.name = data.get('name', config.name)
        config.description = data.get('description', config.description)
        config.aspect_ratio = data.get('aspect_ratio', config.aspect_ratio)

        # Rail 설정
        if 'rail' in data:
            rail_data = data['rail']
            config.rail.enabled = rail_data.get('enabled', True)
            config.rail.x = rail_data.get('x', config.rail.x)
            config.rail.y_start = rail_data.get('y_start', config.rail.y_start)
            config.rail.gap = rail_data.get('gap', config.rail.gap)
            config.rail.inactive_opacity = rail_data.get('inactive_opacity', config.rail.inactive_opacity)
            config.rail.active_stroke = rail_data.get('active_stroke', config.rail.active_stroke)

            if 'font' in rail_data:
                config.rail.font.size = rail_data['font'].get('size', config.rail.font.size)
                config.rail.font.family = rail_data['font'].get('family', config.rail.font.family)

            if 'colors' in rail_data:
                config.rail.colors.update(rail_data['colors'])

            # 제목 설정 (새 필드)
            config.rail.title_enabled = rail_data.get('title_enabled', True)
            config.rail.title_offset_x = rail_data.get('title_offset_x', 100)
            config.rail.title_font_size = rail_data.get('title_font_size', 40)

        # Title 설정
        if 'title' in data:
            title_data = data['title']
            config.title.enabled = title_data.get('enabled', True)

            if 'font' in title_data:
                config.title.font.size = title_data['font'].get('size', config.title.font.size)
                config.title.font.color = title_data['font'].get('color', config.title.font.color)
                config.title.font.family = title_data['font'].get('family', config.title.font.family)

            if 'position' in title_data:
                config.title.position.x = title_data['position'].get('x', config.title.position.x)
                config.title.position.y = title_data['position'].get('y', config.title.position.y)

            if 'background' in title_data:
                bg = title_data['background']
                config.title.background.enabled = bg.get('enabled', config.title.background.enabled)
                config.title.background.color = bg.get('color', config.title.background.color)
                config.title.background.opacity = bg.get('opacity', config.title.background.opacity)
                config.title.background.border_radius = bg.get('border_radius', config.title.background.border_radius)

        # Header 설정
        if 'header' in data:
            header_data = data['header']
            config.header.enabled = header_data.get('enabled', True)

            if 'main_title' in header_data:
                mt = header_data['main_title']
                config.header.main_title['text'] = mt.get('text', config.header.main_title['text'])
                config.header.main_title['font_size'] = mt.get('font_size', config.header.main_title['font_size'])
                config.header.main_title['color'] = mt.get('color', config.header.main_title['color'])
                config.header.main_title['position'] = mt.get('position', config.header.main_title['position'])
                config.header.main_title['alignment'] = mt.get('alignment', config.header.main_title['alignment'])
                config.header.main_title['stroke_width'] = mt.get('stroke_width', 0)
                config.header.main_title['stroke_color'] = mt.get('stroke_color', '#000000')

            if 'subtitle' in header_data:
                st = header_data['subtitle']
                config.header.subtitle['text'] = st.get('text', config.header.subtitle['text'])
                config.header.subtitle['font_size'] = st.get('font_size', config.header.subtitle['font_size'])
                config.header.subtitle['color'] = st.get('color', config.header.subtitle['color'])
                config.header.subtitle['position'] = st.get('position', config.header.subtitle['position'])
                config.header.subtitle['alignment'] = st.get('alignment', config.header.subtitle['alignment'])
                config.header.subtitle['stroke_width'] = st.get('stroke_width', 0)
                config.header.subtitle['stroke_color'] = st.get('stroke_color', '#000000')

        # Global 설정
        if 'global' in data:
            global_data = data['global']

            if 'background' in global_data:
                bg = global_data['background']
                config.global_settings.background['blur_strength'] = bg.get('blur_strength', 50)
                config.global_settings.background['vignette_enabled'] = bg.get('vignette_enabled', True)
                config.global_settings.background['vignette_opacity'] = bg.get('vignette_opacity', 0.3)

        # Playback 설정
        if 'playback' in data:
            config.playback.order = data['playback'].get('order', config.playback.order)
            config.playback.clip_duration = data['playback'].get('clip_duration', config.playback.clip_duration)

        return config

    def _config_to_dict(self, config: TemplateConfig) -> Dict:
        """
        dataclass → YAML dict 변환

        Args:
            config: TemplateConfig 객체

        Returns:
            YAML 저장용 dict
        """
        return {
            'name': config.name,
            'description': config.description,
            'aspect_ratio': config.aspect_ratio,
            'rail': {
                'enabled': config.rail.enabled,
                'x': config.rail.x,
                'y_start': config.rail.y_start,
                'gap': config.rail.gap,
                'alignment': config.rail.alignment,
                'font': {
                    'family': config.rail.font.family,
                    'size': config.rail.font.size,
                    'color': config.rail.font.color
                },
                'colors': config.rail.colors,
                'inactive_opacity': config.rail.inactive_opacity,
                'active_stroke': config.rail.active_stroke,
                'title_enabled': getattr(config.rail, 'title_enabled', True),
                'title_offset_x': getattr(config.rail, 'title_offset_x', 100),
                'title_font_size': getattr(config.rail, 'title_font_size', 40),
                'effects': {
                    'border_width': config.rail.effects.border_width,
                    'border_color': config.rail.effects.border_color
                }
            },
            'title': {
                'enabled': config.title.enabled,
                'font': {
                    'family': config.title.font.family,
                    'size': config.title.font.size,
                    'color': config.title.font.color
                },
                'position': {
                    'x': config.title.position.x,
                    'y': config.title.position.y,
                    'alignment': config.title.position.alignment
                },
                'background': {
                    'enabled': config.title.background.enabled,
                    'color': config.title.background.color,
                    'opacity': config.title.background.opacity,
                    'border_radius': config.title.background.border_radius,
                    'padding': list(config.title.background.padding)
                }
            },
            'header': {
                'enabled': config.header.enabled,
                'main_title': config.header.main_title,
                'subtitle': config.header.subtitle,
                'background': config.header.background
            },
            'global': {
                'resolution': config.global_settings.resolution,
                'background': config.global_settings.background,
                'safe_area': config.global_settings.safe_area,
                'clip_area': config.global_settings.clip_area
            },
            'playback': {
                'order': config.playback.order,
                'clip_duration': config.playback.clip_duration
            }
        }

    def _get_default_config(self) -> TemplateConfig:
        """기본 설정 반환"""
        return TemplateConfig()


if __name__ == "__main__":
    # 테스트
    manager = TemplateConfigManager()

    # 기본 설정 생성
    config = manager._get_default_config()
    print(f"Default config: {config.name}")

    # 설정 검증
    is_valid, error = manager.validate_config(config)
    print(f"Validation: {is_valid}, Error: {error}")

    # 템플릿 저장
    manager.save_custom_template("test_template", config)

    # 템플릿 목록
    templates = manager.list_templates()
    print(f"Available templates: {templates}")
