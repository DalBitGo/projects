# 사용자 워크플로우 및 시나리오

## 1. 개요

### 1.1 목적
사용자가 랭킹 쇼츠를 생성하는 전체 과정을 단계별로 설명

### 1.2 사용자 유형
- **주 사용자**: 콘텐츠 크리에이터 (개인, 유튜버)
- **기술 수준**: 중급 (기본적인 컴퓨터 사용 가능)

---

## 2. 기본 워크플로우

```
[1] 검색 → [2] 선택 → [3] 생성 → [4] 검수 → [5] 완료
```

### 2.1 상세 단계

```
1. 홈 페이지 접속
   ↓
2. "Start New Project" 클릭
   ↓
3. 검색 페이지
   ├─ 키워드 입력 (예: "football skills")
   ├─ 필터 설정 (선택사항)
   └─ "Search" 클릭
   ↓
4. 검색 대기 (20-30초)
   ├─ 진행 상황 표시
   └─ 완료 시 자동 이동
   ↓
5. 영상 선택 페이지
   ├─ 20-30개 영상 카드 표시
   ├─ 5-7개 영상 선택 (체크박스)
   ├─ 드래그 앤 드롭으로 순서 조정
   └─ "Generate Video" 클릭
   ↓
6. 생성 진행 페이지
   ├─ 진행 상황 실시간 표시
   ├─ 예상 완료 시간 표시
   └─ 완료 시 자동 이동
   ↓
7. 미리보기 & 검수 페이지
   ├─ 생성된 영상 재생
   ├─ 품질 확인
   └─ 승인/재작업/삭제 선택
   ↓
8. 라이브러리에 저장 또는 다운로드
```

---

## 3. 상세 시나리오

### 시나리오 1: 축구 골 랭킹 영상 제작

#### 3.1 사용자 정보
- **이름**: 김유튜버
- **목표**: "Top 5 Amazing Football Goals" 쇼츠 제작
- **소요 시간**: 약 10분

#### 3.2 단계별 과정

**Step 1: 홈 페이지 접속**
```
김유튜버가 브라우저에서 http://localhost:5173 접속
→ 홈 페이지 표시
→ "Start New Project" 버튼 클릭
```

**Step 2: 검색 설정**
```
검색 페이지 진입
→ 키워드 입력: "football goals amazing"
→ 고급 옵션 설정:
   - Min Views: 500,000
   - Max Duration: 30 seconds
→ "Search" 버튼 클릭
```

**Step 3: 검색 대기**
```
로딩 화면 표시
→ "Searching TikTok for 'football goals amazing'..."
→ 진행 상황: [████████░░] 80%
→ 25초 후 완료
→ 자동으로 선택 페이지 이동
```

**Step 4: 영상 선택**
```
28개 영상 카드 표시
→ 썸네일, 조회수, 좋아요 수 확인
→ 다음 5개 영상 선택:
   1. Video 3 (2M views, amazing goal)
   2. Video 7 (1.5M views, bicycle kick)
   3. Video 1 (3M views, long range)
   4. Video 12 (800K views, team play)
   5. Video 5 (1.2M views, free kick)

→ 선택 영역에서 드래그 앤 드롭으로 순서 조정:
   최종 순서: #1 Video 1 (3M), #2 Video 3 (2M), ...

→ "Generate Video" 버튼 활성화
→ 클릭
```

**Step 5: 생성 대기**
```
생성 진행 페이지 표시
→ 진행 상황 실시간 업데이트:
   [✓] Downloading videos (5/5)
   [✓] Preprocessing videos
   [✓] Adding ranking text
   [⏳] Concatenating videos... 65%
   [⏹] Adding background music
   [⏹] Final rendering

→ 예상 시간: 3분
→ 3분 20초 후 완료
→ 자동으로 미리보기 페이지 이동
```

**Step 6: 미리보기 & 검수**
```
생성된 영상 자동 재생
→ 김유튜버가 영상 확인:
   - 랭킹 텍스트 위치 OK
   - 영상 품질 OK
   - 배경음악 볼륨 약간 큼 → 재작업 필요

→ "Retry" 버튼 클릭
→ 설정 조정 (배경음악 볼륨: 30% → 20%)
→ 재생성 (2분 소요)

→ 재확인 → 만족
→ "✓ Approve & Save to Library" 클릭
```

**Step 7: 다운로드**
```
라이브러리 페이지 이동
→ "Top 5 Amazing Football Goals" 프로젝트 표시
→ "Download" 버튼 클릭
→ ranking_short_20250119.mp4 다운로드 완료
```

**Step 8: 유튜브 업로드**
```
김유튜버가 유튜브 스튜디오에서 수동 업로드
→ 완료!
```

---

### 시나리오 2: 빠른 테스트 워크플로우

#### 사용자 정보
- **이름**: 박개발자
- **목표**: 시스템 동작 테스트
- **소요 시간**: 약 5분

#### 과정
```
1. 홈 → "Start New Project"
2. 검색: "test" 입력, 필터 없음 → Search
3. 검색 완료 → 무작위로 5개 선택
4. 순서 조정 없이 바로 "Generate Video"
5. 생성 완료 → 1~2초 재생 확인
6. "Delete" 클릭 (테스트 영상이므로)
```

---

### 시나리오 3: 에러 발생 시나리오

#### 문제 상황
TikTok 스크래핑 실패

#### 과정
```
1. 검색 페이지에서 "coding tips" 입력 → Search
2. 검색 중... 30초 경과
3. 에러 메시지 표시:
   ┌─────────────────────────────────┐
   │ ⚠ Search Failed                │
   │ Unable to connect to TikTok.    │
   │ Please try again later.         │
   │                                 │
   │ [Retry] [Cancel]                │
   └─────────────────────────────────┘

4. 사용자가 "Retry" 클릭
5. 재시도 → 성공
```

---

## 4. 화면별 상호작용 상세

### 4.1 검색 페이지

#### 4.1.1 입력 요소
**키워드 입력 필드**:
- Placeholder: "Enter hashtag or keyword (e.g., football skills)"
- 자동 완성 (검색 히스토리)
- Enter 키로 검색 실행 가능

**필터 패널**:
- 토글 버튼으로 열기/닫기
- 슬라이더로 값 조정 (Min Views, Max Duration)
- "Reset Filters" 버튼

#### 4.1.2 검증
- 빈 키워드 → 에러: "Please enter a keyword"
- 너무 짧은 키워드 (< 2자) → 경고: "Keyword too short"

#### 4.1.3 사용자 피드백
- 검색 버튼 클릭 → 버튼 비활성화 + 로딩 스피너
- Toast 알림: "Search started for 'football skills'"

---

### 4.2 영상 선택 페이지

#### 4.2.1 영상 카드 상호작용
**호버**:
- 카드 확대 효과
- "Play Preview" 버튼 표시

**클릭**:
- 체크박스 토글
- 선택 카운터 업데이트 (3/7)

**미리보기**:
- Play 버튼 클릭 → 모달 팝업
- 영상 자동 재생 (음소거)
- ESC 키로 닫기

#### 4.2.2 드래그 앤 드롭
- 마우스 드래그로 순서 변경
- 드래그 중 카드 반투명 표시
- 드롭 시 순서 즉시 반영

#### 4.2.3 검증
- 5개 미만 선택 → "Generate Video" 버튼 비활성화
- 7개 초과 선택 → 추가 선택 불가, Toast: "Maximum 7 videos allowed"

---

### 4.3 생성 진행 페이지

#### 4.3.1 진행 상황 표시
```
[████████████████░░░░░░] 65%

Current Step:
⏳ Concatenating videos (in progress)

Estimated Time: 2 minutes

Steps:
✅ Downloaded videos (5/5)
✅ Preprocessed videos (5/5)
✅ Added ranking text (5/5)
⏳ Concatenating videos (in progress)
⏹ Adding background music
⏹ Final rendering
```

#### 4.3.2 WebSocket 업데이트
- 1초마다 진행률 업데이트
- 단계 변경 시 체크마크 추가

#### 4.3.3 취소 기능 (선택사항)
- "Cancel" 버튼 클릭
- 확인 다이얼로그:
  ```
  Are you sure you want to cancel?
  This action cannot be undone.
  [No] [Yes, Cancel]
  ```

---

### 4.4 미리보기 & 검수 페이지

#### 4.4.1 영상 플레이어
- 자동 재생 (음소거 해제)
- 컨트롤: 재생/일시정지, 볼륨, 전체화면
- 모바일 비율 (9:16) 유지

#### 4.4.2 액션 버튼
**Download**:
- 클릭 → 파일 다운로드 시작
- 다운로드 완료 Toast: "Video downloaded successfully"

**Retry**:
- 클릭 → 설정 모달 표시
- 설정 변경 (배경음악, 텍스트 위치 등)
- "Regenerate" → 생성 페이지로 이동

**Delete**:
- 클릭 → 확인 다이얼로그
- 삭제 후 라이브러리로 이동

**Approve**:
- 클릭 → DB 업데이트 (status = 'approved')
- 파일 이동: `pending/` → `approved/`
- Toast: "Video approved and saved to library"
- 라이브러리로 이동

---

## 5. 키보드 단축키

| 키 | 액션 | 페이지 |
|----|------|--------|
| `Ctrl + K` | 검색 필드 포커스 | 전체 |
| `Enter` | 검색 실행 | 검색 페이지 |
| `Space` | 영상 선택 토글 | 선택 페이지 |
| `↑` `↓` | 영상 순서 변경 | 선택 페이지 |
| `Esc` | 모달 닫기 | 전체 |
| `D` | 다운로드 | 미리보기 페이지 |
| `A` | 승인 | 미리보기 페이지 |

---

## 6. 모바일/태블릿 워크플로우 (향후)

### 6.1 반응형 조정
- **모바일**: 1열 그리드, 햄버거 메뉴
- **태블릿**: 2열 그리드
- **데스크톱**: 4열 그리드

### 6.2 터치 제스처
- **스와이프**: 영상 카드 간 이동
- **롱 프레스**: 카드 선택
- **핀치 줌**: 미리보기 확대

---

## 7. 에러 처리 워크플로우

### 7.1 검색 실패
```
사용자 입력 → 검색 실행 → TikTok 연결 실패
→ 에러 화면 표시
→ 옵션:
   1. [Retry] → 재시도
   2. [Use Manual URLs] → 수동 URL 입력 모드
   3. [Cancel] → 홈으로 이동
```

### 7.2 영상 다운로드 실패
```
생성 시작 → 영상 1개 다운로드 실패
→ 진행 중단
→ 알림: "Failed to download video 3. Please select a different video."
→ 옵션:
   1. [Replace Video] → 선택 페이지로 돌아가 다른 영상 선택
   2. [Continue with 4 videos] → 4개로 계속 진행
   3. [Cancel] → 프로젝트 취소
```

### 7.3 영상 처리 실패
```
FFmpeg 에러 발생
→ 진행 중단
→ 에러 로그 표시 (개발자용)
→ 알림: "Video processing failed. Please try again or contact support."
→ 옵션:
   1. [Retry] → 재시도
   2. [Report Issue] → GitHub Issue 페이지 열기
```

---

## 8. 고급 사용자 시나리오

### 시나리오 4: 배치 작업

#### 목표
한 번에 여러 주제의 랭킹 영상 생성

#### 과정
```
1. 프로젝트 1: "Top 5 Football Goals"
   → 검색 → 선택 → 생성 시작

2. 생성 진행 중, 새 탭에서 프로젝트 2 시작
   → "Top 5 Basketball Dunks"
   → 검색 → 선택 → 생성 시작

3. 두 프로젝트 동시 진행 (Celery 큐)
   → 프로젝트 1: 65% 완료
   → 프로젝트 2: 대기 중 (Queued)

4. 프로젝트 1 완료 → 승인
5. 프로젝트 2 자동 시작 → 완료 → 승인
```

---

### 시나리오 5: 템플릿 사용 (향후 기능)

```
1. 검색 → 선택
2. "Generate Video" 대신 "Choose Template" 클릭
3. 템플릿 선택:
   - Sports Highlights (골드 텍스트, Epic 음악)
   - Comedy (컬러풀 텍스트, 밝은 음악)
   - Gaming (네온 텍스트, Electronic 음악)

4. 템플릿 적용 → 자동 설정
5. 생성
```

---

## 9. 사용자 피드백 메커니즘

### 9.1 Toast 알림
```javascript
// 성공
showToast("Video generated successfully!", "success")

// 정보
showToast("Downloading video 3/5...", "info")

// 경고
showToast("Please select at least 5 videos", "warning")

// 에러
showToast("Failed to connect to TikTok", "error")
```

### 9.2 프로그레스 표시
- **무한정 로딩**: 초기 연결 시
- **진행률 바**: 다운로드, 처리 중
- **스테퍼**: 전체 워크플로우 진행 상황

### 9.3 확인 다이얼로그
- 삭제 작업 전
- 취소 작업 전
- 중요한 설정 변경 전

---

## 10. 성능 기대치

| 단계 | 예상 소요 시간 |
|------|---------------|
| 검색 (30개 영상) | 20-40초 |
| 영상 다운로드 (5개) | 1-3분 |
| 영상 처리 | 2-4분 |
| **전체 워크플로우** | **5-10분** |

---

## 11. 사용자 교육

### 11.1 온보딩 (첫 실행 시)
```
Welcome to Ranking Shorts Generator!

Let's create your first ranking short in 3 steps:
[Step 1] Search for videos
[Step 2] Select and arrange
[Step 3] Generate!

[Start Tutorial] [Skip]
```

### 11.2 툴팁
- 각 기능에 "?" 아이콘
- 호버 시 간단한 설명 표시

### 11.3 도움말 링크
- 네비게이션 바에 "Help" 링크
- 문서 페이지로 연결

---

**문서 버전**: 1.0
**작성일**: 2025-01-19
**최종 수정일**: 2025-01-19
