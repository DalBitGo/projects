# Blender 중심 고퀄리티 쇼츠 제작 워크플로우

## 목표
- **퀄리티 우선**: 전문가 수준의 3D 애니메이션
- **독창성**: 나만의 캐릭터/스타일
- **효율성**: 반복 작업만 자동화

## 핵심 전략

> AI는 **아이디어와 반복 작업**만 담당
> Blender로 **실제 퀄리티 제작**
> 자동화는 **시간 아끼는 부분만**

---

## 전체 워크플로우

```
[AI] 아이디어/스크립트 생성
    ↓
[사람] Blender 씬 구성 및 애니메이션 (핵심!)
    ↓
[자동] Blender Python API로 반복 작업 자동화
    ↓
[자동] 렌더링
    ↓
[자동] 후반 작업 (음성, 자막, 편집)
    ↓
[사람] 최종 검수
```

---

## 1단계: AI로 아이디어 & 기획

### AI가 도와주는 것
- **주제 브레인스토밍**
  ```
  "건강/과학 관련 흥미로운 쇼츠 주제 10개 추천해줘"
  ```

- **스크립트 초안**
  ```
  씬1: 캐릭터가 라면 먹기 시작
  씬2: 나트륨 분자가 몸에 쌓이는 비주얼
  씬3: 혈관이 좁아지는 모습
  씬4: 결과 및 교훈
  ```

- **비주얼 레퍼런스 생성**
  - Midjourney로 스타일 참고용 이미지
  - 색감, 구도, 분위기 레퍼런스

**소요시간: 5-10분**

---

## 2단계: Blender 제작 (핵심!)

### 초기 설정 (1회만)

#### A. 캐릭터 제작/구매
**옵션 1: 직접 제작**
- 시간: 3-7일
- 퀄리티: 최고
- 독창성: 100%

**옵션 2: 에셋 구매**
- 사이트: Sketchfab, TurboSquid, Blender Market
- 비용: $10-50/캐릭터
- 시간: 30분 (리깅 조정)
- 독창성: 커스터마이징 필요

**옵션 3: AI 생성 → Blender 변환**
- Meshy.ai, Rodin로 3D 모델 생성
- Blender로 import 후 리깅
- 시간: 2-3일
- 독창성: 중상

**추천: 옵션 3 (AI + 수동 조정)**
```
AI로 기본 모델 생성 → Blender에서 디테일 추가
→ 나만의 스타일로 커스터마이징
```

#### B. 씬/배경 템플릿 구축
- 자주 쓰는 배경 3-5개 미리 제작
  - 실내
  - 실외
  - 병원/과학실
  - 추상적 공간

**소요시간: 3-5일 (1회)**

#### C. 애니메이션 라이브러리
- 기본 동작들 미리 만들어두기
  - 걷기
  - 먹기
  - 놀라기
  - 생각하기
- Blender NLA (Non-Linear Animation)로 재사용

**소요시간: 5-7일 (1회)**

### 영상별 제작 (매번)

#### 1. 씬 구성 (30-60분)
- 스크립트 기반으로 씬 레이아웃
- 카메라 앵글 설정
- 조명 배치
- 소품 배치

**자동화 가능 부분:**
```python
# Blender Python API
import bpy

# 템플릿 씬 자동 로드
def load_scene_template(scene_type):
    if scene_type == "indoor":
        bpy.ops.wm.append(filename="indoor_template.blend")
    # 카메라 자동 배치
    # 조명 자동 설정
```

#### 2. 캐릭터 애니메이션 (1-2시간)
- 기본 동작 라이브러리에서 가져오기
- 타이밍 조정
- 표정 애니메이션 (Shape Keys)
- 립싱크 (음성에 맞춰)

**부분 자동화:**
```python
# 음성 파일 → 립싱크 자동 생성
# Rhubarb Lip Sync 활용
def auto_lipsync(audio_file, character):
    # 음성 분석
    # 입모양 자동 매핑
    # Blender Shape Keys 자동 키프레임
```

#### 3. 이펙트 & 디테일 (30-60분)
- 파티클 효과
- 물리 시뮬레이션
- 특수 효과
- 카메라 무빙 세밀 조정

**소요시간: 2-4시간/영상**

---

## 3단계: 자동화로 시간 절약

### Blender Python API 자동화

#### A. 반복 작업 자동화
```python
import bpy

# 1. 씬 템플릿 자동 로드
def setup_scene(scene_type, camera_preset):
    load_template(scene_type)
    setup_camera(camera_preset)
    setup_lighting()

# 2. 캐릭터 자동 배치
def place_character(character, position, rotation):
    bpy.data.objects[character].location = position
    bpy.data.objects[character].rotation_euler = rotation

# 3. 애니메이션 자동 적용
def apply_animation_preset(character, animation_name, start_frame):
    # NLA 스트립 자동 추가
    action = bpy.data.actions[animation_name]
    nla_track = character.animation_data.nla_tracks.new()
    nla_track.strips.new(action.name, start_frame, action)

# 4. 렌더링 설정 자동화
def setup_render(output_path, resolution=(1080, 1920)):
    scene = bpy.context.scene
    scene.render.filepath = output_path
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.image_settings.file_format = 'FFMPEG'
```

#### B. AI 스크립트 → Blender 자동 변환
```python
# GPT-4가 생성한 스크립트를 파싱
script = """
Scene 1 (0-5s): Character eating ramen, happy expression
Scene 2 (5-10s): Sodium molecules entering body, worried expression
Scene 3 (10-15s): Blood vessels narrowing, shocked expression
"""

def parse_and_setup(script):
    scenes = parse_script(script)

    for i, scene in enumerate(scenes):
        # 씬 자동 생성
        create_scene(i)

        # 캐릭터 표정 자동 설정
        set_expression(scene.emotion)

        # 카메라 자동 배치
        auto_camera(scene.focus)

        # 타임라인 자동 설정
        set_timeline(scene.start, scene.end)
```

#### C. 립싱크 자동화
```python
# ElevenLabs 음성 → Blender 립싱크
def auto_lipsync_pipeline(text, character):
    # 1. AI 음성 생성
    audio = generate_voice(text)

    # 2. 음소 분석 (Rhubarb)
    phonemes = analyze_audio(audio)

    # 3. Blender Shape Keys 자동 키프레임
    for phoneme in phonemes:
        set_mouth_shape(character, phoneme.shape, phoneme.time)
```

#### D. 렌더링 자동화
```python
# 여러 씬 배치 렌더링
def batch_render(scenes):
    for scene in scenes:
        bpy.context.scene.frame_start = scene.start_frame
        bpy.context.scene.frame_end = scene.end_frame
        bpy.ops.render.render(animation=True)
```

### 외부 도구 연동

#### 1. AI → Blender 파이프라인
```python
# main.py
from openai import OpenAI
import subprocess

# 1. AI 스크립트 생성
script = generate_script_with_gpt("라면만 먹으면?")

# 2. Blender 스크립트 생성
blender_script = convert_to_blender_commands(script)

# 3. Blender 백그라운드 실행
subprocess.run([
    "blender",
    "--background",
    "template.blend",
    "--python", blender_script,
    "--render-output", "./output/",
    "--render-anim"
])
```

---

## 4단계: 렌더링 (자동)

### 렌더링 설정
- **해상도**: 1080x1920 (세로)
- **FPS**: 30
- **렌더 엔진**:
  - Eevee (빠름, 실시간) - 1-5분
  - Cycles (고퀄, 느림) - 30분-2시간

### 최적화
```python
# GPU 렌더링 활성화
bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
bpy.context.scene.cycles.device = 'GPU'

# 샘플 수 조정 (퀄리티 vs 속도)
bpy.context.scene.cycles.samples = 128  # 기본값, 낮추면 빠름
```

**소요시간:**
- Eevee: 2-5분
- Cycles: 30분-1시간

---

## 5단계: 후반 작업 (자동화)

### 자동화 스크립트
```python
# post_production.py

# 1. 음성 생성 (AI)
voice = generate_voice_elevenlabs(script)

# 2. 자막 생성
subtitles = generate_subtitles(script)

# 3. FFmpeg로 합성
ffmpeg -i render.mp4 -i voice.mp3 -i subtitles.srt \
  -c:v copy -c:a aac \
  -vf "subtitles=subtitles.srt:force_style='FontSize=24'" \
  output.mp4
```

**소요시간: 1-2분**

---

## 독창성 확보 방법

### 1. 캐릭터 디자인
- **Zack D Films 스타일 분석**
  - 단순화된 형태
  - 과장된 표정
  - 명확한 실루엣

- **나만의 스타일 만들기**
  - 색감 차별화
  - 독특한 캐릭터 특징 (예: 큰 눈, 특이한 머리 모양)
  - 일관된 디자인 언어

### 2. 비주얼 스타일
- **참고할 수 있는 스타일:**
  - Kurzgesagt (평면적, 미니멀)
  - TED-Ed (일러스트 느낌)
  - Zack D Films (3D 만화)

- **Blender로 구현:**
  - Shader 커스터마이징
  - 툰 쉐이딩 (Toon Shader)
  - 독특한 아웃라인

### 3. 스토리텔링
- AI가 제안한 스크립트를 **무조건 수정**
- 나만의 유머, 톤 추가
- 독특한 시각화 방법

---

## 최종 제작 시간 (Blender 중심)

### 초기 설정 (1회)
- 캐릭터: 3-7일
- 템플릿 씬: 3-5일
- 애니메이션 라이브러리: 5-7일
- **총: 2-3주 (한 번만!)**

### 영상 1개 제작
```
아이디어/스크립트 (AI):        10분
씬 구성 (Blender):            30-60분
애니메이션 (Blender):          1-2시간
이펙트 (Blender):             30-60분
렌더링 (자동):                30-60분
후반작업 (자동):              5분
최종 검수:                    10분
──────────────────────────────────
총: 3-5시간/영상
```

### 자동화로 절약되는 시간
- 씬 템플릿 로드: 10분 절약
- 립싱크 자동화: 20-30분 절약
- 렌더링 설정: 5분 절약
- 후반작업: 30분 절약
- **총 1시간 이상 절약**

**자동화 전: 5-6시간**
**자동화 후: 3-4시간**

---

## 추천 제작 흐름

### 주 1회 제작 (고퀄리티)
- 월요일: 아이디어 5개 (AI 도움)
- 화요일: 스크립트 작성 및 씬 구성
- 수-목: 애니메이션 제작 (2개)
- 금요일: 렌더링 및 후반작업
- **주당 2-3개 고퀄리티 쇼츠**

### 일부만 Blender, 나머지는 AI
- 메인 시리즈: Blender (주 1-2개)
- 서브 컨텐츠: AI 자동화 (주 5-10개)
- **퀄리티 + 양 모두 확보**

---

## 필요한 도구 & 비용

### 소프트웨어
- **Blender**: 무료 (오픈소스)
- **Python**: 무료
- **FFmpeg**: 무료

### API/서비스
- OpenAI API: $10-20/월
- ElevenLabs: $5/월 (Starter)
- Meshy.ai (선택): $20/월

### 하드웨어
- **최소**: GTX 1060, 16GB RAM
- **권장**: RTX 3060, 32GB RAM
- **이상적**: RTX 4070, 64GB RAM

### 에셋 (선택)
- 캐릭터 모델: $10-50
- 배경/소품: $5-30
- **총: $0-100 (1회)**

---

## 자동화 우선순위

### 반드시 자동화할 것 ⭐⭐⭐
1. 렌더링 설정
2. 후반 작업 (음성, 자막 합성)
3. 립싱크 생성
4. 배치 렌더링

### 자동화하면 좋은 것 ⭐⭐
1. 씬 템플릿 로드
2. 기본 애니메이션 적용
3. 카메라 프리셋
4. 조명 설정

### 자동화 안 할 것 (직접 해야 함) ⭐
1. 캐릭터 애니메이션 디테일
2. 표정 연기
3. 카메라 워크 세밀 조정
4. 창의적인 연출

---

## 결론

### 이 방식의 장점
✅ **전문가급 퀄리티**
✅ **완전한 독창성**
✅ **지속 가능한 워크플로우**
✅ **자동화로 효율성 확보**
✅ **확장 가능 (팀 작업 시)**

### 예상 타임라인
- **1개월**: 기본 시스템 구축
- **2개월**: 첫 10개 영상 제작
- **3개월**: 안정적 주간 생산
- **6개월**: 최적화된 워크플로우

### 성공 포인트
1. **초기 2-3주 투자** (캐릭터/템플릿)
2. **자동화 스크립트 구축** (1주)
3. **꾸준한 제작** (주 2-3개)
4. **피드백 반영** 및 개선

이게 **진짜 현실적이고 지속 가능한** 방법!
