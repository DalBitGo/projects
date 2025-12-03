"""
Test 4: 음성 합성 TTS 테스트 (선택적)
목적: 다양한 TTS 엔진 테스트 (gTTS, pyttsx3)
"""
import os

def test_gtts():
    """gTTS (Google Text-to-Speech) 테스트"""
    print("=" * 50)
    print("Test 4-1: gTTS (Google TTS) 테스트")
    print("=" * 50)

    try:
        from gtts import gTTS
        print("✅ gTTS 설치됨")

        # 한글 음성 생성
        text = "1위, 웃긴 고양이 영상"
        tts = gTTS(text=text, lang='ko', slow=False)

        output_path = "output/test_gtts.mp3"
        os.makedirs("output", exist_ok=True)
        tts.save(output_path)

        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"✅ 음성 생성 성공: {output_path} ({size:,} bytes)")
            print(f"  - 텍스트: {text}")
            print(f"  - 언어: 한국어")
            return True
        else:
            print("❌ 음성 파일 생성 실패")
            return False

    except ImportError:
        print("⚠️  gTTS 미설치")
        print("설치: pip install gtts")
        return False
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pyttsx3():
    """pyttsx3 (오프라인 TTS) 테스트"""
    print("\n" + "=" * 50)
    print("Test 4-2: pyttsx3 (오프라인 TTS) 테스트")
    print("=" * 50)

    try:
        import pyttsx3
        print("✅ pyttsx3 설치됨")

        # TTS 엔진 초기화
        engine = pyttsx3.init()

        # 음성 속성 확인
        voices = engine.getProperty('voices')
        rate = engine.getProperty('rate')
        volume = engine.getProperty('volume')

        print(f"  - 사용 가능한 음성: {len(voices)}개")
        print(f"  - 속도: {rate}")
        print(f"  - 볼륨: {volume}")

        # 첫 번째 음성으로 설정
        if voices:
            engine.setProperty('voice', voices[0].id)
            print(f"  - 선택된 음성: {voices[0].name}")

        # 음성 생성
        text = "Number one, Funny cat video"
        output_path = "output/test_pyttsx3.mp3"

        engine.save_to_file(text, output_path)
        engine.runAndWait()

        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"✅ 음성 생성 성공: {output_path} ({size:,} bytes)")
            print(f"  - 텍스트: {text}")
            return True
        else:
            print("⚠️  음성 파일 생성 실패 (일부 환경에서는 지원 안 됨)")
            return False

    except ImportError:
        print("⚠️  pyttsx3 미설치")
        print("설치: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"⚠️  에러: {e}")
        print("  (헤드리스 환경에서는 pyttsx3가 작동하지 않을 수 있습니다)")
        return False

def test_google_cloud_tts_check():
    """Google Cloud TTS 설치 확인 (실제 생성은 안 함)"""
    print("\n" + "=" * 50)
    print("Test 4-3: Google Cloud TTS 확인")
    print("=" * 50)

    try:
        from google.cloud import texttospeech
        print("✅ Google Cloud TTS 라이브러리 설치됨")
        print("  - 실제 사용하려면 GCP 계정 및 인증 필요")
        print("  - 설정: export GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json")
        return True

    except ImportError:
        print("⚠️  Google Cloud TTS 미설치")
        print("설치: pip install google-cloud-texttospeech")
        print("  (선택적 - 고품질 음성이 필요한 경우에만)")
        return False

def test_tts_comparison():
    """생성된 TTS 파일 비교"""
    print("\n" + "=" * 50)
    print("📊 생성된 TTS 파일 비교")
    print("=" * 50)

    tts_files = [
        ("gTTS", "output/test_gtts.mp3"),
        ("pyttsx3", "output/test_pyttsx3.mp3"),
    ]

    found_any = False
    for name, path in tts_files:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {name}: {path} ({size:,} bytes)")
            found_any = True
        else:
            print(f"❌ {name}: 파일 없음")

    return found_any

def print_recommendations():
    """TTS 엔진 추천"""
    print("\n" + "=" * 50)
    print("💡 TTS 엔진 추천")
    print("=" * 50)

    recommendations = """
1. **gTTS** (추천 ⭐)
   - 장점: 무료, 설치 간단, 한국어 지원 우수
   - 단점: 인터넷 필요, 느린 속도
   - 사용: pip install gtts

2. **pyttsx3**
   - 장점: 오프라인 작동, 빠름
   - 단점: 음성 품질 낮음, 한국어 지원 제한적
   - 사용: pip install pyttsx3

3. **Google Cloud TTS**
   - 장점: 최고 품질, 다양한 음성
   - 단점: 유료 ($4/1M 글자)
   - 사용: pip install google-cloud-texttospeech

**이 프로젝트에서는 gTTS를 기본으로 사용 권장**
"""
    print(recommendations)

if __name__ == "__main__":
    print("\n🎙️  TTS (음성 합성) 테스트 시작\n")

    results = {}

    results['gtts'] = test_gtts()
    results['pyttsx3'] = test_pyttsx3()
    results['google_cloud'] = test_google_cloud_tts_check()

    test_tts_comparison()
    print_recommendations()

    print("\n" + "=" * 50)
    print("📊 테스트 결과")
    print("=" * 50)
    print(f"gTTS: {'✅ PASS' if results['gtts'] else '⚠️  미설치/실패'}")
    print(f"pyttsx3: {'✅ PASS' if results['pyttsx3'] else '⚠️  미설치/실패'}")
    print(f"Google Cloud TTS: {'✅ 설치됨' if results['google_cloud'] else '⚠️  미설치'}")

    if results['gtts'] or results['pyttsx3']:
        print("\n✅ 최소 1개 이상의 TTS 엔진 사용 가능!")
    else:
        print("\n⚠️  TTS 엔진이 설치되지 않았습니다.")
        print("gTTS 설치 권장: pip install gtts")
