# NotebookLM YouTube 자동화 프로젝트

Google NotebookLM의 Video Overview 기능을 활용한 YouTube 영상 자동 생성/업로드 시스템

## 개요

문서(PDF, Google Docs, 슬라이드 등)를 업로드하면 NotebookLM이 자동으로 슬라이드 형태의 내레이션 영상을 생성하고, 이를 YouTube에 자동 업로드하는 파이프라인

## NotebookLM Video Overview

- 문서 → 슬라이드 영상 + AI 내레이션 자동 생성
- 80+ 언어 지원 (한국어 포함)
- MP4 다운로드 가능 (16:9 비율)
- 커스터마이징:
  - 포맷: Explainer(상세) / Brief(짧은 쇼츠)
  - 스타일: Whiteboard, Watercolor, Retro Print 등
  - 대상: 초급자/전문가
  - 언어 설정

## 🚀 빠른 시작

### API 키 없이 시작 (무료)
→ [무료 버전 가이드](./docs/free-version-guide.md) 참조

```
1. NotebookLM 웹에서 수동으로 Video Overview 생성
2. YouTube에 수동 또는 브라우저 자동화로 업로드
3. 비용: 완전 무료
4. 자동화 수준: 0-70%
```

### API 키로 자동화 (권장)
→ [API 버전 가이드](./docs/api-version-guide.md) 참조

```
1. YouTube Data API v3 사용 (무료 할당량)
2. NotebookLM Enterprise API (유료, 옵션)
3. 비용: 무료 or 일부 유료
4. 자동화 수준: 60-100%
```

## 버전 비교

| 항목 | 무료 버전 | API 버전 |
|------|----------|---------|
| **NotebookLM** | 웹 수동 or 브라우저 자동화 | Enterprise API (유료) |
| **YouTube** | 수동 or 브라우저 자동화 | Data API v3 (무료) |
| **자동화 수준** | 0-70% | 60-100% |
| **비용** | 완전 무료 | 무료 or 일부 유료 |
| **난이도** | 쉬움-중간 | 중간-어려움 |
| **추천 대상** | 소규모, 테스트 | 대량 처리, 프로덕션 |

## 프로젝트 구조

```
notebooklm-automation/
├── README.md                       # 프로젝트 개요
├── docs/                           # 📚 문서
│   ├── free-version-guide.md      # 🆓 무료 버전 가이드 (API 없음)
│   ├── api-version-guide.md       # 🔑 API 버전 가이드 (API 있음)
│   ├── notebooklm-guide.md        # NotebookLM 사용법
│   ├── automation-plan.md         # 자동화 상세 계획
│   └── youtube-api-guide.md       # YouTube API 가이드
├── src/                            # 소스 코드
│   ├── free/                      # 무료 버전 스크립트
│   │   ├── notebooklm-automation.js
│   │   ├── youtube-upload.js
│   │   └── main.js
│   └── api/                       # API 버전 스크립트
│       ├── auth.js
│       ├── youtube-upload.js
│       ├── notebooklm-api.js
│       └── main.js
├── config/                         # 설정 파일
│   ├── credentials.json           # YouTube OAuth (수동 다운로드)
│   └── token.json                 # 액세스 토큰 (자동 생성)
├── input/                          # 입력 문서
├── downloads/                      # NotebookLM 다운로드 영상
└── package.json
```

## 📖 문서 가이드

### 어디서 시작해야 할까요?

#### API 키 없음 (무료)
1. [무료 버전 가이드](./docs/free-version-guide.md) - **여기서 시작** ⭐
2. [NotebookLM 사용법](./docs/notebooklm-guide.md)

#### API 키 있음 (YouTube API)
1. [API 버전 가이드](./docs/api-version-guide.md) - **여기서 시작** ⭐
2. [YouTube API 가이드](./docs/youtube-api-guide.md)

#### 상세 계획 확인
- [자동화 계획](./docs/automation-plan.md) - 3단계 자동화 전략

## 요구사항

### 공통
- Node.js 18+
- Google 계정 (NotebookLM 접근용)
- YouTube 채널

### 무료 버전
- Puppeteer (브라우저 자동화 시)

### API 버전
- YouTube Data API v3 (무료)
- NotebookLM Enterprise (유료, 옵션)

## 설치

```bash
# 프로젝트 클론
cd youtube-project/notebooklm-automation

# 패키지 설치
npm install

# 무료 버전 실행
node src/free/main.js

# API 버전 실행
node src/api/main.js
```

## 주의사항

### NotebookLM Enterprise Video API
현재(2025년 1월) NotebookLM Enterprise API 문서에는:
- ✅ Audio Overview API 지원 명시
- ❓ **Video Overview API 지원 여부 확인 필요**

Video Overview를 프로그래밍으로 생성하려면 Google Cloud 영업팀에 문의 필요

### YouTube API 할당량
- 기본: 10,000 units/day
- 영상 업로드: 1,600 units
- **하루 최대 약 6개 영상**

## 라이선스

MIT

## 참고 자료

### NotebookLM
- [공식 사이트](https://notebooklm.google/)
- [헬프센터](https://support.google.com/notebooklm)
- [Enterprise API](https://cloud.google.com/agentspace/notebooklm-enterprise/docs/api-notebooks)

### YouTube
- [Data API v3](https://developers.google.com/youtube/v3)
- [OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)

### Google Cloud
- [Cloud Console](https://console.cloud.google.com/)
- [영업 문의](https://cloud.google.com/contact)
