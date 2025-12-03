"""
AI 제목 생성기
- OpenAI GPT-4 Vision을 사용하여 비디오 프레임에서 제목 생성
"""

import os
import base64
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class AITitleGenerator:
    """AI 기반 제목 생성기"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: OpenAI API 키 (None이면 환경변수에서 로드)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables or .env file")

    def generate_title_from_video(
        self,
        video_path: str,
        max_length: int = 10,
        language: str = "korean"
    ) -> str:
        """
        비디오 파일에서 AI 제목 생성

        Args:
            video_path: 비디오 파일 경로
            max_length: 최대 제목 길이
            language: 언어 (korean, english)

        Returns:
            생성된 제목
        """
        # 1. 비디오에서 중간 프레임 추출
        frame_path = self._extract_middle_frame(video_path)

        if not frame_path:
            return f"영상 {Path(video_path).stem}"

        try:
            # 2. AI로 제목 생성
            title = self._generate_title_from_image(frame_path, max_length, language)
            return title
        finally:
            # 3. 임시 프레임 삭제
            if os.path.exists(frame_path):
                os.remove(frame_path)

    def generate_titles_batch(
        self,
        video_paths: List[str],
        max_length: int = 10,
        language: str = "korean"
    ) -> List[str]:
        """
        여러 비디오에서 일괄 제목 생성

        Args:
            video_paths: 비디오 파일 경로 리스트
            max_length: 최대 제목 길이
            language: 언어

        Returns:
            생성된 제목 리스트
        """
        titles = []
        for i, video_path in enumerate(video_paths, 1):
            print(f"  [{i}/{len(video_paths)}] AI 제목 생성 중: {Path(video_path).name}")
            try:
                title = self.generate_title_from_video(video_path, max_length, language)
                titles.append(title)
                print(f"    → {title}")
            except Exception as e:
                print(f"    ⚠️  실패: {e}, 기본 제목 사용")
                titles.append(f"영상 {i}")

        return titles

    def _extract_middle_frame(self, video_path: str) -> Optional[str]:
        """
        비디오 중간 프레임 추출

        Args:
            video_path: 비디오 파일 경로

        Returns:
            추출된 프레임 이미지 경로
        """
        # 비디오 길이 확인
        duration_cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]

        try:
            result = subprocess.run(duration_cmd, capture_output=True, text=True)
            duration = float(result.stdout.strip())
            middle_time = duration / 2
        except Exception:
            middle_time = 1.0  # 기본 1초

        # 중간 프레임 추출
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        frame_path = temp_file.name
        temp_file.close()

        extract_cmd = [
            'ffmpeg', '-y',
            '-ss', str(middle_time),
            '-i', video_path,
            '-vframes', '1',
            '-q:v', '2',
            frame_path
        ]

        result = subprocess.run(extract_cmd, capture_output=True)

        if result.returncode == 0 and os.path.exists(frame_path):
            return frame_path
        else:
            return None

    def _generate_title_from_image(
        self,
        image_path: str,
        max_length: int,
        language: str
    ) -> str:
        """
        이미지에서 AI 제목 생성

        Args:
            image_path: 이미지 파일 경로
            max_length: 최대 제목 길이
            language: 언어

        Returns:
            생성된 제목
        """
        try:
            import openai
        except ImportError:
            raise ImportError("openai 패키지가 설치되지 않았습니다. pip install openai를 실행하세요.")

        # 이미지를 base64로 인코딩
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # OpenAI API 호출
        client = openai.OpenAI(api_key=self.api_key)

        lang_instruction = {
            "korean": f"한국어로 {max_length}자 이내의 짧고 임팩트 있는 제목을 만들어주세요.",
            "english": f"Create a short and catchy title in English (max {max_length} characters)."
        }

        prompt = f"""
이 이미지는 쇼츠 영상의 한 장면입니다.
{lang_instruction.get(language, lang_instruction['korean'])}

규칙:
- 제목만 출력하세요 (설명이나 다른 텍스트 없이)
- 이모지 사용 금지
- 간결하고 임팩트 있게
- {max_length}자 이하
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # 또는 "gpt-4o"
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=50,
                temperature=0.7
            )

            title = response.choices[0].message.content.strip()

            # 따옴표 제거
            title = title.strip('"\'')

            # 길이 제한
            if len(title) > max_length:
                title = title[:max_length]

            return title

        except Exception as e:
            print(f"⚠️  OpenAI API 오류: {e}")
            raise


# 폴백: 로컬 AI 모델 (미구현)
class LocalAITitleGenerator:
    """로컬 AI 모델 기반 제목 생성기 (미구현)"""

    def __init__(self):
        """향후 BLIP, CLIP 등 로컬 모델 지원"""
        raise NotImplementedError("Local AI title generation is not implemented yet")


if __name__ == "__main__":
    # 테스트
    print("AI Title Generator Test")

    # API 키 체크
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set in environment")
        print("   .env 파일에 OPENAI_API_KEY=your-key-here 를 추가하세요")
    else:
        print(f"✅ OpenAI API Key found: {api_key[:8]}...")

        # 테스트 비디오가 있다면
        test_video = "downloads/user_clips/clip_1.mp4"
        if os.path.exists(test_video):
            generator = AITitleGenerator()
            title = generator.generate_title_from_video(test_video, max_length=15, language="korean")
            print(f"\n생성된 제목: {title}")
