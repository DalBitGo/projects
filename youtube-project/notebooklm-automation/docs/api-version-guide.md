# API 버전 가이드 (API 키 있음)

API를 활용한 완전 자동화 구축 가이드

## 대상

- YouTube Data API v3 사용 가능 (무료 할당량)
- NotebookLM Enterprise 고려 중 (유료)
- 프로그래밍으로 완전 자동화 원하는 경우
- 대량 처리 필요한 경우

## API 종류 및 비용

| API | 비용 | 기능 | 추천 |
|-----|------|------|------|
| **YouTube Data API v3** | 무료 (할당량 제한) | 영상 업로드, 메타데이터 관리 | ✅ 필수 |
| **NotebookLM Enterprise API** | 유료 | 노트북/소스 관리, 오디오 생성 | ⚠️ Video API 확인 필요 |

---

## Level 1: YouTube API만 사용 (추천)

**자동화 수준**: 60%
**비용**: 무료 (할당량 내)
**난이도**: ⭐⭐ 쉬움

### 개요

- NotebookLM: 수동 or 브라우저 자동화
- YouTube: API로 완전 자동화

```
1. [수동] NotebookLM에서 Video Overview 생성 & 다운로드
   ↓
2. [자동] YouTube Data API로 업로드
   ↓
3. [자동] 메타데이터 설정
   ↓
4. [자동] 썸네일 업로드
   ↓
5. [수동] 검수 후 공개
```

### YouTube Data API v3 설정

#### 1단계: Google Cloud Console 설정

```bash
# 1. Google Cloud Console 접속
https://console.cloud.google.com/

# 2. 프로젝트 생성
프로젝트 이름: youtube-automation

# 3. API 활성화
API 및 서비스 → 라이브러리 → "YouTube Data API v3" 검색 → 사용 설정

# 4. OAuth 2.0 클라이언트 ID 생성
사용자 인증 정보 → 사용자 인증 정보 만들기 → OAuth 클라이언트 ID
애플리케이션 유형: 데스크톱 앱
이름: youtube-uploader

# 5. JSON 다운로드
생성된 클라이언트 ID → JSON 다운로드 → credentials.json으로 저장
```

#### 2단계: OAuth 동의 화면

```
1. OAuth 동의 화면 → 외부 → 만들기
2. 앱 정보:
   - 앱 이름: NotebookLM YouTube Automation
   - 사용자 지원 이메일: [본인 이메일]
   - 개발자 연락처: [본인 이메일]

3. 범위 추가:
   - https://www.googleapis.com/auth/youtube.upload
   - https://www.googleapis.com/auth/youtube

4. 테스트 사용자:
   - [본인 Google 계정] 추가
```

#### 3단계: 할당량 확인

- **기본 할당량**: 10,000 units/day
- **영상 업로드**: 1,600 units
- **하루 최대**: 약 6개 영상

```
할당량 계산:
- videos.insert: 1,600 units
- thumbnails.set: 50 units
- videos.update: 50 units

총: 1,700 units/영상
10,000 / 1,700 ≈ 5.8개 영상/일
```

### 구현

#### 프로젝트 구조

```
notebooklm-automation/
├── config/
│   ├── credentials.json      # OAuth 클라이언트 ID (수동 다운로드)
│   └── token.json            # 액세스 토큰 (자동 생성)
├── src/
│   └── api/
│       ├── auth.js           # 인증
│       ├── youtube-upload.js # 업로드
│       └── main.js           # 메인 스크립트
├── videos/                   # 업로드할 영상
├── downloads/                # NotebookLM 다운로드 영상
└── package.json
```

#### 패키지 설치

```bash
npm init -y
npm install googleapis @google-cloud/local-auth dotenv
```

#### auth.js

```javascript
const fs = require('fs').promises;
const path = require('path');
const { authenticate } = require('@google-cloud/local-auth');
const { google } = require('googleapis');

const SCOPES = [
  'https://www.googleapis.com/auth/youtube.upload',
  'https://www.googleapis.com/auth/youtube',
];
const TOKEN_PATH = path.join(__dirname, '../../config/token.json');
const CREDENTIALS_PATH = path.join(__dirname, '../../config/credentials.json');

async function authorize() {
  // 저장된 토큰 확인
  let client = await loadSavedCredentialsIfExist();
  if (client) {
    return client;
  }

  // 새로 인증
  client = await authenticate({
    scopes: SCOPES,
    keyfilePath: CREDENTIALS_PATH,
  });

  if (client.credentials) {
    await saveCredentials(client);
  }

  return client;
}

async function loadSavedCredentialsIfExist() {
  try {
    const content = await fs.readFile(TOKEN_PATH);
    const credentials = JSON.parse(content);
    return google.auth.fromJSON(credentials);
  } catch (err) {
    return null;
  }
}

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

#### youtube-upload.js

```javascript
const fs = require('fs');
const { google } = require('googleapis');
const { authorize } = require('./auth');

/**
 * YouTube 영상 업로드
 */
async function uploadVideo(videoPath, metadata) {
  const auth = await authorize();
  const youtube = google.youtube({ version: 'v3', auth });

  const fileSize = fs.statSync(videoPath).size;
  console.log(`파일 크기: ${(fileSize / 1024 / 1024).toFixed(2)} MB`);

  const videoMetadata = {
    snippet: {
      title: metadata.title,
      description: metadata.description,
      tags: metadata.tags || [],
      categoryId: metadata.categoryId || '22', // People & Blogs
      defaultLanguage: 'ko',
      defaultAudioLanguage: 'ko',
    },
    status: {
      privacyStatus: metadata.privacyStatus || 'private',
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

    console.log('✅ 업로드 완료!');
    console.log('Video ID:', videoId);
    console.log('URL:', videoUrl);

    return {
      videoId,
      videoUrl,
      response: response.data,
    };
  } catch (error) {
    console.error('❌ 업로드 실패:', error.message);
    if (error.code === 403) {
      console.error('할당량 초과 또는 권한 부족');
    }
    throw error;
  }
}

/**
 * 썸네일 업로드
 */
async function uploadThumbnail(videoId, thumbnailPath) {
  const auth = await authorize();
  const youtube = google.youtube({ version: 'v3', auth });

  const media = {
    mimeType: 'image/jpeg',
    body: fs.createReadStream(thumbnailPath),
  };

  try {
    console.log('썸네일 업로드 중...');
    const response = await youtube.thumbnails.set({
      videoId: videoId,
      media: media,
    });

    console.log('✅ 썸네일 업로드 완료');
    return response.data;
  } catch (error) {
    console.error('❌ 썸네일 업로드 실패:', error.message);
    throw error;
  }
}

/**
 * 영상 공개 설정 변경
 */
async function updatePrivacyStatus(videoId, privacyStatus) {
  const auth = await authorize();
  const youtube = google.youtube({ version: 'v3', auth });

  try {
    const response = await youtube.videos.update({
      part: 'status',
      requestBody: {
        id: videoId,
        status: {
          privacyStatus: privacyStatus, // 'public', 'unlisted', 'private'
        },
      },
    });

    console.log(`✅ 공개 설정 변경: ${privacyStatus}`);
    return response.data;
  } catch (error) {
    console.error('❌ 상태 업데이트 실패:', error.message);
    throw error;
  }
}

/**
 * 재생목록에 추가
 */
async function addToPlaylist(videoId, playlistId) {
  const auth = await authorize();
  const youtube = google.youtube({ version: 'v3', auth });

  try {
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

    console.log('✅ 재생목록에 추가 완료');
    return response.data;
  } catch (error) {
    console.error('❌ 재생목록 추가 실패:', error.message);
    throw error;
  }
}

module.exports = {
  uploadVideo,
  uploadThumbnail,
  updatePrivacyStatus,
  addToPlaylist,
};
```

#### main.js

```javascript
const path = require('path');
const { uploadVideo, uploadThumbnail } = require('./youtube-upload');

async function main() {
  // NotebookLM에서 다운로드한 영상
  const videoPath = path.join(__dirname, '../../downloads/video.mp4');
  const thumbnailPath = path.join(__dirname, '../../downloads/thumbnail.jpg');

  const metadata = {
    title: '2024 부동산 시장 분석 - NotebookLM 자동 생성',
    description: `
📊 2024년 부동산 시장 주요 지표 분석

주요 내용:
- 전년 대비 거래량 -32.7% 감소
- 평균 가격 변동 추이
- 지역별 상세 분석

⏱️ 타임스탬프:
0:00 인트로
0:30 시장 개요
1:45 지역별 분석
3:20 향후 전망

🤖 제작 정보:
- AI 생성: Google NotebookLM
- 자동 업로드: YouTube Data API v3

📁 원본 자료: [출처 링크]

#부동산 #시장분석 #NotebookLM #AI생성콘텐츠
    `.trim(),
    tags: ['부동산', '시장분석', 'NotebookLM', 'AI', '데이터분석'],
    categoryId: '22', // People & Blogs
    privacyStatus: 'private', // 검수 후 공개
  };

  try {
    // 1. 영상 업로드
    console.log('1️⃣ 영상 업로드 중...\n');
    const result = await uploadVideo(videoPath, metadata);

    // 2. 썸네일 업로드
    console.log('\n2️⃣ 썸네일 업로드 중...\n');
    await uploadThumbnail(result.videoId, thumbnailPath);

    console.log('\n✅ 모든 작업 완료!');
    console.log('YouTube URL:', result.videoUrl);
    console.log('\n⚠️  YouTube Studio에서 검수 후 공개 처리하세요.');
  } catch (error) {
    console.error('\n❌ 에러 발생:', error);
  }
}

main();
```

#### 실행

```bash
# 첫 실행 시 OAuth 인증 (브라우저 열림)
node src/api/main.js

# 이후 실행은 token.json 사용 (자동)
node src/api/main.js
```

### 장점

- ✅ YouTube 업로드 완전 자동화
- ✅ 안정적 (공식 API)
- ✅ 메타데이터 프로그래밍 제어
- ✅ 에러 핸들링 쉬움
- ✅ 무료 (할당량 내)

### 단점

- ❌ NotebookLM은 여전히 수동
- ❌ 하루 6개 영상 제한 (할당량)

---

## Level 2: NotebookLM Enterprise API 추가 (프로덕션)

**자동화 수준**: 100%
**비용**: Enterprise 요금제 (문의 필요)
**난이도**: ⭐⭐⭐⭐ 어려움

### 개요

```
1. [자동] NotebookLM Enterprise API로 노트북 생성
   ↓
2. [자동] 소스 업로드
   ↓
3. [자동] Audio Overview 생성 (현재 지원)
   ↓
4. [확인 필요] Video Overview API 지원 여부
   ↓
5. [자동] YouTube Data API로 업로드
```

### NotebookLM Enterprise API 설정

#### 1단계: Enterprise 계정 신청

```
1. Google Cloud 영업팀 문의
   https://cloud.google.com/contact

2. NotebookLM Enterprise 계약
   - 가격 문의 필요
   - API 액세스 권한 포함

3. Google Cloud 프로젝트 설정
   - API 활성화
   - 서비스 계정 생성
```

#### 2단계: API 활성화

```bash
# Google Cloud Console
1. API 및 서비스 → 라이브러리
2. "NotebookLM API" 또는 "Discovery Engine API" 검색
3. 사용 설정
```

#### 3단계: 인증 설정

```bash
# 서비스 계정 키 다운로드
gcloud iam service-accounts keys create key.json \
  --iam-account=SERVICE_ACCOUNT_EMAIL
```

### 구현 (현재 API 기준)

#### 패키지 설치

```bash
npm install @google-cloud/discoveryengine
```

#### notebooklm-api.js

```javascript
const { DiscoveryEngineServiceClient } = require('@google-cloud/discoveryengine');

// 주의: Video Overview API 지원 여부 확인 필요
// 현재는 Audio Overview만 공식 문서에 명시

class NotebookLMClient {
  constructor(projectId, location = 'us') {
    this.client = new DiscoveryEngineServiceClient();
    this.parent = `projects/${projectId}/locations/${location}`;
  }

  /**
   * 노트북 생성
   */
  async createNotebook(displayName) {
    try {
      const [notebook] = await this.client.createNotebook({
        parent: this.parent,
        notebook: {
          displayName: displayName,
        },
      });

      console.log('✅ 노트북 생성:', notebook.name);
      return notebook;
    } catch (error) {
      console.error('❌ 노트북 생성 실패:', error.message);
      throw error;
    }
  }

  /**
   * 소스 추가 (문서 업로드)
   */
  async addSources(notebookName, sources) {
    try {
      const [operation] = await this.client.batchCreateSources({
        parent: notebookName,
        sources: sources.map((source) => ({
          uri: source.uri, // Google Drive URL or Cloud Storage URI
          displayName: source.displayName,
        })),
      });

      console.log('✅ 소스 추가 완료');
      return operation;
    } catch (error) {
      console.error('❌ 소스 추가 실패:', error.message);
      throw error;
    }
  }

  /**
   * Audio Overview 생성 (현재 지원)
   */
  async generateAudioOverview(notebookName, options = {}) {
    try {
      // API 문서 기준 (실제 메서드명은 문서 확인 필요)
      const [operation] = await this.client.generateAudioOverview({
        notebook: notebookName,
        language: options.language || 'ko',
        format: options.format || 'podcast',
      });

      console.log('✅ Audio Overview 생성 완료');
      return operation;
    } catch (error) {
      console.error('❌ Audio Overview 생성 실패:', error.message);
      throw error;
    }
  }

  /**
   * Video Overview 생성 (지원 여부 확인 필요)
   */
  async generateVideoOverview(notebookName, options = {}) {
    // ⚠️ 주의: 공식 API 문서에 Video Overview 메서드 확인 필요
    // 현재 문서에는 Audio Overview만 명시

    try {
      // 가상의 API 호출 (실제 지원 여부 확인 필요)
      const [operation] = await this.client.generateVideoOverview({
        notebook: notebookName,
        format: options.format || 'EXPLAINER', // 'EXPLAINER' or 'BRIEF'
        style: options.style || 'WHITEBOARD',
        language: options.language || 'ko',
        customPrompt: options.prompt || '',
      });

      console.log('✅ Video Overview 생성 완료');
      return operation;
    } catch (error) {
      console.error('❌ Video Overview 생성 실패:', error.message);
      console.error('⚠️  Video Overview API 미지원 가능성 확인 필요');
      throw error;
    }
  }

  /**
   * 생성된 영상 다운로드
   */
  async downloadVideo(videoUri, outputPath) {
    // Cloud Storage에서 다운로드
    const { Storage } = require('@google-cloud/storage');
    const storage = new Storage();

    try {
      await storage.bucket(bucketName).file(fileName).download({
        destination: outputPath,
      });

      console.log('✅ 영상 다운로드 완료:', outputPath);
      return outputPath;
    } catch (error) {
      console.error('❌ 다운로드 실패:', error.message);
      throw error;
    }
  }
}

module.exports = { NotebookLMClient };
```

#### full-automation.js

```javascript
const { NotebookLMClient } = require('./notebooklm-api');
const { uploadVideo, uploadThumbnail } = require('./youtube-upload');

async function fullAutomation(documentUri, metadata) {
  console.log('=== 완전 자동화 파이프라인 시작 ===\n');

  try {
    // 1. NotebookLM 노트북 생성
    console.log('1️⃣ NotebookLM 노트북 생성 중...');
    const nbClient = new NotebookLMClient('your-project-id');
    const notebook = await nbClient.createNotebook(metadata.title);

    // 2. 소스 추가
    console.log('\n2️⃣ 문서 업로드 중...');
    await nbClient.addSources(notebook.name, [
      {
        uri: documentUri, // gs://bucket/file.pdf or Google Drive URL
        displayName: 'Source Document',
      },
    ]);

    // 3. Video Overview 생성
    console.log('\n3️⃣ Video Overview 생성 중...');
    const videoOp = await nbClient.generateVideoOverview(notebook.name, {
      format: 'EXPLAINER',
      style: 'WHITEBOARD',
      language: 'ko',
      prompt: metadata.customPrompt,
    });

    // 4. 생성 완료 대기
    console.log('생성 완료 대기 중... (최대 10분)');
    const [video] = await videoOp.promise(); // Long-running operation
    const videoPath = await nbClient.downloadVideo(video.uri, './downloads/video.mp4');

    // 5. YouTube 업로드
    console.log('\n4️⃣ YouTube 업로드 중...');
    const result = await uploadVideo(videoPath, {
      title: metadata.title,
      description: metadata.description,
      tags: metadata.tags,
      privacyStatus: 'private',
    });

    // 6. 썸네일 업로드
    if (metadata.thumbnailPath) {
      console.log('\n5️⃣ 썸네일 업로드 중...');
      await uploadThumbnail(result.videoId, metadata.thumbnailPath);
    }

    console.log('\n✅ 완전 자동화 완료!');
    console.log('YouTube URL:', result.videoUrl);
    console.log('\n⚠️  검수 후 공개 처리하세요.');

    return result;
  } catch (error) {
    console.error('\n❌ 에러 발생:', error);
    throw error;
  }
}

// 사용 예시
const metadata = {
  title: '2024 부동산 시장 분석',
  description: '...',
  tags: ['부동산', '시장분석'],
  customPrompt: '표 중심으로 90초 요약',
};

fullAutomation('gs://my-bucket/report.pdf', metadata);
```

### 중요 확인 사항

#### Video Overview API 지원 여부

현재(2025년 1월 기준) NotebookLM Enterprise API 공식 문서에는:
- ✅ **Audio Overview API**: 명확히 지원
- ❓ **Video Overview API**: **확인 필요**

**확인 방법**:
1. Google Cloud 영업팀에 문의
2. Enterprise API 문서 확인
3. 베타 프로그램 신청 고려

### 비용

| 항목 | 예상 비용 |
|------|----------|
| NotebookLM Enterprise | 문의 필요 (월/연 구독) |
| API 호출 | 포함 or 종량제 |
| Cloud Storage | ~$0.02/GB |
| YouTube API | 무료 |

---

## 할당량 관리

### YouTube API 할당량

#### 기본 전략

```javascript
// 할당량 추적
class QuotaManager {
  constructor(dailyLimit = 10000) {
    this.dailyLimit = dailyLimit;
    this.used = 0;
    this.resetDate = new Date();
    this.resetDate.setHours(0, 0, 0, 0);
    this.resetDate.setDate(this.resetDate.getDate() + 1);
  }

  checkAndUse(cost) {
    if (this.used + cost > this.dailyLimit) {
      throw new Error('일일 할당량 초과');
    }
    this.used += cost;
    console.log(`할당량 사용: ${this.used}/${this.dailyLimit}`);
  }

  getRemainingQuota() {
    return this.dailyLimit - this.used;
  }
}

const quota = new QuotaManager();

// 업로드 전 확인
quota.checkAndUse(1600); // 영상 업로드
await uploadVideo(videoPath, metadata);

quota.checkAndUse(50); // 썸네일
await uploadThumbnail(videoId, thumbnailPath);
```

#### 할당량 증가 신청

```
1. YouTube API 할당량 증가 양식 제출
   https://support.google.com/youtube/contact/yt_api_form

2. 필요 정보:
   - 프로젝트 설명
   - 예상 사용량
   - 비즈니스 목적

3. 승인 기간: 수일 ~ 수주
```

### NotebookLM Enterprise 할당량

- Enterprise 계약에 따라 다름
- API 호출 제한 확인 필요
- 대량 처리 시 배치 API 사용

---

## 에러 핸들링

### Retry 로직

```javascript
const retry = require('async-retry');

async function uploadWithRetry(videoPath, metadata) {
  return await retry(
    async (bail) => {
      try {
        return await uploadVideo(videoPath, metadata);
      } catch (error) {
        // 할당량 초과는 재시도 안함
        if (error.code === 403 && error.message.includes('quota')) {
          bail(new Error('할당량 초과'));
          return;
        }

        // 다른 에러는 재시도
        throw error;
      }
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

### 에러 로깅

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

try {
  await uploadVideo(videoPath, metadata);
  logger.info('Upload successful', { videoPath, videoId });
} catch (error) {
  logger.error('Upload failed', { error: error.message, videoPath });
  throw error;
}
```

---

## 스케줄링 & 모니터링

### Cron 스케줄링

```javascript
const cron = require('node-cron');

// 매일 오전 9시 실행
cron.schedule('0 9 * * *', async () => {
  console.log('스케줄 작업 시작:', new Date());

  const documents = await getNewDocuments('./input/');

  for (const doc of documents) {
    try {
      await fullAutomation(doc.uri, doc.metadata);
    } catch (error) {
      console.error(`${doc.name} 처리 실패:`, error);
    }
  }
});
```

### Slack 알림

```javascript
const axios = require('axios');

async function sendSlackNotification(message) {
  const webhookUrl = process.env.SLACK_WEBHOOK_URL;

  await axios.post(webhookUrl, {
    text: message,
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: message,
        },
      },
    ],
  });
}

// 사용
try {
  const result = await uploadVideo(videoPath, metadata);
  await sendSlackNotification(`✅ 영상 업로드 완료\n${result.videoUrl}`);
} catch (error) {
  await sendSlackNotification(`❌ 업로드 실패\n${error.message}`);
}
```

---

## 보안 Best Practices

### 환경 변수

```bash
# .env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./config/service-account-key.json
YOUTUBE_OAUTH_CLIENT_ID=xxx.apps.googleusercontent.com
YOUTUBE_OAUTH_CLIENT_SECRET=xxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
```

```javascript
require('dotenv').config();

// 사용
const projectId = process.env.GOOGLE_CLOUD_PROJECT;
```

### .gitignore

```
# API 키 & 인증 정보
.env
config/credentials.json
config/token.json
config/service-account-key.json
config/cookies.json

# 다운로드 파일
downloads/
videos/

# 로그
*.log
```

### Secret Manager (프로덕션)

```javascript
const { SecretManagerServiceClient } = require('@google-cloud/secret-manager');

async function getSecret(secretName) {
  const client = new SecretManagerServiceClient();
  const [version] = await client.accessSecretVersion({
    name: `projects/${projectId}/secrets/${secretName}/versions/latest`,
  });

  return version.payload.data.toString();
}

const apiKey = await getSecret('youtube-api-key');
```

---

## 비용 최적화

### 무료 티어 최대 활용

| 서비스 | 무료 할당량 | 최적화 팁 |
|--------|------------|----------|
| YouTube API | 10,000 units/day | 배치 처리, 스케줄링 |
| Cloud Storage | 5GB | 생성 후 즉시 삭제 |
| Cloud Functions | 2M invocations | 서버리스로 비용 절감 |

### 영상 크기 최적화

```javascript
const ffmpeg = require('fluent-ffmpeg');

async function compressVideo(inputPath, outputPath) {
  return new Promise((resolve, reject) => {
    ffmpeg(inputPath)
      .outputOptions([
        '-c:v libx264',
        '-crf 23', // 품질 (18-28, 낮을수록 고품질)
        '-preset medium',
        '-c:a aac',
        '-b:a 128k',
      ])
      .output(outputPath)
      .on('end', resolve)
      .on('error', reject)
      .run();
  });
}
```

---

## 다음 단계

### 체크리스트

- [ ] YouTube Data API v3 설정
- [ ] OAuth 인증 완료
- [ ] 업로드 스크립트 테스트
- [ ] NotebookLM Enterprise 검토
- [ ] Video Overview API 지원 확인
- [ ] 할당량 모니터링 설정
- [ ] 에러 핸들링 & 로깅
- [ ] 스케줄링 구축
- [ ] 프로덕션 배포

### 추천 진행 순서

```
1주: YouTube API 연동 & 테스트
2주: NotebookLM 수동 + YouTube 자동 워크플로우
3주: NotebookLM Enterprise API 검토
4주: 완전 자동화 or 하이브리드 결정
```

---

## 참고 자료

### YouTube API
- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [OAuth 2.0 가이드](https://developers.google.com/identity/protocols/oauth2)
- [googleapis Node.js](https://github.com/googleapis/google-api-nodejs-client)

### NotebookLM Enterprise
- [API 문서](https://cloud.google.com/agentspace/notebooklm-enterprise/docs/api-notebooks)
- [설정 가이드](https://cloud.google.com/agentspace/notebooklm-enterprise/docs/set-up-notebooklm)
- [영업 문의](https://cloud.google.com/contact)

### Google Cloud
- [Cloud Storage](https://cloud.google.com/storage/docs)
- [Secret Manager](https://cloud.google.com/secret-manager/docs)
- [Cloud Functions](https://cloud.google.com/functions/docs)
