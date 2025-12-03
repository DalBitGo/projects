# 무료 버전 가이드 (API 키 없음)

API 키 없이 완전 무료로 사용하는 방법

## 대상

- NotebookLM 무료 버전 사용자 (개인 Google 계정)
- YouTube API 키 없음
- 비용 지출 없이 시작하고 싶은 경우

## 가능한 자동화 수준

### ❌ 불가능한 것
- NotebookLM API 호출 (Enterprise 전용)
- YouTube 프로그래밍 업로드 (API 필요)
- 완전 자동화 파이프라인

### ✅ 가능한 것
- NotebookLM 웹에서 Video Overview 생성
- 브라우저 자동화로 반자동화 (Puppeteer)
- YouTube 수동 업로드
- 배치 작업 (여러 영상 한번에 준비)

---

## 워크플로우 1: 완전 수동 (가장 간단)

**자동화 수준**: 0%
**비용**: 무료
**소요 시간**: 영상당 10-15분

### 단계

```
1. [수동] 문서 준비 (PDF, Docs 등)
   ↓
2. [수동] NotebookLM 접속
   ↓
3. [수동] 노트북 생성 & 문서 업로드
   ↓
4. [수동] Studio → Video Overview 생성
   ↓
5. [수동] 설정 (포맷, 스타일, 언어)
   ↓
6. [수동] Generate 클릭 & 대기 (3-5분)
   ↓
7. [수동] MP4 다운로드
   ↓
8. [수동] YouTube 업로드
   ↓
9. [수동] 메타데이터 입력 (제목, 설명, 태그)
   ↓
10. [수동] 공개 설정 & 게시
```

### 장점
- 설정 불필요
- 즉시 시작 가능
- 각 단계 품질 확인 용이

### 단점
- 시간 소요
- 반복 작업 지루함
- 대량 처리 어려움

### 추천 대상
- 영상 1-5개만 만들 때
- NotebookLM 품질 테스트
- 자동화 구축 전 검증

---

## 워크플로우 2: 반자동화 (브라우저 자동화)

**자동화 수준**: 70%
**비용**: 무료 (개발 시간만 소요)
**소요 시간**: 초기 설정 3-5일, 이후 영상당 5분

### 개요

Puppeteer로 브라우저를 제어해서 NotebookLM과 YouTube 조작을 자동화

```
1. [자동] 문서 폴더 감시
   ↓
2. [자동] Puppeteer로 NotebookLM 로그인
   ↓
3. [자동] 노트북 생성 & 문서 업로드
   ↓
4. [자동] Video Overview 생성 클릭
   ↓
5. [자동] 생성 완료 대기
   ↓
6. [자동] MP4 다운로드
   ↓
7. [자동] Puppeteer로 YouTube 로그인
   ↓
8. [자동] 영상 업로드 & 메타데이터 입력
   ↓
9. [수동] 최종 검수 & 공개 처리
```

### 필요 기술
- Node.js 기본 지식
- Puppeteer 사용 경험 (없어도 학습 가능)
- 간단한 프로그래밍

### 구현 가이드

#### 1. 환경 설정

```bash
cd notebooklm-automation
npm init -y
npm install puppeteer puppeteer-extra puppeteer-extra-plugin-stealth
```

#### 2. NotebookLM 자동화 스크립트

```javascript
// src/free/notebooklm-automation.js

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

async function createVideoOverview(documentPath, options = {}) {
  const browser = await puppeteer.launch({
    headless: false, // 브라우저 보이게 (Google 로그인 때문)
    defaultViewport: null,
  });

  try {
    const page = await browser.newPage();

    // 1. NotebookLM 접속
    console.log('NotebookLM 접속 중...');
    await page.goto('https://notebooklm.google/');

    // 2. 로그인 대기 (수동 로그인 필요)
    console.log('⚠️  Google 로그인을 수동으로 완료해주세요!');
    await page.waitForSelector('text=New Notebook', { timeout: 300000 }); // 5분 대기

    // 3. 새 노트북 생성
    console.log('노트북 생성 중...');
    await page.click('text=New Notebook');
    await page.waitForTimeout(2000);

    // 4. 파일 업로드
    console.log('파일 업로드 중...');
    const fileInput = await page.$('input[type="file"]');
    await fileInput.uploadFile(documentPath);
    await page.waitForTimeout(5000); // 업로드 대기

    // 5. Studio 탭으로 이동
    console.log('Studio 탭으로 이동...');
    await page.click('text=Studio');
    await page.waitForTimeout(2000);

    // 6. Video Overview 클릭
    console.log('Video Overview 생성 시작...');
    await page.click('text=Video Overview');
    await page.waitForTimeout(2000);

    // 7. 설정 (옵션)
    if (options.format) {
      await page.selectOption('#format-select', options.format); // 'explainer' or 'brief'
    }
    if (options.style) {
      await page.selectOption('#style-select', options.style);
    }
    if (options.language) {
      await page.click('text=Settings');
      await page.selectOption('#language-select', options.language);
    }

    // 8. Generate 클릭
    console.log('Generate 클릭...');
    await page.click('button:has-text("Generate")');

    // 9. 생성 완료 대기 (최대 10분)
    console.log('생성 완료 대기 중... (최대 10분)');
    await page.waitForSelector('.video-ready, text=Download', { timeout: 600000 });

    // 10. 다운로드
    console.log('다운로드 중...');
    const downloadPath = `./downloads/${Date.now()}.mp4`;
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button:has-text("Download")'),
    ]);
    const path = await download.path();
    await download.saveAs(downloadPath);

    console.log('✅ 완료! 저장 위치:', downloadPath);
    return downloadPath;

  } catch (error) {
    console.error('❌ 에러 발생:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

module.exports = { createVideoOverview };
```

#### 3. YouTube 업로드 자동화 (수동 로그인)

```javascript
// src/free/youtube-upload.js

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

async function uploadToYouTube(videoPath, metadata) {
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: null,
  });

  try {
    const page = await browser.newPage();

    // 1. YouTube Studio 접속
    console.log('YouTube Studio 접속 중...');
    await page.goto('https://studio.youtube.com');

    // 2. 로그인 대기
    console.log('⚠️  Google 로그인을 수동으로 완료해주세요!');
    await page.waitForSelector('#create-icon', { timeout: 300000 });

    // 3. 업로드 버튼 클릭
    console.log('업로드 시작...');
    await page.click('#create-icon');
    await page.click('text=Upload videos');

    // 4. 파일 선택
    const fileInput = await page.$('input[type="file"]');
    await fileInput.uploadFile(videoPath);
    await page.waitForTimeout(3000);

    // 5. 메타데이터 입력
    console.log('메타데이터 입력 중...');

    // 제목
    const titleInput = await page.$('#textbox[placeholder*="title"]');
    await titleInput.click({ clickCount: 3 }); // 전체 선택
    await titleInput.type(metadata.title);

    // 설명
    const descInput = await page.$('#textbox[placeholder*="description"]');
    await descInput.click();
    await descInput.type(metadata.description);

    // 6. 썸네일 업로드 (옵션)
    if (metadata.thumbnailPath) {
      const thumbInput = await page.$('#file-loader');
      await thumbInput.uploadFile(metadata.thumbnailPath);
      await page.waitForTimeout(2000);
    }

    // 7. "어린이용 아니요" 선택
    await page.click('#audience input[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]');

    // 8. 다음 버튼들 클릭
    await page.click('button:has-text("Next")'); // 1단계 완료
    await page.waitForTimeout(1000);
    await page.click('button:has-text("Next")'); // 2단계 완료
    await page.waitForTimeout(1000);
    await page.click('button:has-text("Next")'); // 3단계 완료
    await page.waitForTimeout(1000);

    // 9. 공개 설정 (비공개로 설정)
    await page.click('input[name="PRIVATE"]');

    // 10. 게시 클릭
    await page.click('button:has-text("Publish")');
    await page.waitForTimeout(5000);

    // 11. 영상 URL 가져오기
    const videoUrl = await page.$eval('.video-url-container a', (el) => el.href);

    console.log('✅ 업로드 완료!');
    console.log('URL:', videoUrl);

    return { videoUrl };

  } catch (error) {
    console.error('❌ 업로드 실패:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

module.exports = { uploadToYouTube };
```

#### 4. 메인 스크립트

```javascript
// src/free/main.js

const path = require('path');
const { createVideoOverview } = require('./notebooklm-automation');
const { uploadToYouTube } = require('./youtube-upload');

async function processDocument(documentPath, metadata) {
  console.log('=== 자동화 파이프라인 시작 ===\n');

  try {
    // 1. NotebookLM Video Overview 생성
    console.log('1️⃣ NotebookLM Video Overview 생성 중...');
    const videoPath = await createVideoOverview(documentPath, {
      format: 'explainer',
      style: 'whiteboard',
      language: 'ko',
    });

    console.log('\n✅ Video Overview 생성 완료!\n');

    // 2. YouTube 업로드
    console.log('2️⃣ YouTube 업로드 중...');
    const result = await uploadToYouTube(videoPath, metadata);

    console.log('\n✅ 모든 작업 완료!');
    console.log('YouTube URL:', result.videoUrl);
    console.log('\n⚠️  YouTube Studio에서 검수 후 공개 처리하세요.');

  } catch (error) {
    console.error('\n❌ 에러 발생:', error);
  }
}

// 사용 예시
const documentPath = path.join(__dirname, '../../input/report.pdf');
const metadata = {
  title: '2024 부동산 시장 분석 - AI 자동 생성',
  description: `
📊 2024년 부동산 시장 주요 지표 분석

주요 내용:
- 전년 대비 거래량 변동
- 가격 추이 분석
- 향후 전망

🤖 Google NotebookLM으로 자동 생성
  `.trim(),
  thumbnailPath: path.join(__dirname, '../../input/thumbnail.jpg'), // 옵션
};

processDocument(documentPath, metadata);
```

#### 5. 실행

```bash
node src/free/main.js
```

### 주의사항

#### Google 로그인
- 헤드리스 모드에서 Google 로그인 어려움
- **수동 로그인 필요** (브라우저 창에서 직접 로그인)
- 로그인 후 쿠키 저장해서 재사용 가능

#### 세션 유지
```javascript
// 쿠키 저장
const cookies = await page.cookies();
await fs.writeFile('./config/cookies.json', JSON.stringify(cookies));

// 쿠키 로드
const cookies = JSON.parse(await fs.readFile('./config/cookies.json'));
await page.setCookie(...cookies);
```

#### UI 변경 대응
- NotebookLM/YouTube UI가 변경되면 셀렉터 수정 필요
- 정기적으로 스크립트 업데이트 필요

---

## 워크플로우 3: 배치 작업 (반자동)

**자동화 수준**: 50%
**비용**: 무료
**소요 시간**: 초기 설정 1일

### 개념

여러 문서를 한번에 준비해서 NotebookLM에서 순차적으로 처리

```bash
# 폴더 구조
input/
  ├── video1/
  │   ├── document.pdf
  │   ├── config.json        # 메타데이터
  │   └── thumbnail.jpg
  ├── video2/
  │   ├── document.pdf
  │   ├── config.json
  │   └── thumbnail.jpg
  └── video3/
      ├── document.pdf
      ├── config.json
      └── thumbnail.jpg
```

### config.json 예시

```json
{
  "notebooklm": {
    "format": "explainer",
    "style": "whiteboard",
    "language": "ko",
    "prompt": "표 중심으로 설명, 90초 이내"
  },
  "youtube": {
    "title": "2024 부동산 시장 분석",
    "description": "...",
    "tags": ["부동산", "시장분석"],
    "privacyStatus": "private"
  }
}
```

### 배치 스크립트

```javascript
// src/free/batch-process.js

const fs = require('fs');
const path = require('path');
const { createVideoOverview } = require('./notebooklm-automation');
const { uploadToYouTube } = require('./youtube-upload');

async function batchProcess(inputFolder) {
  const folders = fs.readdirSync(inputFolder);

  for (const folder of folders) {
    const folderPath = path.join(inputFolder, folder);
    const configPath = path.join(folderPath, 'config.json');
    const documentPath = path.join(folderPath, 'document.pdf');

    if (!fs.existsSync(configPath)) {
      console.log(`⚠️  ${folder}: config.json 없음, 건너뜀`);
      continue;
    }

    const config = JSON.parse(fs.readFileSync(configPath));

    console.log(`\n=== ${folder} 처리 시작 ===`);

    try {
      // 1. Video Overview 생성
      const videoPath = await createVideoOverview(documentPath, config.notebooklm);

      // 2. YouTube 업로드
      const result = await uploadToYouTube(videoPath, config.youtube);

      console.log(`✅ ${folder} 완료: ${result.videoUrl}`);

      // 완료 표시
      fs.writeFileSync(
        path.join(folderPath, 'completed.txt'),
        `Completed at: ${new Date().toISOString()}\nURL: ${result.videoUrl}`
      );

    } catch (error) {
      console.error(`❌ ${folder} 실패:`, error.message);

      // 에러 로그
      fs.writeFileSync(
        path.join(folderPath, 'error.txt'),
        `Error: ${error.message}\nTime: ${new Date().toISOString()}`
      );
    }

    // 다음 영상 전 대기 (5초)
    await new Promise((resolve) => setTimeout(resolve, 5000));
  }

  console.log('\n=== 배치 작업 완료 ===');
}

batchProcess('./input');
```

---

## 비용 분석

### 완전 무료

| 항목 | 비용 |
|------|------|
| NotebookLM | 무료 |
| YouTube 업로드 | 무료 |
| 브라우저 자동화 | 무료 (오픈소스) |
| 서버 | 로컬 PC (무료) |
| **합계** | **0원** |

### 시간 투자

| 워크플로우 | 초기 설정 | 영상당 소요 |
|-----------|----------|------------|
| 완전 수동 | 0시간 | 10-15분 |
| 반자동화 | 3-5일 | 5분 |
| 배치 작업 | 1일 | 3분 |

---

## 한계와 대안

### 한계

1. **로그인 수동 필요**
   - Google 보안 정책으로 완전 자동 로그인 어려움

2. **UI 변경 취약**
   - NotebookLM/YouTube UI 변경 시 스크립트 수정 필요

3. **에러 핸들링 복잡**
   - 브라우저 자동화 특성상 예외 상황 많음

4. **대량 처리 한계**
   - NotebookLM 생성 속도 제한
   - YouTube 업로드 시간

### 대안

#### 1. 세션 쿠키 재사용
- 한번 로그인 후 쿠키 저장
- 다음 실행 시 쿠키로 자동 로그인
- 주기적으로 재인증 필요

#### 2. 헤드리스 모드
- 로그인만 수동, 이후 헤드리스로 전환
- 서버에서 백그라운드 실행 가능

#### 3. API 버전 업그레이드
- 일정 규모 이상이면 API 버전 고려
- YouTube API: 무료 (할당량 제한)
- NotebookLM Enterprise: 유료

---

## 추천 시작 방법

### 단계별 접근

```
1주차: 완전 수동으로 10개 영상 제작
  → NotebookLM 품질 확인
  → 최적 설정 찾기

2주차: 브라우저 자동화 POC
  → Puppeteer 학습
  → NotebookLM 로그인/업로드만 자동화

3주차: 전체 파이프라인 통합
  → YouTube 업로드 추가
  → 에러 핸들링

4주차: 배치 작업 구축
  → 여러 영상 자동 처리
  → 스케줄링 추가
```

### 체크리스트

- [ ] NotebookLM 계정 생성
- [ ] YouTube 채널 생성
- [ ] Node.js 설치
- [ ] Puppeteer 설치
- [ ] 테스트 문서 준비
- [ ] 수동으로 1개 영상 제작 (품질 확인)
- [ ] 브라우저 자동화 시도
- [ ] 전체 파이프라인 테스트
- [ ] 에러 핸들링 추가
- [ ] 배치 작업 구축

---

## 다음 단계

무료 버전으로 시작해서 규모가 커지면:

1. **YouTube API 추가** (무료)
   - 업로드 자동화 더 안정적
   - 메타데이터 관리 편리

2. **NotebookLM Enterprise** (유료)
   - API로 완전 자동화
   - 대량 처리 최적화

자세한 내용은 [API 버전 가이드](./api-version-guide.md) 참조
