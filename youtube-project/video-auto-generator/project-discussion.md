# YouTube 자동 영상 생성기 - 프로젝트 논의 정리

## 개요
스크립트 입력 → 자동 영상 생성 → YouTube 업로드까지 자동화하는 파이프라인 구축

## 가능성 & 주의점

### ✅ 가능한 것
- 스크립트 → 장면 분해 & 키워드 추출
- 이미지/영상 검색 & 다운로드 (Pexels/Pixabay API)
- 한국어 TTS 합성
- 컷 편집/자막/전환 효과
- 인코딩 및 YouTube 업로드 자동화

### ⚠️ 주의할 점
- **GIPHY**: "Powered by GIPHY" 표기 의무, 제3자 저작물 많아 상업적 이용 시 저작권 클레임 위험 → **사용 비추천**
- **Pexels/Pixabay**: 상업적 사용 가능하지만 조건 준수 필요 (Standalone 판매 금지 등)
- **YouTube API**: 업로드 쿼터 관리 필요 (1600 유닛/업로드)

---

## 아키텍처

### V1: MVP 파이프라인

```
1. 스크립트 입력 & 장면 분해
   └─> LLM으로 문단/문장 단위 씬 분할
   └─> 각 씬: {scene_id, text, keywords, mood, duration_hint}

2. 소스 검색
   └─> Pexels/Pixabay API (사진·영상)
   └─> 9:16 (Shorts) / 16:9 필터

3. TTS 합성 (ko-KR)
   └─> Google TTS / Azure Neural TTS / Polly
   └─> 오디오 길이 = duration 기준

4. 편집 (타임라인 구성)
   └─> FFmpeg / MoviePy
   └─> Ken Burns 효과 (이미지)
   └─> Fade/Crossfade 전환
   └─> 자막 합성 (ASS/SRT)

5. 메타데이터 & 썸네일
   └─> LLM으로 제목/설명/태그 생성
   └─> 최적 프레임 캡처 + 텍스트 오버레이

6. YouTube 업로드 (선택)
   └─> YouTube Data API videos.insert
```

### V2: 품질 고도화 (추후)
- BGM 비트 맞춤 컷팅
- 키워드 하이라이트 자막
- 안전/저작권 필터
- 세로/가로 동시 산출
- 장면별 LUT/색감 자동 적용
- 다국어 TTS + 자막

---

## 기술 스택

### Backend
- **Python** (FastAPI) + Celery (비동기 작업) + Redis (큐)

### Media Processing
- **FFmpeg** + **MoviePy**

### API
- **Pexels/Pixabay SDK** (미디어 검색)
- **TTS**: Google Cloud TTS / Azure Neural TTS / Amazon Polly
- **YouTube Data API** (업로드)

### Frontend (선택)
- Next.js (업로드·미리보기·파라미터 설정)

---

## 비용 분석

### 방안 1: 클라우드 TTS 사용
```
Google Cloud TTS (Chirp 3 HD)
├─ 한국어: $16/1M 문자
├─ 10분 영상 (약 1,500자) = $0.024
└─ 월 100개 = $2.4

Pexels/Pixabay API: 무료
YouTube API: 무료 (쿼터 내)
서버: AWS/GCP ~$10-30/월

→ 총 월 $15-35
```

### 방안 2: Vrew 활용 (추천) ⭐
```
Vrew: 무료 or 유료 (~₩10,000/월)
API: 전부 무료
서버: 로컬 실행 시 $0

→ 총 월 $0-10
```

---

## Vrew 활용 아키텍처

```python
# 워크플로우

1. 스크립트 → Vrew
   └─> TTS + 자막 + 타이밍 자동 생성
   └─> Export (영상 or JSON/프로젝트 파일)

2. Python 스크립트
   ├─ Vrew 출력 파싱 (타이밍 정보 추출)
   ├─ Pexels/Pixabay에서 키워드로 B-roll 검색
   └─ FFmpeg로 조합
      ├─ Vrew 음성 트랙
      ├─ B-roll 영상 (타이밍 맞춤)
      ├─ 자막 (Vrew 재사용 or 재생성)
      └─ 전환/BGM

3. YouTube 업로드 (선택)
```

### 장점
- **TTS 비용 제로** (Vrew가 처리)
- 한국어 품질 보장
- 자막 타이밍 자동 처리
- 로컬 실행 가능

---

## 타이밍 로직 (핵심)

```python
# 각 씬별 처리
for scene in scenes:
    # TTS 오디오 길이 기준
    duration = scene.audio.duration

    # Asset 길이 조정
    if asset.type == "video":
        clip = trim(asset, min(available, duration + ε))
    else:  # image
        clip = ken_burns(asset, duration)

    # 전환 효과
    apply_fade(clip, in=4-6frames, out=4-6frames)

    # 씬 경계 crossfade
    crossfade(prev_clip, clip, 8-12frames)

    # 자막 동기화
    subtitle = sync_to_audio_waveform(scene.text, scene.audio)
```

---

## 라이선스 체크리스트

| 소스 | 상업적 이용 | 표기 의무 | 주의사항 |
|------|------------|----------|---------|
| **GIPHY** | ⚠️ 위험 | ✅ "Powered by GIPHY" | 제3자 저작물 많음, Content ID 클레임 위험 |
| **Pexels** | ✅ 가능 | 권장 | Standalone 판매 금지 |
| **Pixabay** | ✅ 가능 | 권장 | 상표/로고 콘텐츠 상업 이용 제한 |
| **YouTube** | ✅ | - | API 쿼터 관리 필요 |

---

## MVP 구현 로드맵 (2-3주)

### Week 1
- [ ] API 키 세팅 (Pexels/Pixabay/TTS/YouTube OAuth)
- [ ] 씬 분해 모듈 (키워드 추출)
- [ ] 미디어 검색/다운로드 모듈

### Week 2
- [ ] TTS 합성 (or Vrew 연동)
- [ ] 타임라인 생성 (오디오 길이 기준)
- [ ] FFmpeg/MoviePy 렌더러

### Week 3
- [ ] 자막/전환/BGM 합성
- [ ] 웹 UI or CLI
- [ ] YouTube 업로드 자동화

---

## 의사코드 (핵심)

```python
# 파이프라인
scenes = scene_segmenter(script_text)

for s in scenes:
    # 미디어 검색
    s.assets = search_stock_media(s.keywords, aspect="9:16")

    # TTS (or Vrew)
    s.voice = select_voice("ko-KR")
    s.audio = tts(s.text, voice=s.voice)  # returns path + duration

# 타임라인 구성
timeline = align_by_audio_duration(scenes)

# 렌더링
render_ffmpeg(timeline, output="video.mp4")

# 업로드
if upload_enabled:
    youtube_upload("video.mp4", title, description, tags)
```

---

## 다음 결정 사항

### 1. Vrew 출력 포맷 확인
- [ ] 영상 파일 (.mp4)?
- [ ] 프로젝트 파일 (.vrew)?
- [ ] JSON/SRT 타이밍 데이터?

### 2. 목표 명확화
- [ ] Vrew 영상 + B-roll 자동 삽입?
- [ ] Vrew는 TTS만, 영상 편집은 처음부터?

### 3. 실행 환경
- [ ] 로컬 PC (무료)
- [ ] 클라우드 서버 (자동화, 약간 비용)

### 4. MVP 범위
- **Phase 1**: CLI 도구 (스크립트 → 고정 템플릿 영상)
- **Phase 2**: 미디어 검색 (Pexels 연동)
- **Phase 3**: YouTube 자동화

---

## TTS 선택 가이드

| 서비스 | 한국어 품질 | 가격 | 특징 |
|--------|-----------|------|------|
| **Google Cloud TTS** | ⭐⭐⭐⭐⭐ | $16/1M 문자 | Chirp 3 HD, 가장 자연스러움 |
| **Azure Neural TTS** | ⭐⭐⭐⭐ | 비슷 | Google 대안 |
| **Amazon Polly** | ⭐⭐⭐ | 저렴 | 가격 경쟁력, 한국어는 약간 떨어짐 |
| **Vrew** | ⭐⭐⭐⭐ | ~₩10,000/월 | 한국 서비스, 로컬 실행 가능 |

**추천**: Vrew 활용 → 비용 절감 + 한국어 품질 보장

---

## 참고 자료
- YouTube Data API: https://developers.google.com/youtube/v3
- Pexels API: https://www.pexels.com/api/
- Pixabay API: https://pixabay.com/api/docs/
- Google Cloud TTS: https://cloud.google.com/text-to-speech
- MoviePy 문서: https://zulko.github.io/moviepy/
