"""
Video Compositor for Shorts Generation
FFmpeg wrapper for video composition
"""

import subprocess
from pathlib import Path
from typing import List, Optional


class VideoCompositor:
    """FFmpeg 기반 영상 합성기"""

    def __init__(self, aspect_ratio: str = "9:16"):
        """
        Args:
            aspect_ratio: 화면 비율 (9:16 or 16:9)
        """
        self.aspect_ratio = aspect_ratio

        if aspect_ratio == "9:16":
            self.width, self.height = 1080, 1920
            self.clip_w, self.clip_h = 900, 1600
        else:  # 16:9
            self.width, self.height = 1920, 1080
            self.clip_w, self.clip_h = 1600, 900

    def compose_clip(
        self,
        clip_path: str,
        overlay_path: str,
        output_path: str,
        duration: float = 10.0,
        rail_overlay_path: Optional[str] = None,
        intro_overlay_path: Optional[str] = None
    ) -> None:
        """
        단일 랭킹 클립 합성

        Args:
            clip_path: 원본 클립 경로
            overlay_path: 오버레이 이미지 경로
            output_path: 출력 파일 경로
            duration: 클립 길이 (초)
            rail_overlay_path: 레일 오버레이 경로 (선택)
            intro_overlay_path: 인트로 오버레이 경로 (선택)
        """
        # 출력 디렉토리 생성
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 입력 파일 리스트 구성
        inputs = ['-i', clip_path, '-i', overlay_path]
        input_idx = 2  # 다음 입력 인덱스

        if rail_overlay_path:
            inputs.extend(['-i', rail_overlay_path])
            rail_idx = input_idx
            input_idx += 1
        else:
            rail_idx = None

        if intro_overlay_path:
            inputs.extend(['-i', intro_overlay_path])
            intro_idx = input_idx
            input_idx += 1
        else:
            intro_idx = None

        # 필터 체인 구성
        filter_parts = [
            f"[0:v]scale={self.width}:{self.height}:force_original_aspect_ratio=increase,",
            f"crop={self.width}:{self.height}[scaled];",
            "[scaled]split[main][blur];",
            "[blur]gblur=sigma=50[blurred];",
            f"color=c=black@0.3:s={self.width}x{self.height}:d={duration}[vignette];",
            "[blurred][vignette]overlay=0:0[bg];",
            f"[main]scale={self.clip_w}:{self.clip_h}:force_original_aspect_ratio=decrease[resized];",
            "[bg][resized]overlay=(W-w)/2:(H-h)/2[with_clip];",
            "[with_clip][1:v]overlay=0:0[with_overlay];"
        ]

        # 레일 오버레이 추가
        if rail_idx is not None:
            filter_parts.append(f"[with_overlay][{rail_idx}:v]overlay=0:0[with_rail];")
            last_output = "with_rail"
        else:
            last_output = "with_overlay"

        # 인트로 오버레이 추가 (0~0.5초만 표시)
        if intro_idx is not None:
            filter_parts.append(f"[{last_output}][{intro_idx}:v]overlay=0:0:enable='between(t,0,0.5)'[with_intro];")
            last_output = "with_intro"

        # 페이드 효과
        filter_parts.append(f"[{last_output}]fade=t=in:st=0:d=0.5,fade=t=out:st={duration-0.3}:d=0.3")

        filter_complex = ''.join(filter_parts).replace('\n', '').replace(' ', '')

        # FFmpeg 명령어
        cmd = [
            'ffmpeg', '-y',
            *inputs,
            '-filter_complex', filter_complex,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-r', '30',
            '-an',  # 오디오 제거 (나중에 BGM 추가)
            output_path
        ]

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✓ Composed: {Path(output_path).name}")
        except subprocess.CalledProcessError as e:
            print(f"✗ FFmpeg error: {e.stderr}")
            raise

    def concatenate_clips(
        self,
        clip_list: List[str],
        output_path: str,
        transition: str = "concat"
    ) -> None:
        """
        여러 클립 연결

        Args:
            clip_list: 클립 경로 리스트
            output_path: 출력 파일 경로
            transition: 전환 타입 (concat or crossfade)
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if transition == "concat":
            # 단순 연결 (빠름)
            self._concat_simple(clip_list, output_path)
        else:
            # Crossfade 전환 (느림)
            self._concat_with_xfade(clip_list, output_path)

    def _concat_simple(self, clip_list: List[str], output_path: str):
        """단순 concat (전환 효과 없음)"""
        # concat 파일 생성
        concat_file = Path("output/concat.txt")
        with open(concat_file, 'w') as f:
            for clip in clip_list:
                f.write(f"file '{Path(clip).absolute()}'\n")

        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✓ Concatenated {len(clip_list)} clips")
        except subprocess.CalledProcessError as e:
            print(f"✗ Concatenation error")
            raise

    def _concat_with_xfade(self, clip_list: List[str], output_path: str):
        """Crossfade 전환 (간단 버전: 2개만)"""
        if len(clip_list) == 1:
            # 클립이 1개면 복사만
            subprocess.run(['cp', clip_list[0], output_path], check=True)
            return

        # TODO: 여러 클립 xfade는 복잡한 필터 체인 필요
        # 현재는 단순 concat으로 대체
        print("Warning: xfade with multiple clips not implemented, using simple concat")
        self._concat_simple(clip_list, output_path)

    def add_bgm(
        self,
        video_path: str,
        bgm_path: str,
        output_path: str,
        volume: float = 0.3,
        drop_times: Optional[List[float]] = None
    ) -> None:
        """
        BGM 추가

        Args:
            video_path: 영상 파일 경로
            bgm_path: BGM 파일 경로
            output_path: 출력 파일 경로
            volume: BGM 볼륨 (0.0 ~ 1.0)
            drop_times: BGM 드롭 시간 리스트 (초) - 페이드 경계 정렬용
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 영상 길이 가져오기
        duration_cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        result = subprocess.run(duration_cmd, capture_output=True, text=True)
        video_duration = float(result.stdout.strip())

        # 드롭 싱크 지원 (간단 버전: 페이드 타이밍만 조정)
        if drop_times and len(drop_times) > 0:
            # 첫 드롭에 맞춰 페이드인
            fade_in_start = drop_times[0] if drop_times[0] > 0 else 0
            # 마지막 드롭에서 2초 전 페이드아웃
            fade_out_start = max(video_duration - 2, drop_times[-1] if len(drop_times) > 1 else video_duration - 2)
        else:
            fade_in_start = 0
            fade_out_start = video_duration - 2

        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-stream_loop', '-1',  # BGM 무한 반복
            '-i', bgm_path,
            '-filter_complex',
            f"""
            [1:a]volume={volume},
            afade=t=in:st={fade_in_start}:d=2,
            afade=t=out:st={fade_out_start}:d=2,
            atrim=duration={video_duration}[bgm]
            """.replace('\n', '').replace(' ', ''),
            '-map', '0:v',
            '-map', '[bgm]',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✓ Added BGM: {Path(output_path).name}")
        except subprocess.CalledProcessError as e:
            print(f"✗ BGM addition error")
            raise


if __name__ == "__main__":
    # 테스트 코드
    compositor = VideoCompositor("9:16")
    print("VideoCompositor initialized")
