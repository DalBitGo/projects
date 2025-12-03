# Google Cloud Platform 설정 가이드

## 📋 목차
1. [개요](#개요)
2. [필수 준비물](#필수-준비물)
3. [단계별 설정](#단계별-설정)
4. [문제 해결](#문제-해결)

---

## 개요

### 무엇을 하는가?
YouTube API를 사용하기 위한 **OAuth 인증 정보**를 생성합니다.

### 필요한 것?
- Google 계정 (Gmail)
- 웹 브라우저
- **시간: 10분**
- **비용: 무료**

### 결과물?
`client_secrets.json` 파일 (로컬 PC에서 사용)

---

## 필수 준비물

### 1. Google 계정
- 이미 있는 Gmail 계정 사용 가능
- 회사 Google Workspace 계정도 가능

### 2. YouTube 채널 계정 이메일
우리가 소유한 3개 계정의 이메일:
```
account1: john@company.com
account2: jane@company.com
account3: team@company.com
```

---

## 단계별 설정

### Step 1: Google Cloud Console 접속

1. 브라우저에서 접속:
   ```
   https://console.cloud.google.com
   ```

2. Google 계정으로 로그인

3. 첫 방문 시 약관 동의

---

### Step 2: 프로젝트 생성

1. 상단 프로젝트 선택기 클릭
   ```
   [선택: 프로젝트 선택] ▼
   ```

2. "새 프로젝트" 클릭

3. 프로젝트 정보 입력:
   ```
   프로젝트 이름: YouTube Intelligence
   조직: (선택 사항, 없으면 공란)
   위치: (선택 사항, 없으면 공란)
   ```

4. "만들기" 클릭

5. 프로젝트 생성 완료 (10초 정도 소요)

6. 상단에서 생성된 프로젝트 선택
   ```
   [YouTube Intelligence] ✓
   ```

---

### Step 3: YouTube API 활성화

#### 3-1. YouTube Data API v3

1. 왼쪽 메뉴에서:
   ```
   API 및 서비스 → 라이브러리
   ```

2. 검색창에 입력:
   ```
   YouTube Data API v3
   ```

3. "YouTube Data API v3" 클릭

4. "사용" 버튼 클릭

5. 활성화 완료 (초록색 체크 표시)

#### 3-2. YouTube Analytics API

1. 다시 "라이브러리"로 이동

2. 검색창에 입력:
   ```
   YouTube Analytics API
   ```

3. "YouTube Analytics API" 클릭

4. "사용" 버튼 클릭

5. 활성화 완료

---

### Step 4: OAuth 동의 화면 구성

1. 왼쪽 메뉴에서:
   ```
   API 및 서비스 → OAuth 동의 화면
   ```

2. 사용자 유형 선택:
   ```
   ◉ 외부
   ◯ 내부 (Google Workspace만 가능)
   ```
   "외부" 선택 후 "만들기"

3. **앱 정보** 입력:
   ```
   앱 이름: YouTube Intelligence
   사용자 지원 이메일: (본인 Gmail 주소)
   앱 로고: (선택 사항, 건너뛰기)
   ```

4. **앱 도메인** (모두 선택 사항, 건너뛰기):
   ```
   앱 홈페이지: (공란)
   개인정보처리방침: (공란)
   서비스 약관: (공란)
   ```

5. **승인된 도메인** (선택 사항, 건너뛰기)

6. **개발자 연락처 정보**:
   ```
   이메일 주소: (본인 Gmail 주소)
   ```

7. "저장 후 계속" 클릭

8. **범위 추가** 화면:
   ```
   "저장 후 계속" 클릭 (범위는 나중에 자동 설정됨)
   ```

9. **테스트 사용자** 추가 ⭐ 중요!:
   ```
   + ADD USERS 클릭

   추가할 이메일:
   - john@company.com
   - jane@company.com
   - team@company.com

   "추가" 클릭
   ```

10. "저장 후 계속" 클릭

11. **요약** 화면에서 내용 확인 후 "대시보드로 돌아가기"

---

### Step 5: OAuth 클라이언트 ID 생성

1. 왼쪽 메뉴에서:
   ```
   API 및 서비스 → 사용자 인증 정보
   ```

2. 상단 "+ 사용자 인증 정보 만들기" 클릭

3. "OAuth 클라이언트 ID" 선택

4. **애플리케이션 유형** 선택:
   ```
   ◉ 데스크톱 앱
   ◯ 웹 애플리케이션
   ◯ Android
   ◯ iOS
   ◯ Chrome 앱
   ```
   "데스크톱 앱" 선택 ⭐

5. **이름** 입력:
   ```
   이름: Local App
   ```

6. "만들기" 클릭

7. **OAuth 클라이언트 생성됨** 팝업:
   ```
   클라이언트 ID: XXX.apps.googleusercontent.com
   클라이언트 보안 비밀번호: GOCSPX-XXX
   ```
   "확인" 클릭 (이 정보는 나중에도 볼 수 있음)

---

### Step 6: client_secrets.json 다운로드

1. "사용자 인증 정보" 화면에서:
   ```
   OAuth 2.0 클라이언트 ID 섹션에
   "Local App" 항목 보임
   ```

2. 오른쪽 다운로드 아이콘 (↓) 클릭
   ```
   JSON 다운로드
   ```

3. 파일 다운로드됨:
   ```
   client_secret_XXXXX.apps.googleusercontent.com.json
   ```

4. **파일명 변경** ⭐ 중요!:
   ```
   변경 전: client_secret_XXXXX.apps.googleusercontent.com.json
   변경 후: client_secrets.json
   ```

5. 프로젝트 폴더로 이동:
   ```
   youtube-intelligence/
     └── client_secrets.json  ← 여기에 저장!
   ```

---

### Step 7: 설정 완료 확인

#### 체크리스트

```
✅ Google Cloud Console 접속
✅ 프로젝트 생성 (YouTube Intelligence)
✅ YouTube Data API v3 활성화
✅ YouTube Analytics API 활성화
✅ OAuth 동의 화면 구성
✅ 테스트 사용자 3명 추가
✅ OAuth 클라이언트 ID 생성 (데스크톱 앱)
✅ client_secrets.json 다운로드
✅ 파일명 변경 및 프로젝트 폴더에 저장
```

#### 파일 내용 확인

`client_secrets.json` 파일을 열어서 확인:

```json
{
  "installed": {
    "client_id": "XXXXX.apps.googleusercontent.com",
    "project_id": "youtube-intelligence-XXXXX",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-XXXXX",
    "redirect_uris": ["http://localhost"]
  }
}
```

**중요:**
- `"installed"` 키가 있어야 함 (데스크톱 앱)
- `"web"` 키가 있으면 잘못된 것 (웹 앱용)
- 잘못된 경우 → Step 5로 돌아가서 "데스크톱 앱" 재생성

---

## 다음 단계

### 로컬에서 OAuth 인증

```bash
# 가상환경 활성화 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install google-auth google-auth-oauthlib google-api-python-client

# POC 실행
python poc_setup.py        # 파일 확인
python poc_authenticate.py account1  # OAuth 인증
python poc_test_api.py account1      # API 테스트
```

---

## 문제 해결

### Q1: "OAuth 동의 화면" 메뉴가 안 보여요
**A:** 프로젝트가 선택되었는지 확인
- 상단에 "YouTube Intelligence" 프로젝트 선택됨
- 다른 프로젝트 선택되어 있으면 변경

### Q2: "앱이 차단됨" 오류
**A:** 테스트 사용자 추가 확인
- OAuth 동의 화면 → 테스트 사용자
- 해당 계정 이메일이 추가되어 있는지 확인
- 없으면 추가 후 다시 시도

### Q3: "redirect_uri_mismatch" 오류
**A:** OAuth 클라이언트 유형 확인
- "데스크톱 앱"으로 생성했는지 확인
- "웹 애플리케이션"으로 만들었다면 삭제 후 재생성

### Q4: client_secrets.json에 "web" 키가 있어요
**A:** 잘못된 유형으로 생성됨
- OAuth 클라이언트 ID 삭제
- Step 5로 돌아가서 "데스크톱 앱"으로 재생성

### Q5: API 활성화가 안 돼요
**A:** 프로젝트 선택 확인
- 올바른 프로젝트가 선택되었는지 확인
- 브라우저 새로고침

### Q6: "할당량 초과" 오류
**A:** 일일 할당량 10,000 units 확인
- API 및 서비스 → 할당량
- YouTube Data API v3 사용량 확인
- 다음날까지 대기 또는 할당량 증가 요청 (유료)

### Q7: 여러 프로젝트가 있어서 헷갈려요
**A:** 프로젝트명 명확히 구분
- 상단 프로젝트 선택기에서 "YouTube Intelligence" 선택
- 다른 프로젝트는 삭제 또는 무시

---

## 보안 주의사항

### ⚠️ client_secrets.json 관리

**절대 하지 말 것:**
- ❌ GitHub/Git에 커밋
- ❌ 공개 저장소에 업로드
- ❌ 이메일로 전송
- ❌ 클라우드 스토리지에 공개 업로드

**권장 사항:**
- ✅ 로컬 PC에만 보관
- ✅ `.gitignore`에 추가
- ✅ 백업 시 암호화
- ✅ 팀원과 공유 시 안전한 방법 (1Password, LastPass 등)

### .gitignore 추가

```gitignore
# OAuth 인증 정보
client_secrets.json
tokens/
*.json

# 환경 변수
.env

# 데이터베이스
*.db

# 로그
logs/
*.log
```

---

## 추가 리소스

### 공식 문서
- [Google Cloud Console](https://console.cloud.google.com)
- [YouTube API 문서](https://developers.google.com/youtube/v3)
- [OAuth 2.0 가이드](https://developers.google.com/identity/protocols/oauth2)

### 영상 가이드 (참고)
- Google Cloud Console 사용법: YouTube 검색 "Google Cloud Console tutorial"
- OAuth 설정: YouTube 검색 "OAuth 2.0 desktop app python"

### 도움받기
- [Stack Overflow - youtube-api 태그](https://stackoverflow.com/questions/tagged/youtube-api)
- [Google API Python Client GitHub](https://github.com/googleapis/google-api-python-client)

---

## 요약

### 핵심 단계 (빠른 참조)

```
1. console.cloud.google.com 접속
2. 프로젝트 생성: "YouTube Intelligence"
3. API 활성화:
   - YouTube Data API v3
   - YouTube Analytics API
4. OAuth 동의 화면:
   - 외부
   - 앱 이름: YouTube Intelligence
   - 테스트 사용자: 3개 계정 추가
5. OAuth 클라이언트 ID:
   - 유형: 데스크톱 앱
   - 이름: Local App
6. JSON 다운로드 → client_secrets.json
7. 프로젝트 폴더에 저장
8. 완료!
```

### 예상 소요 시간
- 처음: 15분
- 두 번째부터: 5분

---

**마지막 업데이트:** 2024-01-15
