"""
Template Engine for Shorts Video Generation
Handles overlay creation with Pillow
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
import yaml
import sys

# TemplateConfig import
sys.path.append(str(Path(__file__).parent.parent))
from core.template_config import TemplateConfig, TemplateConfigManager


class TemplateEngine:
    """템플릿 기반 그래픽 생성 엔진"""

    def __init__(
        self,
        style: Optional[str] = "modern",
        aspect_ratio: str = "9:16",
        config: Optional[TemplateConfig] = None
    ):
        """
        Args:
            style: 템플릿 스타일 (modern, neon, minimal) - config 없을 때 사용
            aspect_ratio: 화면 비율 (9:16 or 16:9)
            config: TemplateConfig 객체 (제공시 style 무시)
        """
        self.aspect_ratio = aspect_ratio

        # Config 설정
        if config:
            # 직접 제공된 config 사용
            self.template_config = config
            self.style = config.name
        else:
            # style에서 로드 (기존 방식 호환)
            self.style = style
            manager = TemplateConfigManager()
            try:
                self.template_config = manager.load_template(style)
            except Exception as e:
                print(f"⚠️ Failed to load template config: {e}")
                self.template_config = manager._get_default_config()

        # 레거시 config (하위 호환성)
        self.config = self._convert_to_legacy_config()

        # 캔버스 크기 설정
        if aspect_ratio == "9:16":
            self.canvas_size = (1080, 1920)
        else:
            self.canvas_size = (1920, 1080)

    def _convert_to_legacy_config(self) -> Dict:
        """
        TemplateConfig → 레거시 dict 변환 (하위 호환성)
        """
        tc = self.template_config

        return {
            'colors': {
                'gold': tc.rail.colors.get('rank_1', '#FFD700'),
                'silver': tc.rail.colors.get('rank_2', '#C0C0C0'),
                'bronze': tc.rail.colors.get('rank_3', '#CD7F32'),
                'primary': tc.rail.colors.get('default', '#667eea'),
                'text': tc.title.font.color
            },
            'fonts': {
                'bold': tc.title.font.family,
                'regular': tc.title.font.family
            },
            'layout': {
                'badge_position': [tc.rail.x, tc.rail.y_start - 100],
                'emoji_position': [920, 80],
                'score_position': [tc.rail.x, tc.rail.y_start - 50],
                'title_position': [tc.title.position.x, tc.title.position.y]
            },
            'sizes': {
                'badge_diameter': 120,
                'emoji_size': 100,
                'title_font_size': tc.title.font.size,
                'description_font_size': int(tc.title.font.size * 0.7),
                'score_font_size': 40
            },
            'rail': {
                'x': tc.rail.x,
                'gap': tc.rail.gap,
                'font_size': tc.rail.font.size,
                'inactive_opacity': tc.rail.inactive_opacity,
                'active_stroke': tc.rail.active_stroke
            },
            'title_intro': {
                'offset_y': 50
            }
        }

    def _load_config(self, style: str) -> Dict:
        """템플릿 설정 로드"""
        config_path = Path(f"templates/ranking/{style}/config.yaml")
        if not config_path.exists():
            raise FileNotFoundError(f"Template config not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def create_overlay(
        self,
        rank: int,
        title: str,
        emoji: str = "",
        score: Optional[float] = None,
        description: str = "",
        max_rank: Optional[int] = None
    ) -> str:
        """
        오버레이 이미지 생성

        Args:
            rank: 순위
            title: 제목
            emoji: 이모지 (선택)
            score: 점수 (선택)
            description: 설명 (선택)
            max_rank: 전체 순위 개수 (레일 렌더링용)

        Returns:
            오버레이 파일 경로
        """
        # 투명 캔버스 생성
        canvas = Image.new('RGBA', self.canvas_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        # 1. 순위 뱃지
        badge = self._create_badge(rank)
        badge_pos = tuple(self.config['layout']['badge_position'])
        canvas.paste(badge, badge_pos, badge)

        # 2. 이모지
        if emoji:
            try:
                emoji_img = self._render_emoji(emoji)
                emoji_pos = tuple(self.config['layout']['emoji_position'])
                canvas.paste(emoji_img, emoji_pos, emoji_img)
            except Exception as e:
                print(f"Warning: Failed to render emoji: {e}")

        # 3. 점수
        if score is not None:
            self._draw_score(draw, score)

        # 4. 제목 & 설명
        title_box = self._create_title_box(title, description)
        title_y = self.config['layout']['title_position'][1]
        canvas.paste(title_box, (0, title_y), title_box)

        # 저장
        output_dir = Path("output/overlays")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"overlay_{rank:02d}.png"
        canvas.save(output_path)

        return str(output_path)

    def draw_ranking_rail(
        self,
        max_rank: int,
        active_rank: int,
        titles: Optional[Dict[int, str]] = None
    ) -> str:
        """
        좌측 숫자 레일 생성 (1~max_rank, active_rank만 하이라이트)

        Args:
            max_rank: 전체 순위 개수
            active_rank: 활성화할 순위
            titles: 순위별 제목 딕셔너리 {1: "제목1", 2: "제목2", ...}

        Returns:
            레일 오버레이 파일 경로
        """
        canvas = Image.new('RGBA', self.canvas_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        # 헤더 렌더링 (있으면)
        if self.template_config.header.enabled:
            self._draw_header(draw)

        # Rail 설정 (TemplateConfig에서 가져오기)
        rail_cfg = self.template_config.rail
        x = rail_cfg.x
        gap = rail_cfg.gap
        font_size = rail_cfg.font.size
        inactive_opacity = int(rail_cfg.inactive_opacity * 255)
        active_stroke = rail_cfg.active_stroke

        try:
            font_number = ImageFont.truetype(rail_cfg.font.family, font_size)
        except Exception:
            font_number = ImageFont.load_default()

        # 제목 폰트 (숫자보다 작게)
        try:
            title_font_size = getattr(rail_cfg, 'title_font_size', int(font_size * 0.8))
            font_title = ImageFont.truetype(rail_cfg.font.family, title_font_size)
        except Exception:
            font_title = ImageFont.load_default()

        # 숫자 렌더링
        start_y = rail_cfg.y_start
        for i in range(1, max_rank + 1):
            y = start_y + (i - 1) * gap
            number_text = str(i)

            # 순위별 색상 가져오기
            if i == 1:
                rank_color = rail_cfg.colors.get('rank_1', '#FFD700')
            elif i == 2:
                rank_color = rail_cfg.colors.get('rank_2', '#C0C0C0')
            elif i == 3:
                rank_color = rail_cfg.colors.get('rank_3', '#CD7F32')
            else:
                rank_color = rail_cfg.colors.get('default', '#667eea')

            # Hex → RGBA 변환
            rank_rgba = self._hex_to_rgba(rank_color)

            if i == active_rank:
                # 활성: 불투명, 외곽선
                color = rank_rgba
                # 외곽선 효과 (간단 구현)
                for dx in range(-active_stroke, active_stroke + 1):
                    for dy in range(-active_stroke, active_stroke + 1):
                        if dx*dx + dy*dy <= active_stroke*active_stroke:
                            draw.text((x + dx, y + dy), number_text, font=font_number, fill=(100, 100, 255, 200))
                draw.text((x, y), number_text, font=font_number, fill=color)
            else:
                # 비활성: 반투명
                color = (*rank_rgba[:3], inactive_opacity)
                draw.text((x, y), number_text, font=font_number, fill=color)

            # 제목 렌더링 (있으면)
            if titles and i in titles and getattr(rail_cfg, 'title_enabled', True):
                title_text = titles[i]
                title_offset_x = getattr(rail_cfg, 'title_offset_x', 100)
                title_x = x + title_offset_x

                if i == active_rank:
                    # 활성: 불투명
                    title_color = rank_rgba
                else:
                    # 비활성: 반투명
                    title_color = (*rank_rgba[:3], inactive_opacity)

                draw.text((title_x, y), title_text, font=font_title, fill=title_color)

        # 저장
        output_dir = Path("output/overlays")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"rail_{active_rank:02d}.png"
        canvas.save(output_path)

        return str(output_path)

    def _hex_to_rgba(self, hex_color: str) -> Tuple[int, int, int, int]:
        """
        Hex 색상을 RGBA 튜플로 변환

        Args:
            hex_color: #RRGGBB or #RRGGBBAA

        Returns:
            (R, G, B, A) 튜플
        """
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return (r, g, b, 255)
        elif len(hex_color) == 8:
            r, g, b, a = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), int(hex_color[6:8], 16)
            return (r, g, b, a)
        else:
            return (255, 255, 255, 255)  # 기본값

    def _draw_header(self, draw: ImageDraw.ImageDraw):
        """
        상단 헤더 렌더링 (메인 제목 + 부제목)

        Args:
            draw: ImageDraw 객체
        """
        header_cfg = self.template_config.header

        # 메인 제목
        main_title = header_cfg.main_title
        try:
            font_main = ImageFont.truetype(
                self.template_config.title.font.family,
                main_title['font_size']
            )
        except Exception:
            font_main = ImageFont.load_default()

        main_color = self._hex_to_rgba(main_title['color'])
        main_x = main_title['position'][0]
        main_y = main_title['position'][1]

        # 정렬 anchor 계산
        alignment = main_title.get('alignment', 'center')
        if alignment == 'left':
            anchor = "lt"  # left-top
        elif alignment == 'right':
            anchor = "rt"  # right-top
        else:
            anchor = "mt"  # middle-top

        # 외곽선 그리기 (있으면)
        stroke_width = main_title.get('stroke_width', 0)
        if stroke_width > 0:
            stroke_color = self._hex_to_rgba(main_title.get('stroke_color', '#000000'))
            draw.text(
                (main_x, main_y),
                main_title['text'],
                font=font_main,
                fill=main_color,
                anchor=anchor,
                stroke_width=stroke_width,
                stroke_fill=stroke_color
            )
        else:
            draw.text(
                (main_x, main_y),
                main_title['text'],
                font=font_main,
                fill=main_color,
                anchor=anchor
            )

        # 부제목
        subtitle = header_cfg.subtitle
        try:
            font_sub = ImageFont.truetype(
                self.template_config.title.font.family,
                subtitle['font_size']
            )
        except Exception:
            font_sub = ImageFont.load_default()

        sub_color = self._hex_to_rgba(subtitle['color'])
        sub_x = subtitle['position'][0]
        sub_y = subtitle['position'][1]

        # 정렬 anchor 계산
        sub_alignment = subtitle.get('alignment', 'center')
        if sub_alignment == 'left':
            sub_anchor = "lt"
        elif sub_alignment == 'right':
            sub_anchor = "rt"
        else:
            sub_anchor = "mt"

        # 외곽선 그리기 (있으면)
        sub_stroke_width = subtitle.get('stroke_width', 0)
        if sub_stroke_width > 0:
            sub_stroke_color = self._hex_to_rgba(subtitle.get('stroke_color', '#000000'))
            draw.text(
                (sub_x, sub_y),
                subtitle['text'],
                font=font_sub,
                fill=sub_color,
                anchor=sub_anchor,
                stroke_width=sub_stroke_width,
                stroke_fill=sub_stroke_color
            )
        else:
            draw.text(
                (sub_x, sub_y),
                subtitle['text'],
                font=font_sub,
                fill=sub_color,
                anchor=sub_anchor
            )

    def create_title_intro_overlay(self, title: str) -> str:
        """
        타이틀 인트로 오버레이 생성 (0~0.5초 동안만 표시)

        Args:
            title: 제목 텍스트

        Returns:
            인트로 오버레이 파일 경로
        """
        canvas = Image.new('RGBA', self.canvas_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        # Title intro 설정 (config.yaml에서 가져오기, 없으면 기본값)
        intro_config = self.config.get('title_intro', {})
        offset_y = intro_config.get('offset_y', 50)

        try:
            font = ImageFont.truetype(
                self.config['fonts']['bold'],
                self.config['sizes']['title_font_size']
            )
        except Exception:
            font = ImageFont.load_default()

        # 중앙 상단에 타이틀 표시
        center_x = self.canvas_size[0] // 2
        y = 100 + offset_y

        # 반투명 배경 박스
        bbox = draw.textbbox((0, 0), title, font=font)
        text_w = bbox[2] - bbox[0]
        padding = 60
        box_coords = [
            (center_x - text_w // 2 - padding, y - 20),
            (center_x + text_w // 2 + padding, y + 80)
        ]
        draw.rounded_rectangle(box_coords, radius=30, fill=(0, 0, 0, 200))

        # 타이틀 텍스트
        draw.text((center_x, y), title, font=font, fill=(255, 255, 255), anchor="mt")

        # 저장
        output_dir = Path("output/overlays")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "title_intro.png"
        canvas.save(output_path)

        return str(output_path)

    def _create_badge(self, rank: int) -> Image.Image:
        """순위 뱃지 생성 (금/은/동/일반)"""
        colors = self.config['colors']

        # 순위별 색상
        if rank == 1:
            color = colors['gold']
        elif rank == 2:
            color = colors['silver']
        elif rank == 3:
            color = colors['bronze']
        else:
            color = colors['primary']

        size = self.config['sizes']['badge_diameter']
        badge = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(badge)

        # 원형 배경
        draw.ellipse([0, 0, size, size], fill=color)

        # 순위 숫자
        try:
            font_path = self.config['fonts']['bold']
            font = ImageFont.truetype(font_path, 60)
        except Exception:
            # 폰트 로드 실패 시 기본 폰트 사용
            font = ImageFont.load_default()

        text = str(rank)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_pos = ((size - text_w) // 2, (size - text_h) // 2)

        draw.text(text_pos, text, font=font, fill=(255, 255, 255))

        return badge

    def _render_emoji(self, emoji: str) -> Image.Image:
        """이모지 렌더링"""
        emoji_size = self.config['sizes']['emoji_size']
        emoji_img = Image.new('RGBA', (emoji_size, emoji_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(emoji_img)

        try:
            # 이모지 폰트가 있으면 사용
            font_path = self.config['fonts'].get('emoji')
            if font_path and Path(font_path).exists():
                font = ImageFont.truetype(font_path, emoji_size)
                draw.text((0, 0), emoji, font=font, embedded_color=True)
            else:
                # 폰트 없으면 텍스트로 렌더링 (일부 시스템에서 동작)
                font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), emoji, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                draw.text(((emoji_size - text_w) // 2, (emoji_size - text_h) // 2),
                         emoji, font=font, fill=(255, 255, 255))
        except Exception as e:
            print(f"Emoji rendering error: {e}")

        return emoji_img

    def _draw_score(self, draw: ImageDraw.ImageDraw, score: float):
        """점수 표시"""
        score_pos = tuple(self.config['layout']['score_position'])
        score_text = f"⭐ {score:.1f} / 10"

        try:
            font_path = self.config['fonts']['regular']
            font = ImageFont.truetype(font_path, self.config['sizes']['score_font_size'])
        except Exception:
            font = ImageFont.load_default()

        draw.text(score_pos, score_text,
                 font=font, fill=self.config['colors']['text'])

    def _create_title_box(self, title: str, description: str) -> Image.Image:
        """제목 + 설명 박스 생성"""
        box_height = 200
        box = Image.new('RGBA', (self.canvas_size[0], box_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(box)

        try:
            font_title = ImageFont.truetype(
                self.config['fonts']['bold'],
                self.config['sizes']['title_font_size']
            )
            font_desc = ImageFont.truetype(
                self.config['fonts']['regular'],
                self.config['sizes']['description_font_size']
            )
        except Exception:
            font_title = ImageFont.load_default()
            font_desc = ImageFont.load_default()

        # 제목 크기 계산
        bbox = draw.textbbox((0, 0), title, font=font_title)
        title_w = bbox[2] - bbox[0]

        # 반투명 박스
        padding = 40
        center_x = self.canvas_size[0] // 2
        box_coords = [
            (center_x - title_w // 2 - padding, 20),
            (center_x + title_w // 2 + padding, 120)
        ]
        draw.rounded_rectangle(box_coords, radius=20, fill=(0, 0, 0, 180))

        # 제목 텍스트
        draw.text((center_x, 30), title,
                 font=font_title, fill=(255, 255, 255), anchor="mt")

        # 설명 (있으면)
        if description:
            draw.text((center_x, 90), description,
                     font=font_desc, fill=(200, 200, 200), anchor="mt")

        return box


if __name__ == "__main__":
    # 테스트
    engine = TemplateEngine("modern", "9:16")
    overlay = engine.create_overlay(
        rank=1,
        title="웃긴 고양이",
        emoji="😹",
        score=9.8,
        description="빵 터지는 순간"
    )
    print(f"Created overlay: {overlay}")
