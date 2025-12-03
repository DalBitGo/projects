"""
Ranking Shorts Generator
Generates ranking-style shorts videos from CSV data
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List
from tqdm import tqdm
import re

from .template_engine import TemplateEngine
from .video_compositor import VideoCompositor


class RankingShortsGenerator:
    """랭킹형 쇼츠 생성기"""

    def __init__(
        self,
        style: str = "modern",
        aspect_ratio: str = "9:16"
    ):
        """
        Args:
            style: 템플릿 스타일
            aspect_ratio: 화면 비율
        """
        self.style = style
        self.aspect_ratio = aspect_ratio
        self.template_engine = TemplateEngine(style, aspect_ratio)
        self.compositor = VideoCompositor(aspect_ratio)

    def generate_from_csv(
        self,
        csv_path: str,
        output_dir: str,
        bgm_path: Optional[str] = None,
        bgm_drops: Optional[str] = None,
        enable_rail: bool = True,
        enable_intro: bool = True
    ) -> str:
        """
        CSV 파일에서 랭킹 영상 생성

        Args:
            csv_path: CSV 파일 경로
            output_dir: 출력 디렉토리
            bgm_path: BGM 파일 경로 (선택)
            bgm_drops: BGM 드롭 시간 (쉼표 구분, 예: "0,8,16,24")
            enable_rail: 좌측 레일 활성화
            enable_intro: 타이틀 인트로 활성화

        Returns:
            최종 영상 파일 경로
        """
        print(f"\n🎬 Ranking Shorts Generator")
        print(f"Style: {self.style}, Aspect: {self.aspect_ratio}")
        print(f"Input: {csv_path}\n")

        # CSV 읽기
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded {len(df)} items from CSV\n")

        # 출력 디렉토리 생성
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        max_rank = len(df)

        # 각 항목 처리
        clip_paths = []
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing items"):
            rank = int(row['rank'])
            title = str(row['title'])

            # 1. 오버레이 생성
            overlay_path = self.template_engine.create_overlay(
                rank=rank,
                title=title,
                emoji=str(row.get('emoji', '')),
                score=float(row['score']) if 'score' in row and pd.notna(row['score']) else None,
                description=str(row.get('description', '')),
                max_rank=max_rank
            )

            # 2. 레일 오버레이 생성 (선택)
            rail_path = None
            if enable_rail:
                rail_path = self.template_engine.draw_ranking_rail(max_rank, rank)

            # 3. 인트로 오버레이 생성 (선택)
            intro_path = None
            if enable_intro:
                intro_path = self.template_engine.create_title_intro_overlay(title)

            # 4. 클립 합성
            clip_output = output_path / f"clip_{rank:02d}.mp4"
            duration = float(row.get('duration', 10))

            self.compositor.compose_clip(
                clip_path=str(row['clip_path']),
                overlay_path=overlay_path,
                output_path=str(clip_output),
                duration=duration,
                rail_overlay_path=rail_path,
                intro_overlay_path=intro_path
            )

            clip_paths.append(str(clip_output))

        print(f"\n✓ Created {len(clip_paths)} clips\n")

        # 5. 클립 연결
        print("🔗 Concatenating clips...")
        concat_output = output_path / "ranking_raw.mp4"
        self.compositor.concatenate_clips(clip_paths, str(concat_output))

        # 6. BGM 추가
        if bgm_path and Path(bgm_path).exists():
            print(f"🎵 Adding BGM: {Path(bgm_path).name}...")
            final_output = output_path / "final.mp4"

            # BGM 드롭 파싱
            drop_times = None
            if bgm_drops:
                try:
                    drop_times = [float(t.strip()) for t in bgm_drops.split(',')]
                except ValueError:
                    print(f"⚠ Invalid bgm_drops format: {bgm_drops}")

            self.compositor.add_bgm(
                str(concat_output),
                bgm_path,
                str(final_output),
                drop_times=drop_times
            )
        else:
            final_output = concat_output
            if bgm_path:
                print(f"⚠ BGM file not found: {bgm_path}")

        print(f"\n✅ Done! Output: {final_output}\n")
        return str(final_output)

    def generate_from_dir(
        self,
        input_dir: str,
        output_dir: str,
        top: Optional[int] = None,
        order: str = "desc",
        title_mode: str = "local",
        titles_csv: Optional[str] = None,
        bgm_path: Optional[str] = None,
        bgm_drops: Optional[str] = None,
        enable_rail: bool = True,
        enable_intro: bool = True
    ) -> str:
        """
        폴더에서 비디오 파일을 스캔하여 랭킹 영상 생성

        Args:
            input_dir: 입력 폴더 경로
            output_dir: 출력 디렉토리
            top: 상위 N개만 사용 (None이면 전체)
            order: 순위 정렬 (desc: N→1 카운트다운, asc: 1→N)
            title_mode: 제목 생성 모드 (manual/local/ai)
            titles_csv: 제목 CSV 파일 (title_mode=manual일 때)
            bgm_path: BGM 파일 경로 (선택)
            bgm_drops: BGM 드롭 시간 (쉼표 구분)
            enable_rail: 좌측 레일 활성화
            enable_intro: 타이틀 인트로 활성화

        Returns:
            최종 영상 파일 경로
        """
        print(f"\n🎬 Ranking Shorts Generator (Folder Mode)")
        print(f"Style: {self.style}, Aspect: {self.aspect_ratio}")
        print(f"Input Dir: {input_dir}\n")

        # 비디오 파일 스캔
        video_extensions = ['*.mp4', '*.mov', '*.avi', '*.mkv']
        video_files = []
        for ext in video_extensions:
            video_files.extend(Path(input_dir).glob(ext))

        # 자연 정렬 (natural sort)
        video_files = sorted(video_files, key=lambda p: self._natural_sort_key(p.name))

        if not video_files:
            print(f"❌ No video files found in {input_dir}")
            return ""

        # Top N 필터링
        if top and top < len(video_files):
            video_files = video_files[:top]

        print(f"📊 Found {len(video_files)} video files\n")

        # 순위 할당 (desc면 N→1, asc면 1→N)
        max_rank = len(video_files)
        if order == "desc":
            ranks = list(range(max_rank, 0, -1))  # [N, N-1, ..., 2, 1]
        else:
            ranks = list(range(1, max_rank + 1))  # [1, 2, ..., N-1, N]

        # 제목 생성
        titles = self._generate_titles(video_files, title_mode, titles_csv)

        # 출력 디렉토리 생성
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 각 비디오 처리
        clip_paths = []
        for i, (video_file, rank, title) in enumerate(zip(video_files, ranks, titles)):
            print(f"Processing [{i+1}/{max_rank}]: {video_file.name} (Rank {rank})")

            # 1. 오버레이 생성
            overlay_path = self.template_engine.create_overlay(
                rank=rank,
                title=title,
                emoji="",
                score=None,
                description="",
                max_rank=max_rank
            )

            # 2. 레일 오버레이 생성
            rail_path = None
            if enable_rail:
                rail_path = self.template_engine.draw_ranking_rail(max_rank, rank)

            # 3. 인트로 오버레이 생성
            intro_path = None
            if enable_intro:
                intro_path = self.template_engine.create_title_intro_overlay(title)

            # 4. 클립 합성
            clip_output = output_path / f"clip_{rank:02d}.mp4"

            self.compositor.compose_clip(
                clip_path=str(video_file),
                overlay_path=overlay_path,
                output_path=str(clip_output),
                duration=10.0,  # 기본 10초
                rail_overlay_path=rail_path,
                intro_overlay_path=intro_path
            )

            clip_paths.append(str(clip_output))

        print(f"\n✓ Created {len(clip_paths)} clips\n")

        # 5. 클립 연결
        print("🔗 Concatenating clips...")
        concat_output = output_path / "ranking_raw.mp4"
        self.compositor.concatenate_clips(clip_paths, str(concat_output))

        # 6. BGM 추가
        if bgm_path and Path(bgm_path).exists():
            print(f"🎵 Adding BGM: {Path(bgm_path).name}...")
            final_output = output_path / "final.mp4"

            # BGM 드롭 파싱
            drop_times = None
            if bgm_drops:
                try:
                    drop_times = [float(t.strip()) for t in bgm_drops.split(',')]
                except ValueError:
                    print(f"⚠ Invalid bgm_drops format: {bgm_drops}")

            self.compositor.add_bgm(
                str(concat_output),
                bgm_path,
                str(final_output),
                drop_times=drop_times
            )
        else:
            final_output = concat_output
            if bgm_path:
                print(f"⚠ BGM file not found: {bgm_path}")

        print(f"\n✅ Done! Output: {final_output}\n")
        return str(final_output)

    def _natural_sort_key(self, text: str):
        """자연 정렬을 위한 키 생성"""
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]

    def _generate_titles(
        self,
        video_files: List[Path],
        mode: str,
        titles_csv: Optional[str] = None
    ) -> List[str]:
        """
        제목 생성

        Args:
            video_files: 비디오 파일 리스트
            mode: 제목 생성 모드 (manual/local/ai)
            titles_csv: 제목 CSV 파일 (manual 모드)

        Returns:
            제목 리스트
        """
        if mode == "manual" and titles_csv:
            # CSV에서 제목 로드
            df = pd.read_csv(titles_csv)
            if 'title' in df.columns:
                return df['title'].tolist()[:len(video_files)]
            else:
                print("⚠ 'title' column not found in titles CSV, using local mode")
                mode = "local"

        if mode == "local":
            # 파일명에서 키워드 추출 (간단 버전)
            titles = []
            for vf in video_files:
                # 확장자 제거, 언더스코어/하이픈을 공백으로
                name = vf.stem.replace('_', ' ').replace('-', ' ')
                # 숫자 제거
                name = re.sub(r'\d+', '', name).strip()
                # 10자로 제한
                if len(name) > 10:
                    name = name[:10]
                if not name:
                    name = f"영상 {len(titles)+1}"
                titles.append(name)
            return titles

        if mode == "ai":
            # AI 모드 (OpenAI GPT-4 Vision)
            try:
                from ..utils.ai_title_generator import AITitleGenerator

                print("🤖 AI 제목 생성 시작...")
                generator = AITitleGenerator()
                titles = generator.generate_titles_batch(
                    [str(vf) for vf in video_files],
                    max_length=15,
                    language="korean"
                )
                print("✅ AI 제목 생성 완료")
                return titles

            except ImportError:
                print("⚠️  AI 제목 생성기를 불러올 수 없습니다.")
                print("   src/utils/ai_title_generator.py가 있는지 확인하세요.")
                print("   local 모드로 전환합니다.")
                return self._generate_titles(video_files, "local", titles_csv)

            except ValueError as e:
                print(f"⚠️  {e}")
                print("   .env 파일에 OPENAI_API_KEY를 설정하세요.")
                print("   local 모드로 전환합니다.")
                return self._generate_titles(video_files, "local", titles_csv)

            except Exception as e:
                print(f"⚠️  AI 제목 생성 실패: {e}")
                print("   local 모드로 전환합니다.")
                return self._generate_titles(video_files, "local", titles_csv)

        # 기본값
        return [f"영상 {i+1}" for i in range(len(video_files))]

    def validate_csv(self, csv_path: str) -> bool:
        """
        CSV 파일 검증

        Args:
            csv_path: CSV 파일 경로

        Returns:
            검증 성공 여부
        """
        try:
            df = pd.read_csv(csv_path)

            # 필수 컬럼 확인
            required_columns = ['rank', 'title', 'clip_path']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                print(f"✗ Missing required columns: {missing_columns}")
                return False

            # 클립 파일 존재 확인
            missing_files = []
            for clip_path in df['clip_path']:
                if not Path(clip_path).exists():
                    missing_files.append(clip_path)

            if missing_files:
                print(f"✗ Missing clip files:")
                for f in missing_files:
                    print(f"  - {f}")
                return False

            print(f"✓ CSV validation passed")
            return True

        except Exception as e:
            print(f"✗ CSV validation error: {e}")
            return False


if __name__ == "__main__":
    # 테스트
    generator = RankingShortsGenerator("modern", "9:16")
    print("RankingShortsGenerator initialized")
