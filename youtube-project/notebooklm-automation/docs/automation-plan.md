# NotebookLM YouTube 자동화 계획

## 목표

**문서 입력 → 검수만 하면 YouTube 업로드 완료**

최소한의 수동 작업으로 NotebookLM Video Overview 생성부터 YouTube 업로드까지 자동화

## 자동화 단계별 계획

### Phase 1: 수동 + 반자동 (빠른 시작)

**구현 난이도**: ⭐ 쉬움
**자동화 수준**: 50%
**예상 소요**: 1-2일

#### 워크플로우
```
1. [수동] NotebookLM에서 문서 업로드
2. [수동] Video Overview 생성 설정 & 클릭
3. [수동] MP4 다운로드
4. [자동] YouTube API로 업로드
5. [수동] 최종 검수
```

#### 구현 항목
- [ ] YouTube Data API v3 설정
- [ ] OAuth 2.0 인증 구현
- [ ] 업로드 스크립트 작성 (Node.js)
- [ ] 메타데이터 자동 생성 (제목, 설명, 태그)
- [ ] 썸네일 자동 생성 (옵션)

#### 장점
- 구현 빠름
- API 공식 지원으로 안정적
- NotebookLM 품질 확인하며 진행 가능

#### 단점
- NotebookLM 조작은 수동
- 대량 처리 어려움

---

### Phase 2: 브라우저 자동화 (권장)

**구현 난이도**: ⭐⭐⭐ 중간
**자동화 수준**: 80-90%
**예상 소요**: 3-5일

#### 워크플로우
```
1. [자동] 문서 준비 (파일 감시 or 스케줄)
2. [자동] Puppeteer로 NotebookLM 로그인
3. [자동] 노트북 생성 & 파일 업로드
4. [자동] Video Overview 생성 클릭
5. [자동] 생성 완료 대기 (polling)
6. [자동] MP4 다운로드
7. [자동] YouTube 업로드
8. [수동] 검수 & 공개 전환
```

#### 기술 스택
- **Puppeteer** or **Playwright**: 브라우저 자동화
- **Node.js**: 스크립트 실행
- **YouTube Data API**: 업로드
- **pm2** or **cron**: 스케줄링

#### 구현 상세

##### 1. NotebookLM 자동화
```javascript
// notebooklm-automation.js 의사코드

async function createVideoOverview(documentPath, options) {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  // 1. 로그인
  await page.goto('https://notebooklm.google/');
  await googleLogin(page); // OAuth 처리

  // 2. 노트북 생성
  await page.click('button:has-text("New Notebook")');

  // 3. 파일 업로드
  const fileInput = await page.$('input[type="file"]');
  await fileInput.uploadFile(documentPath);
  await page.waitForSelector('.upload-complete');

  // 4. Studio → Video Overview
  await page.click('text=Studio');
  await page.click('text=Video Overview');

  // 5. 설정
  await page.selectOption('#format', options.format); // 'explainer' or 'brief'
  await page.selectOption('#style', options.style); // 'whiteboard' etc
  await page.fill('#custom-prompt', options.prompt);

  // 6. 생성 클릭
  await page.click('button:has-text("Generate")');

  // 7. 완료 대기 (polling)
  await page.waitForSelector('.video-ready', { timeout: 600000 }); // 10분

  // 8. 다운로드
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('button:has-text("Download")')
  ]);
  const filePath = await download.path();

  await browser.close();
  return filePath;
}
```

##### 2. YouTube 업로드 통합
```javascript
// main-pipeline.js

async function automatedPipeline(documentPath, config) {
  console.log('1. NotebookLM Video 생성 중...');
  const videoPath = await createVideoOverview(documentPath, config.notebooklm);

  console.log('2. YouTube 업로드 중...');
  const videoId = await uploadToYouTube(videoPath, config.youtube);

  console.log('3. 완료! 검수 대기 중');
  console.log(`YouTube URL: https://youtube.com/watch?v=${videoId}`);
  console.log('검수 후 공개 처리하세요.');

  // 알림 전송 (Slack, Email 등)
  await sendNotification(`영상 업로드 완료: ${videoId}`);
}
```

##### 3. 스케줄링
```javascript
// schedule.js

const cron = require('node-cron');

// 매일 오전 9시 실행
cron.schedule('0 9 * * *', async () => {
  const documents = await getNewDocuments('./input/');

  for (const doc of documents) {
    await automatedPipeline(doc, config);
  }
});
```

#### 장점
- 거의 완전 자동화
- 대량 처리 가능
- 스케줄링 가능

#### 단점
- NotebookLM UI 변경 시 스크립트 수정 필요
- 헤드리스 모드에서 Google 로그인 제한 가능
- 세션 유지 관리 필요

---

### Phase 3: Enterprise API (프로덕션)

**구현 난이도**: ⭐⭐⭐⭐ 어려움
**자동화 수준**: 100%
**예상 소요**: 1주일 + Enterprise 계약

#### 전제조건
- NotebookLM Enterprise 계정 필요
- Video Overview API 지원 확인 필요 (현재 문서에 명시 안됨)
- Google Cloud 프로젝트 설정

#### 워크플로우
```
1. [자동] 문서 준비
2. [자동] NotebookLM Enterprise API로 노트북 생성
3. [자동] API로 소스 업로드
4. [자동] API로 Video Overview 생성
5. [자동] MP4 다운로드
6. [자동] YouTube 업로드
7. [자동] 검수 알림
```

#### API 예상 구조
```javascript
// 공식 API 문서 확인 필요

const { NotebookLMClient } = require('@google-cloud/notebooklm');

async function createVideoViaAPI(documentUrl) {
  const client = new NotebookLMClient();

  // 1. 노트북 생성
  const notebook = await client.createNotebook({
    parent: 'projects/my-project/locations/us',
    notebook: { displayName: 'Auto Generated' }
  });

  // 2. 소스 추가
  await client.batchCreateSources({
    parent: notebook.name,
    sources: [{ uri: documentUrl }]
  });

  // 3. Video Overview 생성 (API 지원 여부 확인 필요)
  const video = await client.generateVideoOverview({
    notebook: notebook.name,
    format: 'EXPLAINER',
    language: 'ko',
    style: 'WHITEBOARD'
  });

  return video.downloadUrl;
}
```

#### 장점
- 완전 자동화
- 안정적 (공식 API)
- 대량 처리 최적화

#### 단점
- 비용 발생 (Enterprise)
- Video Overview API 지원 여부 불확실
- 초기 설정 복잡

---

## 권장 로드맵

### Step 1: Phase 1 구현 (1-2일)
- YouTube API 연동 먼저 완성
- 수동 워크플로우로 품질 확인
- 메타데이터 최적화 패턴 찾기

### Step 2: Phase 2 POC (2-3일)
- Puppeteer로 NotebookLM 자동화 시도
- 로그인/업로드/다운로드만 자동화
- 안정성 테스트

### Step 3: Phase 2 완성 (3-5일)
- 전체 파이프라인 통합
- 에러 핸들링
- 로깅 & 모니터링

### Step 4: Phase 3 검토 (옵션)
- Enterprise API 지원 여부 확인
- 비용 대비 효과 분석
- 필요시 마이그레이션

---

## 기술적 고려사항

### 1. 인증 관리

#### Google OAuth 2.0
- NotebookLM: 브라우저 쿠키/세션
- YouTube API: OAuth 토큰
- 리프레시 토큰 저장 (.env)

```env
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REFRESH_TOKEN=xxx
YOUTUBE_CHANNEL_ID=xxx
```

### 2. 에러 핸들링

```javascript
const retry = require('async-retry');

await retry(async () => {
  return await createVideoOverview(doc);
}, {
  retries: 3,
  onRetry: (err, attempt) => {
    console.log(`Retry ${attempt}: ${err.message}`);
  }
});
```

### 3. 상태 관리

```javascript
// jobs.json
{
  "jobs": [
    {
      "id": "job-001",
      "document": "report.pdf",
      "status": "video_generating", // pending, video_generating, uploading, completed, failed
      "notebooklm_video": "/downloads/video.mp4",
      "youtube_id": null,
      "created_at": "2025-01-20T09:00:00Z"
    }
  ]
}
```

### 4. 모니터링

- 로그: Winston or Pino
- 알림: Slack Webhook
- 대시보드: 간단한 웹 UI

---

## 예상 비용

| 항목 | Phase 1 | Phase 2 | Phase 3 |
|------|---------|---------|---------|
| NotebookLM | 무료 | 무료 | Enterprise 요금 |
| YouTube API | 무료 (할당량 내) | 무료 | 무료 |
| 서버 | 로컬 | VPS $5-10/월 | Cloud $20+/월 |
| 개발 시간 | 1-2일 | 3-5일 | 1주일+ |

---

## 다음 단계

1. [ ] Phase 1 시작: YouTube API 설정
2. [ ] 테스트 문서로 수동 파이프라인 검증
3. [ ] Phase 2 POC: Puppeteer로 NotebookLM 로그인 테스트
4. [ ] 결정: Phase 2 vs Phase 3

---

## 참고 자료

### 브라우저 자동화
- [Puppeteer 문서](https://pptr.dev/)
- [Playwright 문서](https://playwright.dev/)

### YouTube API
- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [OAuth 2.0 가이드](https://developers.google.com/youtube/v3/guides/authentication)

### NotebookLM Enterprise
- [API 문서](https://cloud.google.com/agentspace/notebooklm-enterprise/docs/api-notebooks)
- [설정 가이드](https://cloud.google.com/agentspace/notebooklm-enterprise/docs/set-up-notebooklm)
