# 프론트엔드 UI/UX 설계

## 1. 개요

### 1.1 디자인 철학
- **미니멀리즘**: 불필요한 요소 제거, 핵심 기능에 집중
- **직관성**: 별도 학습 없이 사용 가능
- **반응성**: 실시간 피드백 및 진행 상황 표시
- **접근성**: 다양한 화면 크기 지원

### 1.2 색상 팔레트
```
Primary: #3B82F6 (Blue)
Secondary: #10B981 (Green)
Accent: #F59E0B (Amber)
Background: #F9FAFB (Light Gray)
Text: #111827 (Dark Gray)
Error: #EF4444 (Red)
Success: #10B981 (Green)
```

---

## 2. 페이지 구조 및 라우팅

### 2.1 페이지 맵
```
/ (Home)
│
├─ /search (검색)
│  └─ /select/:searchId (영상 선택)
│     └─ /generate/:projectId (생성 진행)
│        └─ /preview/:videoId (미리보기 & 검수)
│
├─ /library (라이브러리)
│
└─ /settings (설정)
```

### 2.2 네비게이션 바
```
┌────────────────────────────────────────────┐
│ 🎬 Ranking Shorts  [Search][Library][Settings] │
└────────────────────────────────────────────┘
```

---

## 3. 페이지별 상세 설계

### 3.1 홈 페이지 (`/`)

#### 레이아웃
```
┌─────────────────────────────────────────┐
│         Ranking Shorts Generator        │
│                                         │
│   Create viral ranking shorts in       │
│          minutes, not hours             │
│                                         │
│     ┌─────────────────────────┐        │
│     │   [Start New Project]   │        │
│     └─────────────────────────┘        │
│                                         │
│   Recent Projects:                      │
│   ┌───────────┬───────────┬──────────┐ │
│   │ Project 1 │ Project 2 │ Project 3│ │
│   └───────────┴───────────┴──────────┘ │
└─────────────────────────────────────────┘
```

#### 컴포넌트
- Hero Section (제목, 설명, CTA 버튼)
- Recent Projects Grid (최근 프로젝트 카드)

---

### 3.2 검색 페이지 (`/search`)

#### 레이아웃
```
┌─────────────────────────────────────────┐
│  Search TikTok Videos                   │
│  ┌────────────────────┐  [Search]      │
│  │ #football skills   │                 │
│  └────────────────────┘                 │
│                                         │
│  Advanced Options:                      │
│  ☑ Min Views: [100,000]                │
│  ☑ Max Duration: [60] seconds          │
│  ☐ Only verified creators              │
│                                         │
│  [Search]                               │
└─────────────────────────────────────────┘
```

#### 기능
- 검색 입력 (해시태그/키워드)
- 필터링 옵션 (최소 조회수, 최대 길이)
- 검색 히스토리

#### 상태
1. **대기 중**: 빈 입력 폼
2. **검색 중**: 로딩 스피너 + "Searching TikTok..."
3. **결과 표시**: 영상 그리드 (다음 페이지로 이동)

---

### 3.3 영상 선택 페이지 (`/select/:searchId`)

#### 레이아웃
```
┌──────────────────────────────────────────────┐
│ Select Videos (5-7 videos)         [0/7]     │
├──────────────────────────────────────────────┤
│ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐            │
│ │Video│ │Video│ │Video│ │Video│ ...         │
│ │  1  │ │  2  │ │  3  │ │  4  │            │
│ │     │ │     │ │     │ │     │            │
│ │ 👁 1M│ │ 👁 2M│ │ 👁 500K│ │ 👁 800K│      │
│ │ ❤ 50K│ │ ❤ 100K│ │ ❤ 25K│ │ ❤ 40K│      │
│ │[☐]  │ │[☐]  │ │[☐]  │ │[☐]  │            │
│ └─────┘ └─────┘ └─────┘ └─────┘            │
│                                              │
│ Selected Videos:                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 1. [Video 2] ⋮ ⋮                        │ │
│ │ 2. [Video 5] ⋮ ⋮                        │ │
│ │ 3. [Video 1] ⋮ ⋮                        │ │
│ └─────────────────────────────────────────┘ │
│                                              │
│ [Generate Video] →                           │
└──────────────────────────────────────────────┘
```

#### 영상 카드 컴포넌트
```jsx
<VideoCard>
  <Thumbnail src={video.thumbnail} />
  <Stats>
    <Views>👁 {formatNumber(video.views)}</Views>
    <Likes>❤ {formatNumber(video.likes)}</Likes>
  </Stats>
  <Checkbox checked={isSelected} onChange={handleSelect} />
  <PlayButton onClick={openPreview} />
</VideoCard>
```

#### 선택 영역 (드래그 앤 드롭)
- **react-beautiful-dnd** 사용
- 순서 변경 가능
- 랭킹 번호 자동 표시 (1, 2, 3, ...)

#### 검증
- 최소 5개, 최대 7개 선택
- 선택 개수 실시간 표시 (0/7 → 5/7)
- "Generate Video" 버튼은 5개 이상 선택 시 활성화

---

### 3.4 생성 진행 페이지 (`/generate/:projectId`)

#### 레이아웃
```
┌─────────────────────────────────────────┐
│  Generating Your Ranking Short...      │
│                                         │
│  [████████████████░░░░░░] 65%          │
│                                         │
│  Current Step:                          │
│  ⏳ Downloading video 4/5...           │
│                                         │
│  Estimated Time: 2 minutes              │
│                                         │
│  ✅ Downloaded videos                  │
│  ✅ Preprocessed videos                │
│  ✅ Added ranking text                 │
│  ⏳ Concatenating videos (in progress) │
│  ⏹ Adding background music             │
│  ⏹ Final rendering                     │
└─────────────────────────────────────────┘
```

#### 기능
- 실시간 진행 상황 (WebSocket)
- 각 단계별 체크마크
- 예상 완료 시간
- 취소 버튼 (선택사항)

#### 상태
1. **Queued**: "Waiting in queue..."
2. **Processing**: 진행률 표시
3. **Completed**: 자동으로 미리보기 페이지 이동
4. **Failed**: 에러 메시지 + 재시도 버튼

---

### 3.5 미리보기 & 검수 페이지 (`/preview/:videoId`)

#### 레이아웃
```
┌──────────────────────────────────────────────┐
│  Your Ranking Short is Ready! 🎉            │
├──────────────────────────────────────────────┤
│                                              │
│         ┌────────────────┐                   │
│         │                │                   │
│         │  Video Player  │                   │
│         │   (9:16 ratio) │                   │
│         │                │                   │
│         │      ▶         │                   │
│         │                │                   │
│         └────────────────┘                   │
│                                              │
│  Duration: 45s | Size: 15.2 MB              │
│                                              │
│  Actions:                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ Download │ │  Retry   │ │  Delete  │    │
│  └──────────┘ └──────────┘ └──────────┘    │
│                                              │
│  [✓ Approve & Save to Library]              │
└──────────────────────────────────────────────┘
```

#### 영상 플레이어
- **react-player** 사용
- 재생/일시정지 컨트롤
- 볼륨 조절
- 전체화면 지원

#### 액션 버튼
- **Download**: 파일 다운로드
- **Retry**: 동일 설정으로 재생성
- **Delete**: 영상 삭제
- **Approve**: `output/approved/`로 이동 + 라이브러리에 추가

---

### 3.6 라이브러리 페이지 (`/library`)

#### 레이아웃
```
┌──────────────────────────────────────────────┐
│  Your Video Library                          │
│  ┌──────────────────────────────────────┐   │
│  │ [All] [Pending] [Approved] [Search]  │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌────────┐ ┌────────┐ ┌────────┐          │
│  │ Video 1│ │ Video 2│ │ Video 3│  ...     │
│  │ APPROVED│ │ PENDING│ │ APPROVED│         │
│  │        │ │        │ │        │          │
│  │ 📅 Jan 15│ │ 📅 Jan 16│ │ 📅 Jan 17│       │
│  └────────┘ └────────┘ └────────┘          │
└──────────────────────────────────────────────┘
```

#### 기능
- 필터링 (All, Pending, Approved)
- 검색 (제목, 날짜)
- 정렬 (최신순, 오래된순, 이름순)
- 카드 클릭 → 미리보기 페이지

---

### 3.7 설정 페이지 (`/settings`)

#### 레이아웃
```
┌──────────────────────────────────────────────┐
│  Settings                                    │
├──────────────────────────────────────────────┤
│  General                                     │
│  ☐ Auto-approve videos                      │
│  ☑ Show notifications                       │
│  ☑ Auto-delete temp files                   │
│                                              │
│  Video Settings                              │
│  Default Duration: [7] seconds               │
│  Quality: ○ Low ● Medium ○ High             │
│  FPS: [30]                                   │
│                                              │
│  Text Overlay                                │
│  Font: [Arial Bold ▼]                        │
│  Color: [⬜ #FFFFFF]                         │
│  Position: [Top Center ▼]                    │
│                                              │
│  Background Music                            │
│  Default Music: [Energetic 1 ▼]             │
│  Volume: [■■■■■░░░░░] 30%                  │
│                                              │
│  [Save Settings]                             │
└──────────────────────────────────────────────┘
```

---

## 4. 컴포넌트 설계

### 4.1 공통 컴포넌트

#### Button
```jsx
<Button variant="primary" size="md" onClick={handleClick}>
  Click Me
</Button>

// Variants: primary, secondary, danger, ghost
// Sizes: sm, md, lg
```

#### Card
```jsx
<Card>
  <CardHeader>Title</CardHeader>
  <CardBody>Content</CardBody>
  <CardFooter>Actions</CardFooter>
</Card>
```

#### ProgressBar
```jsx
<ProgressBar
  value={65}
  max={100}
  label="Processing..."
  showPercentage={true}
/>
```

#### Modal
```jsx
<Modal isOpen={isOpen} onClose={handleClose}>
  <ModalHeader>Confirm</ModalHeader>
  <ModalBody>Are you sure?</ModalBody>
  <ModalFooter>
    <Button onClick={handleClose}>Cancel</Button>
    <Button variant="primary" onClick={handleConfirm}>OK</Button>
  </ModalFooter>
</Modal>
```

---

### 4.2 비즈니스 컴포넌트

#### VideoCard
```jsx
<VideoCard
  video={videoData}
  isSelected={selected}
  onSelect={handleSelect}
  onPreview={handlePreview}
/>
```

#### DragDropList
```jsx
<DragDropList
  items={selectedVideos}
  onReorder={handleReorder}
  renderItem={(video, index) => (
    <RankingItem rank={index + 1} video={video} />
  )}
/>
```

#### VideoPlayer
```jsx
<VideoPlayer
  url={videoUrl}
  controls={true}
  width="100%"
  height="auto"
  playing={false}
/>
```

---

## 5. 상태 관리 (Zustand)

### 5.1 Video Store
```javascript
// stores/videoStore.js
import { create } from 'zustand'

export const useVideoStore = create((set) => ({
  // State
  searchResults: [],
  selectedVideos: [],
  currentProject: null,

  // Actions
  setSearchResults: (videos) => set({ searchResults: videos }),

  addVideo: (video) => set((state) => ({
    selectedVideos: [...state.selectedVideos, video]
  })),

  removeVideo: (videoId) => set((state) => ({
    selectedVideos: state.selectedVideos.filter(v => v.id !== videoId)
  })),

  reorderVideos: (videos) => set({ selectedVideos: videos }),

  clearSelection: () => set({ selectedVideos: [] }),

  setCurrentProject: (project) => set({ currentProject: project }),
}))
```

### 5.2 UI Store
```javascript
// stores/uiStore.js
export const useUIStore = create((set) => ({
  isLoading: false,
  notification: null,

  setLoading: (loading) => set({ isLoading: loading }),

  showNotification: (message, type = 'info') => set({
    notification: { message, type, id: Date.now() }
  }),

  hideNotification: () => set({ notification: null }),
}))
```

---

## 6. API 통신 (Axios)

### 6.1 API 클라이언트 설정
```javascript
// utils/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000,
})

// Request Interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response Interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 에러 처리
    if (error.response?.status === 401) {
      // 인증 실패
    }
    return Promise.reject(error)
  }
)

export default api
```

### 6.2 API 함수
```javascript
// services/videoService.js
import api from '@/utils/api'

export const searchVideos = async (keyword, filters) => {
  const response = await api.post('/search', { keyword, ...filters })
  return response.data
}

export const getSearchResults = async (searchId) => {
  const response = await api.get(`/search/${searchId}`)
  return response.data
}

export const createProject = async (projectData) => {
  const response = await api.post('/projects', projectData)
  return response.data
}

export const generateVideo = async (projectId) => {
  const response = await api.post(`/projects/${projectId}/generate`)
  return response.data
}
```

---

## 7. WebSocket 연동 (Socket.IO)

### 7.1 Socket 설정
```javascript
// utils/socket.js
import { io } from 'socket.io-client'

const socket = io('http://localhost:8000', {
  transports: ['websocket'],
  autoConnect: false,
})

export default socket
```

### 7.2 사용 예시
```jsx
// pages/GeneratePage.jsx
import { useEffect } from 'react'
import socket from '@/utils/socket'

function GeneratePage() {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    socket.connect()

    socket.emit('subscribe', { projectId })

    socket.on('progress', (data) => {
      setProgress(data.percent)
      // Update UI
    })

    socket.on('completed', (data) => {
      // Navigate to preview
      navigate(`/preview/${data.videoId}`)
    })

    return () => {
      socket.disconnect()
    }
  }, [projectId])

  return (
    <ProgressBar value={progress} />
  )
}
```

---

## 8. 반응형 디자인

### 8.1 Breakpoints (Tailwind)
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
    }
  }
}
```

### 8.2 반응형 레이아웃 예시
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {videos.map(video => (
    <VideoCard key={video.id} video={video} />
  ))}
</div>
```

---

## 9. 접근성 (a11y)

### 9.1 키보드 네비게이션
- Tab: 다음 요소로 이동
- Enter/Space: 버튼 클릭
- Escape: 모달 닫기
- Arrow Keys: 드래그 앤 드롭 순서 변경

### 9.2 스크린 리더 지원
```jsx
<button
  aria-label="Select video"
  aria-pressed={isSelected}
>
  <CheckIcon />
</button>
```

### 9.3 색상 대비
- 최소 대비율 4.5:1 (WCAG AA)
- 텍스트 색상: #111827 (어두운 회색)
- 배경: #FFFFFF (흰색)

---

## 10. 에러 처리 및 피드백

### 10.1 에러 표시
```jsx
<ErrorBoundary fallback={<ErrorPage />}>
  <App />
</ErrorBoundary>
```

### 10.2 Toast 알림
```jsx
// components/Toast.jsx
<Toast type="success" message="Video generated successfully!" />
<Toast type="error" message="Failed to download video" />
<Toast type="info" message="Processing..." />
```

### 10.3 로딩 상태
```jsx
{isLoading ? (
  <Skeleton count={5} />
) : (
  <VideoGrid videos={videos} />
)}
```

---

## 11. 애니메이션 및 전환 효과

### 11.1 페이지 전환
```jsx
import { motion } from 'framer-motion'

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -20 }}
  transition={{ duration: 0.3 }}
>
  <PageContent />
</motion.div>
```

### 11.2 카드 호버 효과
```css
.video-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.video-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}
```

---

## 12. 성능 최적화

### 12.1 이미지 최적화
- 썸네일 lazy loading
- 적절한 이미지 크기 사용
- WebP 포맷 지원

```jsx
<img
  src={thumbnail}
  alt={title}
  loading="lazy"
  className="w-full h-auto"
/>
```

### 12.2 코드 분할
```jsx
import { lazy, Suspense } from 'react'

const LibraryPage = lazy(() => import('./pages/LibraryPage'))

<Suspense fallback={<Loading />}>
  <LibraryPage />
</Suspense>
```

---

**문서 버전**: 1.0
**작성일**: 2025-10-19
**최종 수정일**: 2025-10-19
