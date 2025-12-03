# 🚀 빠른 시작 가이드

이 프로젝트를 처음 보는 분을 위한 3분 요약

---

## 🎯 프로젝트 목적

**문서(PDF, PPT 등) → NotebookLM → YouTube 영상 자동 업로드**

Google NotebookLM의 Video Overview 기능으로 문서를 슬라이드 영상으로 변환하고, YouTube에 자동 업로드하는 시스템

---

## ⚡ 핵심 요약

### NotebookLM Video Overview란?

```
문서 업로드 → AI가 분석 → 슬라이드 영상 + 내레이션 생성 → MP4 다운로드
```

- **입력**: PDF, Google Docs, 슬라이드, URL, 유튜브 등
- **출력**: MP4 영상 (슬라이드 + AI 음성 내레이션)
- **언어**: 80+ 언어 지원 (한국어 포함)
- **비용**: 개인 계정 무료

### 자동화 레벨

| 방식 | 자동화 | 비용 | 난이도 |
|------|--------|------|--------|
| 완전 수동 | 0% | 무료 | 쉬움 |
| 브라우저 자동화 | 70% | 무료 | 중간 |
| YouTube API | 60% | 무료 | 중간 |
| 완전 자동 (Enterprise) | 100% | 유료 | 어려움 |

---

## 📁 프로젝트 구조

```
notebooklm-automation/
├── README.md                  # 전체 개요
├── QUICKSTART.md             # 이 파일 (빠른 시작)
├── docs/                      # 📚 문서들
│   ├── project-status.md     # ⭐ 프로젝트 현황 (여기서 시작!)
│   ├── test-checklist.md     # ⭐ 품질 테스트 체크리스트
│   ├── free-version-guide.md # 무료 버전 가이드
│   ├── api-version-guide.md  # API 버전 가이드
│   ├── notebooklm-guide.md   # NotebookLM 사용법
│   ├── automation-plan.md    # 자동화 계획
│   └── youtube-api-guide.md  # YouTube API 가이드
├── input/                     # 입력 문서 폴더
├── downloads/                 # NotebookLM 다운로드 폴더
└── test-results/              # 테스트 결과
    ├── screenshots/
    ├── videos/
    └── notes.md
```

---

## 🎬 어디서 시작?

### 1️⃣ 프로젝트 상황 파악 (5분)

👉 **[docs/project-status.md](./docs/project-status.md)** 읽기

이 문서에서:
- ✅ 완료된 것
- ❌ 아직 없는 것
- 🚨 핵심 검증 포인트
- 🎯 다음 단계 옵션

### 2️⃣ NotebookLM 품질 테스트 (1-2시간)

👉 **[docs/test-checklist.md](./docs/test-checklist.md)** 따라하기

**왜 중요한가?**
- NotebookLM이 표/이미지를 제대로 처리하는지 확인 필수
- 품질에 따라 프로젝트 방향 결정
- 테스트 없이 개발 시작하면 위험

**무엇을 테스트?**
- 간단한 표
- 복잡한 표 + 차트
- 이미지 중심 문서

**결과 활용**
- 25-30점: 프로젝트 진행 ✅
- 18-24점: 전처리 추가 필요 ⚠️
- 12-17점: 대안 검토 ⚠️⚠️
- 0-11점: 방향 전환 ❌

### 3️⃣ 가이드 선택 (필요시)

**API 키 없음 (무료로 시작)**
👉 [docs/free-version-guide.md](./docs/free-version-guide.md)
- 완전 수동 워크플로우
- Puppeteer 브라우저 자동화
- 배치 작업

**API 키 있음 (YouTube API)**
👉 [docs/api-version-guide.md](./docs/api-version-guide.md)
- YouTube Data API v3 연동
- NotebookLM Enterprise 검토
- 완전 자동화

**NotebookLM 사용법 모름**
👉 [docs/notebooklm-guide.md](./docs/notebooklm-guide.md)
- 기본 사용법
- Video Overview 설정
- 품질 최적화 팁

---

## ⚠️ 중요: 테스트부터!

```
❌ 테스트 없이 개발 시작 → 시간 낭비 위험

✅ 테스트 먼저 → 품질 확인 → 개발 시작
```

### 테스트 안하면?

- NotebookLM이 표를 제대로 못 보여줄 수 있음
- 이미지 품질이 낮을 수 있음
- 한글 처리가 이상할 수 있음
- 개발 다 하고 나서 알면 늦음

### 테스트 하면?

- 품질 확인 후 개발 시작
- 위험 요소 사전 파악
- 대안 마련 가능
- 확신 있게 진행

---

## 📊 현재 상태 (한눈에)

| 항목 | 상태 |
|------|------|
| **NotebookLM 조사** | ✅ 완료 |
| **문서 작성** | ✅ 완료 (6개 문서) |
| **자동화 전략** | ✅ 완료 (3단계 계획) |
| **품질 테스트** | ⏳ **대기 중** ⭐ |
| **설계 문서** | ❌ 미작성 |
| **코드 구현** | ❌ 미구현 |
| **프론트엔드** | ❌ 미작성 |
| **배포** | ❌ 미배포 |

---

## 🎯 즉시 해야 할 일

### 우선순위 1: 품질 테스트 ⭐⭐⭐

```bash
1. docs/test-checklist.md 열기
2. 테스트 문서 3개 준비
3. NotebookLM 테스트 실행
4. 결과 평가 (30점 만점)
5. 다음 단계 결정
```

**예상 시간**: 1-2시간
**중요도**: 🔥🔥🔥 매우 높음

### 우선순위 2: 방향 결정

테스트 결과에 따라:

```
25-30점 → 설계 문서 작성 → 개발 시작
18-24점 → 전처리 방법 연구 → 설계
12-17점 → 대안 검토 → 프로토타입
0-11점 → 프로젝트 재검토
```

### 우선순위 3: 기술 스택 결정

- 백엔드: Node.js + Express?
- 프론트엔드: React? Next.js?
- DB: PostgreSQL? MongoDB?
- 큐: Bull (Redis)?

---

## 💡 자주 묻는 질문

### Q1: NotebookLM이 뭔가요?

Google의 AI 노트 도구입니다. 문서를 업로드하면 AI가 분석해서 슬라이드 영상(Video Overview) 또는 팟캐스트(Audio Overview)를 만들어줍니다.

### Q2: 무료인가요?

네, 개인 Google 계정으로 무료 사용 가능합니다. Enterprise 버전은 유료입니다.

### Q3: 표나 이미지도 영상에 나오나요?

공식적으로는 "자동 추출"이라고 하지만, **실제 품질은 테스트 필요**합니다. 이게 바로 우선순위 1번 작업입니다.

### Q4: 완전 자동화 가능한가요?

조건부 가능합니다:
- 무료 버전: 70% 자동화 (브라우저 자동화)
- API 버전: 100% 자동화 (Enterprise 필요)

### Q5: 개발 기간은?

테스트 통과 후:
- CLI 버전: 3-5일
- 웹 버전: 3-4주

### Q6: 어떤 기술 스택 필요한가요?

- Node.js (필수)
- React (프론트엔드)
- PostgreSQL or MongoDB (DB)
- Puppeteer (브라우저 자동화)
- YouTube Data API v3

### Q7: YouTube API는 무료인가요?

네, 할당량 내에서 무료입니다 (하루 약 6개 영상).

### Q8: 지금 바로 시작할 수 있나요?

테스트부터 시작하세요! 코드 작성은 테스트 후에.

---

## 📞 다음 미팅 전 준비

### 체크리스트

- [ ] `project-status.md` 읽음
- [ ] `test-checklist.md` 읽음
- [ ] NotebookLM 품질 테스트 완료
- [ ] 테스트 결과 정리 (`test-results/notes.md`)
- [ ] 다음 단계 결정 (진행/보류/대안)
- [ ] 궁금한 점 정리

### 공유할 자료

- 테스트 결과 문서
- 생성된 영상 샘플 (2-3개)
- 스크린샷
- 종합 평가 점수

---

## 🔗 주요 링크

### 문서
- [프로젝트 현황](./docs/project-status.md) ⭐
- [테스트 체크리스트](./docs/test-checklist.md) ⭐
- [무료 버전 가이드](./docs/free-version-guide.md)
- [API 버전 가이드](./docs/api-version-guide.md)

### 외부
- [NotebookLM](https://notebooklm.google/)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [Google Cloud Console](https://console.cloud.google.com/)

---

## 🎬 요약

```
1. project-status.md 읽기 (현재 상황 파악)
2. test-checklist.md 따라 테스트 (품질 검증)
3. 결과에 따라 다음 단계 결정
4. 필요한 가이드 문서 참조
```

**현재 가장 중요한 것**: NotebookLM 품질 테스트!

---

**작성일**: 2025-01-20
**버전**: 1.0
**다음 업데이트**: 테스트 완료 후
