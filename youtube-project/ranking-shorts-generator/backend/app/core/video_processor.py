"""
Video Processing Module
Based on design doc: docs/05-video-processing.md

영상 처리 파이프라인:
1. Download → 2. Preprocess → 3. Add Ranking Text → 4. Concatenate → 5. Add Music → 6. Final Rendering
"""
import ffmpeg
import logging
import json
import uuid
from pathlib import Path
from typing import List, Optional, Callable
from moviepy.editor import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    AudioFileClip,
)

logger = logging.getLogger(__name__)


def get_video_info(video_path: str) -> dict:
    """영상 정보 추출"""
    try:
        probe = ffmpeg.probe(video_path)
        video_stream = next((s for s in probe["streams"] if s["codec_type"] == "video"), None)

        if not video_stream:
            raise ValueError("No video stream found")

        return {
            "width": int(video_stream["width"]),
            "height": int(video_stream["height"]),
            "duration": float(video_stream.get("duration", 0)),
            "fps": eval(video_stream.get("r_frame_rate", "30/1")),
        }
    except Exception as e:
        logger.error(f"Failed to get video info: {e}")
        raise


def crop_to_9_16(input_path: str, output_path: str):
    """
    영상을 9:16 비율로 크롭

    - 세로 영상 (9:16): 그대로 유지
    - 정사각형 (1:1): 좌우 크롭
    - 가로 영상 (16:9): 좌우 크롭
    """
    info = get_video_info(input_path)
    width, height = info["width"], info["height"]

    # 목표 비율
    target_ratio = 9 / 16

    # 현재 비율
    current_ratio = width / height

    if abs(current_ratio - target_ratio) < 0.01:
        # 이미 9:16
        stream = ffmpeg.input(input_path)
    else:
        # 크롭 필요
        if current_ratio > target_ratio:
            # 너무 넓음 → 좌우 크롭
            crop_width = int(height * target_ratio)
            crop_height = height
            x_offset = (width - crop_width) // 2
            y_offset = 0
        else:
            # 너무 높음 → 상하 크롭
            crop_width = width
            crop_height = int(width / target_ratio)
            x_offset = 0
            y_offset = (height - crop_height) // 2

        stream = ffmpeg.input(input_path)
        stream = ffmpeg.crop(stream, x_offset, y_offset, crop_width, crop_height)

    # 1080x1920으로 리사이즈
    stream = ffmpeg.filter(stream, "scale", 1080, 1920)

    # 출력
    stream = ffmpeg.output(stream, output_path, vcodec="libx264", crf=23, preset="medium")
    ffmpeg.run(stream, overwrite_output=True, quiet=True)

    logger.info(f"Cropped and resized video: {output_path}")


def trim_video(input_path: str, output_path: str, duration: int = 7):
    """
    영상을 지정된 길이로 트림

    Args:
        input_path: 입력 영상 경로
        output_path: 출력 영상 경로
        duration: 목표 길이 (초)
    """
    info = get_video_info(input_path)
    video_duration = info["duration"]

    if video_duration <= duration:
        # 이미 짧음 → 그대로 복사
        stream = ffmpeg.input(input_path)
    else:
        # 중간 부분 추출
        start_time = (video_duration - duration) / 2
        stream = ffmpeg.input(input_path, ss=start_time, t=duration)

    stream = ffmpeg.output(stream, output_path, vcodec="copy", acodec="copy")
    ffmpeg.run(stream, overwrite_output=True, quiet=True)

    logger.info(f"Trimmed video to {duration}s: {output_path}")


def preprocess_video(input_path: str, output_path: str, target_duration: int = 7) -> str:
    """
    영상 전처리: 크롭 + 리사이즈 + 트림

    Returns:
        str: 처리된 영상 경로
    """
    temp_cropped = output_path.replace(".mp4", "_cropped.mp4")

    # 1. 크롭 및 리사이즈
    crop_to_9_16(input_path, temp_cropped)

    # 2. 트림
    trim_video(temp_cropped, output_path, target_duration)

    # 3. 임시 파일 삭제
    Path(temp_cropped).unlink(missing_ok=True)

    return output_path


def add_ranking_text_moviepy(input_path: str, output_path: str, rank: int) -> str:
    """
    MoviePy를 사용한 랭킹 텍스트 오버레이 추가

    Args:
        input_path: 입력 영상
        output_path: 출력 영상
        rank: 랭킹 순위 (1, 2, 3, ...)

    Returns:
        str: 처리된 영상 경로
    """
    # 영상 로드
    video = VideoFileClip(input_path)

    # 랭킹 텍스트 생성
    if rank == 1:
        text = "🥇 #1"
    elif rank == 2:
        text = "🥈 #2"
    elif rank == 3:
        text = "🥉 #3"
    else:
        text = f"#{rank}"

    # 텍스트 클립 생성
    txt_clip = TextClip(
        text,
        fontsize=72,
        color="white",
        font="Arial-Bold",
        stroke_color="black",
        stroke_width=3,
        method="caption",
        size=(video.w, None),
    )

    # 위치 및 지속 시간 설정
    txt_clip = txt_clip.set_position(("center", 100)).set_duration(video.duration)

    # 페이드 인 효과 (0.5초)
    txt_clip = txt_clip.crossfadein(0.5)

    # 영상과 텍스트 합성
    final = CompositeVideoClip([video, txt_clip])

    # 저장
    final.write_videofile(
        output_path, codec="libx264", audio_codec="aac", fps=30, preset="medium", threads=4
    )

    # 메모리 정리
    video.close()
    txt_clip.close()
    final.close()

    logger.info(f"Added ranking text #{rank}: {output_path}")
    return output_path


def concatenate_videos(video_paths: list, output_path: str) -> str:
    """
    여러 영상을 순서대로 이어붙이기

    Args:
        video_paths: 영상 경로 리스트 (순서대로)
        output_path: 출력 경로

    Returns:
        str: 최종 영상 경로
    """
    clips = [VideoFileClip(path) for path in video_paths]

    # 이어붙이기
    final_clip = concatenate_videoclips(clips, method="compose")

    # 저장
    final_clip.write_videofile(
        output_path, codec="libx264", audio_codec="aac", fps=30, preset="medium", threads=4
    )

    # 메모리 정리
    for clip in clips:
        clip.close()
    final_clip.close()

    logger.info(f"Concatenated {len(video_paths)} videos: {output_path}")
    return output_path


def add_background_music(
    video_path: str, music_path: str, output_path: str, music_volume: float = 0.3
) -> str:
    """
    배경음악 추가

    Args:
        video_path: 영상 경로
        music_path: 음악 경로
        output_path: 출력 경로
        music_volume: 배경음악 볼륨 (0.0~1.0)

    Returns:
        str: 최종 영상 경로
    """
    video = VideoFileClip(video_path)
    music = AudioFileClip(music_path)

    # 음악 길이 조정
    if music.duration > video.duration:
        music = music.subclip(0, video.duration)
    else:
        # 음악이 짧으면 루프
        music = music.audio_loop(duration=video.duration)

    # 볼륨 조정
    music = music.volumex(music_volume)

    # 원본 오디오와 믹싱
    if video.audio:
        from moviepy.audio.AudioClip import CompositeAudioClip

        final_audio = CompositeAudioClip([video.audio, music])
    else:
        final_audio = music

    # 영상에 오디오 추가
    final_video = video.set_audio(final_audio)

    # 저장
    final_video.write_videofile(
        output_path, codec="libx264", audio_codec="aac", fps=30, preset="medium", threads=4
    )

    # 메모리 정리
    video.close()
    music.close()
    final_video.close()

    logger.info(f"Added background music: {output_path}")
    return output_path


def generate_thumbnail(video_path: str, thumbnail_path: str, timestamp: float = 1.0):
    """
    영상에서 썸네일 추출

    Args:
        video_path: 영상 경로
        thumbnail_path: 썸네일 저장 경로
        timestamp: 추출 시간 (초)
    """
    stream = ffmpeg.input(video_path, ss=timestamp)
    stream = ffmpeg.output(stream, thumbnail_path, vframes=1)
    ffmpeg.run(stream, overwrite_output=True, quiet=True)

    logger.info(f"Generated thumbnail: {thumbnail_path}")
    return thumbnail_path


def generate_ranking_video(
    video_urls: list,
    output_path: str,
    music_path: Optional[str] = None,
    progress_callback: Optional[Callable] = None,
) -> str:
    """
    랭킹 쇼츠 영상 생성 전체 파이프라인

    Args:
        video_urls: 영상 URL 리스트 (순서대로)
        output_path: 최종 출력 경로
        music_path: 배경음악 경로 (선택)
        progress_callback: 진행 상황 콜백 함수

    Returns:
        str: 최종 영상 경로
    """
    from app.core.downloader import download_video

    temp_dir = Path("../storage/temp") / str(uuid.uuid4())
    temp_dir.mkdir(parents=True, exist_ok=True)

    total_steps = len(video_urls) * 3 + 2  # 다운로드 + 전처리 + 텍스트 + 합치기 + 음악
    current_step = 0

    def update_progress(message: str):
        nonlocal current_step
        current_step += 1
        if progress_callback:
            progress_callback(current_step, total_steps, message)

    try:
        # 1. 다운로드
        downloaded_paths = []
        for i, url in enumerate(video_urls):
            update_progress(f"Downloading video {i+1}/{len(video_urls)}")
            path = download_video(url, str(temp_dir))
            downloaded_paths.append(path)

        # 2. 전처리 (크롭, 리사이즈, 트림)
        preprocessed_paths = []
        for i, path in enumerate(downloaded_paths):
            update_progress(f"Preprocessing video {i+1}/{len(video_urls)}")
            output = str(temp_dir / f"preprocessed_{i}.mp4")
            preprocess_video(path, output, target_duration=7)
            preprocessed_paths.append(output)

        # 3. 랭킹 텍스트 추가
        ranked_paths = []
        for i, path in enumerate(preprocessed_paths):
            update_progress(f"Adding ranking text {i+1}/{len(video_urls)}")
            output = str(temp_dir / f"ranked_{i}.mp4")
            add_ranking_text_moviepy(path, output, rank=i + 1)
            ranked_paths.append(output)

        # 4. 영상 합치기
        update_progress("Concatenating videos")
        concat_output = str(temp_dir / "concatenated.mp4")
        concatenate_videos(ranked_paths, concat_output)

        # 5. 배경음악 추가
        if music_path:
            update_progress("Adding background music")
            add_background_music(concat_output, music_path, output_path)
        else:
            # 음악 없으면 그대로 복사
            import shutil

            shutil.copy(concat_output, output_path)

        update_progress("Rendering complete!")

        logger.info(f"Generated ranking video: {output_path}")
        return output_path

    finally:
        # 임시 파일 정리
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)
