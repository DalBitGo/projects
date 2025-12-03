# YouTube Data API v3 사용 가이드

## 1. API 설정

### Google Cloud Console 설정

#### 1단계: 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. "새 프로젝트" 클릭
3. 프로젝트 이름: `youtube-automation`
4. 생성 클릭

#### 2단계: YouTube Data API v3 활성화
1. API 및 서비스 → 라이브러리
2. "YouTube Data API v3" 검색
3. "사용 설정" 클릭

#### 3단계: OAuth 2.0 클라이언트 ID 생성
1. API 및 서비스 → 사용자 인증 정보
2. "사용자 인증 정보 만들기" → "OAuth 클라이언트 ID"
3. 애플리케이션 유형: "데스크톱 앱" 또는 "웹 애플리케이션"
4. 이름: `youtube-uploader`
5. 만들기 → JSON 다운로드

#### 4단계: OAuth 동의 화면 설정
1. OAuth 동의 화면 → 외부 선택
2. 앱 이름, 이메일 등 입력
3. 범위 추가:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube`
4. 테스트 사용자에 본인 이메일 추가

### API 할당량
- **기본 할당량**: 10,000 units/day
- 영상 업로드: 1,600 units
- **하루 최대 약 6개 영상 업로드 가능**
- 할당량 증가 신청 가능

---

## 2. Node.js 설정

### 패키지 설치

```bash
npm init -y
npm install googleapis @google-cloud/local-auth
```

### 프로젝트 구조

```
notebooklm-automation/
├── config/
│   ├── credentials.json      # OAuth 클라이언트 ID
│   └── token.json            # 생성된 액세스 토큰 (자동 생성)
├── src/
│   ├── auth.js               # 인증 처리
│   ├── youtube-upload.js     # 업로드 스크립트
│   └── index.js              # 메인 실행 파일
├── videos/                   # 업로드할 영상 폴더
├── .env                      # 환경 변수
└── package.json
```

---

## 3. 인증 구현

### auth.js

```javascript
const fs = require('fs').promises;
const path = require('path');
const { authenticate } = require('@google-cloud/local-auth');
const { google } = require('googleapis');

const SCOPES = ['https://www.googleapis.com/auth/youtube.upload'];
const TOKEN_PATH = path.join(__dirname, '../config/token.json');
const CREDENTIALS_PATH = path.join(__dirname, '../config/credentials.json');

/**
 * OAuth 2.0 인증
 */
async function authorize() {
  let client = await loadSavedCredentialsIfExist();
  if (client) {
    return client;
  }
  client = await authenticate({
    scopes: SCOPES,
    keyfilePath: CREDENTIALS_PATH,
  });
  if (client.credentials) {
    await saveCredentials(client);
  }
  return client;
}

/**
 * 저장된 토큰 로드
 */
async function loadSavedCredentialsIfExist() {
  try {
    const content = await fs.readFile(TOKEN_PATH);
    const credentials = JSON.parse(content);
    return google.auth.fromJSON(credentials);
  } catch (err) {
    return null;
  }
}

/**
 * 토큰 저장
 */
async function saveCredentials(client) {
  const content = await fs.readFile(CREDENTIALS_PATH);
  const keys = JSON.parse(content);
  const key = keys.installed || keys.web;
  const payload = JSON.stringify({
    type: 'authorized_user',
    client_id: key.client_id,
    client_secret: key.client_secret,
    refresh_token: client.credentials.refresh_token,
  });
  await fs.writeFile(TOKEN_PATH, payload);
}

module.exports = { authorize };
```

---

## 4. 영상 업로드 구현

### youtube-upload.js

```javascript
const fs = require('fs');
const { google } = require('googleapis');
const { authorize } = require('./auth');

/**
 * YouTube 영상 업로드
 * @param {string} videoPath - 업로드할 영상 파일 경로
 * @param {object} metadata - 영상 메타데이터
 */
async function uploadVideo(videoPath, metadata) {
  const auth = await authorize();
  const youtube = google.youtube({ version: 'v3', auth });

  const videoMetadata = {
    snippet: {
      title: metadata.title,
      description: metadata.description,
      tags: metadata.tags || [],
      categoryId: metadata.categoryId || '22', // 22 = People & Blogs
      defaultLanguage: 'ko',
      defaultAudioLanguage: 'ko',
    },
    status: {
      privacyStatus: metadata.privacyStatus || 'private', // 'public', 'unlisted', 'private'
      selfDeclaredMadeForKids: false,
    },
  };

  const media = {
    body: fs.createReadStream(videoPath),
  };

  try {
    console.log('업로드 시작:', metadata.title);

    const response = await youtube.videos.insert({
      part: 'snippet,status',
      requestBody: videoMetadata,
      media: media,
    });

    const videoId = response.data.id;
    const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;

    console.log('업로드 완료!');
    console.log('Video ID:', videoId);
    console.log('URL:', videoUrl);

    return {
      videoId,
      videoUrl,
      response: response.data,
    };
  } catch (error) {
    console.error('업로드 실패:', error.message);
    throw error;
  }
}

/**
 * 썸네일 업로드
 * @param {string} videoId - YouTube 영상 ID
 * @param {string} thumbnailPath - 썸네일 이미지 경로
 */
async function uploadThumbnail(videoId, thumbnailPath) {
  const auth = await authorize();
  const youtube = google.youtube({ version: 'v3', auth });

  const media = {
    mimeType: 'image/jpeg',
    body: fs.createReadStream(thumbnailPath),
  };

  try {
    const response = await youtube.thumbnails.set({
      videoId: videoId,
      media: media,
    });

    console.log('썸네일 업로드 완료');
    return response.data;
  } catch (error) {
    console.error('썸네일 업로드 실패:', error.message);
    throw error;
  }
}

/**
 * 영상 상태 업데이트 (공개 설정 변경)
 * @param {string} videoId - YouTube 영상 ID
 * @param {string} privacyStatus - 'public', 'unlisted', 'private'
 */
async function updateVideoStatus(videoId, privacyStatus) {
  const auth = await authorize();
  const youtube = google.youtube({ version: 'v3', auth });

  try {
    const response = await youtube.videos.update({
      part: 'status',
      requestBody: {
        id: videoId,
        status: {
          privacyStatus: privacyStatus,
        },
      },
    });

    console.log(`영상 공개 설정 변경: ${privacyStatus}`);
    return response.data;
  } catch (error) {
    console.error('상태 업데이트 실패:', error.message);
    throw error;
  }
}

module.exports = {
  uploadVideo,
  uploadThumbnail,
  updateVideoStatus,
};
```

---

## 5. 사용 예시

### index.js

```javascript
const path = require('path');
const { uploadVideo, uploadThumbnail } = require('./youtube-upload');

async function main() {
  const videoPath = path.join(__dirname, '../videos/my-video.mp4');
  const thumbnailPath = path.join(__dirname, '../videos/thumbnail.jpg');

  const metadata = {
    title: '2024 부동산 시장 분석 - NotebookLM 자동 생성',
    description: `
2024년 부동산 시장 주요 지표 분석

📊 주요 내용:
- 전년 대비 거래량 -32.7% 감소
- 평균 가격 변동 추이
- 지역별 상세 분석

🤖 이 영상은 Google NotebookLM으로 자동 생성되었습니다.

📁 원본 자료: [링크 또는 출처]

#부동산 #시장분석 #NotebookLM #AI생성콘텐츠
    `.trim(),
    tags: [
      '부동산',
      '시장분석',
      'NotebookLM',
      'AI',
      '자동생성',
      '데이터분석',
    ],
    categoryId: '22', // People & Blogs
    privacyStatus: 'private', // 검수 후 수동으로 공개
  };

  try {
    // 1. 영상 업로드
    const result = await uploadVideo(videoPath, metadata);
    console.log('업로드 완료:', result.videoUrl);

    // 2. 썸네일 업로드 (옵션)
    if (thumbnailPath) {
      await uploadThumbnail(result.videoId, thumbnailPath);
    }

    // 3. 검수 후 공개 처리
    // await updateVideoStatus(result.videoId, 'public');
  } catch (error) {
    console.error('에러:', error);
  }
}

main();
```

### 실행

```bash
node src/index.js
```

---

## 6. 고급 기능

### 재생목록에 추가

```javascript
async function addToPlaylist(videoId, playlistId) {
  const auth = await authorize();
  const youtube = google.youtube({ version: 'v3', auth });

  const response = await youtube.playlistItems.insert({
    part: 'snippet',
    requestBody: {
      snippet: {
        playlistId: playlistId,
        resourceId: {
          kind: 'youtube#video',
          videoId: videoId,
        },
      },
    },
  });

  return response.data;
}
```

### 업로드 진행률 표시

```javascript
const cliProgress = require('cli-progress');

async function uploadWithProgress(videoPath, metadata) {
  const fileSize = fs.statSync(videoPath).size;
  const progressBar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);
  progressBar.start(100, 0);

  // 스트림에 진행률 추적 추가
  const stream = fs.createReadStream(videoPath);
  let uploaded = 0;

  stream.on('data', (chunk) => {
    uploaded += chunk.length;
    const progress = Math.floor((uploaded / fileSize) * 100);
    progressBar.update(progress);
  });

  // ... 업로드 로직

  progressBar.stop();
}
```

### 배치 업로드

```javascript
const glob = require('glob');

async function batchUpload(videoFolder) {
  const videos = glob.sync(path.join(videoFolder, '*.mp4'));

  for (const videoPath of videos) {
    const filename = path.basename(videoPath, '.mp4');

    const metadata = {
      title: filename,
      description: 'Auto-uploaded video',
      privacyStatus: 'private',
    };

    try {
      await uploadVideo(videoPath, metadata);
      console.log(`✅ ${filename} 업로드 완료`);

      // 할당량 제한 대비 대기
      await sleep(5000); // 5초 대기
    } catch (error) {
      console.error(`❌ ${filename} 업로드 실패:`, error.message);
    }
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
```

---

## 7. 에러 핸들링

### 일반적인 에러

| 에러 | 원인 | 해결 |
|------|------|------|
| `quota exceeded` | 일일 할당량 초과 | 다음 날 재시도 또는 할당량 증가 신청 |
| `invalid credentials` | OAuth 토큰 만료 | token.json 삭제 후 재인증 |
| `file too large` | 파일 크기 제한 초과 (256GB) | 영상 압축 |
| `duplicate upload` | 같은 파일 중복 업로드 | 파일명 변경 또는 메타데이터 변경 |

### Retry 로직

```javascript
const retry = require('async-retry');

async function uploadWithRetry(videoPath, metadata) {
  return await retry(
    async () => {
      return await uploadVideo(videoPath, metadata);
    },
    {
      retries: 3,
      factor: 2,
      minTimeout: 1000,
      maxTimeout: 10000,
      onRetry: (err, attempt) => {
        console.log(`재시도 ${attempt}/3: ${err.message}`);
      },
    }
  );
}
```

---

## 8. 메타데이터 최적화 팁

### 제목 작성
```
[핵심 키워드] + [숫자/결과] + [후킹 요소]

좋은 예:
✅ "2024 부동산 -32.7% 폭락, 5가지 원인 분석"
✅ "ChatGPT 활용법 10가지 (실전편)"

나쁜 예:
❌ "부동산 영상"
❌ "Video 1"
```

### 설명란 구조
```markdown
[한 줄 요약]

📊 주요 내용:
- 포인트 1
- 포인트 2
- 포인트 3

⏱️ 타임스탬프:
0:00 인트로
0:30 첫 번째 주제
2:15 두 번째 주제

🤖 제작 정보:
- AI 생성 도구: Google NotebookLM
- 원본 자료: [출처]

#태그1 #태그2 #태그3
```

### 태그 선택
- 5-10개 적절
- 핵심 키워드 우선
- 구체적일수록 좋음
- 과도한 태그는 역효과

### 카테고리 ID
- 22: People & Blogs
- 27: Education
- 28: Science & Technology
- 24: Entertainment
- [전체 목록](https://developers.google.com/youtube/v3/docs/videoCategories/list)

---

## 9. 보안 주의사항

### credentials.json 보호
```bash
# .gitignore
config/credentials.json
config/token.json
.env
```

### 환경 변수 사용
```javascript
// .env
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://localhost:3000/oauth2callback

// .env 로드
require('dotenv').config();
```

---

## 10. 참고 자료

### 공식 문서
- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [API Reference](https://developers.google.com/youtube/v3/docs)
- [googleapis Node.js](https://github.com/googleapis/google-api-nodejs-client)

### 할당량 관리
- [할당량 계산기](https://developers.google.com/youtube/v3/determine_quota_cost)
- [할당량 증가 신청](https://support.google.com/youtube/contact/yt_api_form)

### 샘플 코드
- [공식 샘플](https://github.com/youtube/api-samples/tree/master/nodejs)
