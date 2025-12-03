# 🔍 Project Inspector 기술 문서

## 1. 프로젝트 개요 (Overview)

**Project Inspector**는 로컬 머신에 저장된 코드 프로젝트를 분석하고, 코드 병합 및 구조 시각화 등 개발자에게 유용한 기능을 제공하는 웹 기반 개발 보조 도구입니다.

사용자는 웹 UI를 통해 분석하고 싶은 프로젝트의 절대 경로를 입력하기만 하면, 복잡한 설정 없이 즉시 프로젝트에 대한 다양한 분석 결과를 얻을 수 있습니다. FastAPI로 구현된 강력한 백엔드와 SvelteKit으로 만들어진 직관적인 프론트엔드로 구성되어 있습니다.

## 2. 주요 기능 (Features)

- **코드 병합 (Code Merging)**
  - **Python 코드 병합**: 지정된 프로젝트 내의 모든 `.py` 파일을 찾아 하나의 텍스트 파일로 병합합니다.
  - **Shell 스크립트 병합**: 지정된 프로젝트 내의 모든 `.sh` 파일을 찾아 하나의 텍스트 파일로 병합합니다.

- **구조 분석 (Structure Analysis)**
  - **프로젝트 구조 분석**: 프로젝트 내 모든 Python 파일의 클래스와 함수 구조를 분석하여 마크다운 형식의 트리 구조로 시각화합니다.
  - **파일 구조 상세 분석**: 단일 Python 파일의 구조를 더 상세하게 분석합니다.
  - **함수 호출 관계 표시 (Show Calls)**: 구조 분석 시, 함수가 내부적으로 어떤 다른 함수들을 호출하는지 관계를 함께 표시하는 옵션을 제공합니다.

- **사용자 편의 기능 (User Experience)**
  - **WSL 경로 자동 변환**: Windows 사용자가 `C:\...` 형태의 경로를 입력하면, WSL(Linux용 Windows 하위 시스템) 환경에 맞는 `/mnt/c/...` 형태로 자동 변환하여 처리합니다.
  - **비동기 처리 및 타임아웃**: 대용량 프로젝트 분석 시 발생할 수 있는 지연에 대비하여, 모든 분석 작업은 비동기적으로 처리되며 일정 시간(기본 30초, 구조 분석 60초) 초과 시 타임아웃 처리되어 시스템 안정성을 보장합니다.
  - **실행 스크립트 제공**: `run.sh` 스크립트를 통해 한 번의 명령어로 백엔드와 프론트엔드 개발 서버를 동시에 실행할 수 있습니다.

## 3. 기술 스택 및 아키텍처 (Tech Stack & Architecture)

- **아키텍처**: 전형적인 SPA(Single Page Application) 구조
  - **Frontend (Client)**: 사용자의 입력을 받아 백엔드 API를 호출하고 결과를 표시합니다.
  - **Backend (Server)**: 실제 프로젝트 분석 로직을 수행하는 API 서버 역할을 합니다.

- **기술 스택**:
  - **Backend**:
    - **Framework**: FastAPI
    - **Web Server**: Uvicorn
    - **Dependencies**: Pydantic (데이터 유효성 검사)
    - **Language**: Python
  - **Frontend**:
    - **Framework**: SvelteKit
    - **Build Tool**: Vite
    - **Language**: JavaScript, HTML, CSS
  - **Development Environment**:
    - **Virtual Environment**: `venv` (Python)
    - **Package Manager**: `npm` (Node.js)

## 4. 프로젝트 파일 구조 (File Structure)

```
project-inspector/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 앱, API 엔드포인트 정의
│   │   └── utils/
│   │       ├── code_merger.py   # 코드 병합 로직
│   │       └── structure_analyzer.py # 구조 분석 로직
│   └── requirements.txt         # Python 의존성 목록
│
├── frontend/
│   ├── src/
│   │   └── routes/
│   │       └── +page.svelte     # 메인 UI 컴포넌트
│   └── package.json             # Node.js 의존성 및 스크립트
│
├── run.sh                       # 개발 서버 동시 실행 스크립트
├── project_documentation.md     # 본 기술 문서
└── README.md                    # 기본 프로젝트 소개
```

## 5. 설치 및 실행 (Setup and Running)

프로젝트를 실행하는 방법은 두 가지가 있습니다.

### 방법 1: `run.sh` 스크립트로 한 번에 실행 (권장)

Linux 또는 WSL 환경에서 아래 명령어를 실행하면 백엔드와 프론트엔드 서버가 동시에 구동됩니다.

```bash
# 스크립트에 실행 권한 부여
chmod +x run.sh

# 스크립트 실행
./run.sh
```
- **Frontend**: `http://localhost:5173`
- **Backend**: `http://localhost:8000`

### 방법 2: 수동으로 각각 실행

두 개의 터미널을 열고 각각 백엔드와 프론트엔드 서버를 실행합니다.

**터미널 1: Backend 실행**
```bash
cd backend
# 가상환경 활성화
source ../venv/bin/activate
# 의존성 설치
pip install -r requirements.txt
# FastAPI 서버 실행
uvicorn app.main:app --reload
```

**터미널 2: Frontend 실행**
```bash
cd frontend
# 의존성 설치
npm install
# SvelteKit 개발 서버 실행
npm run dev
```

## 6. API 명세 (API Endpoint Details)

### `POST /api/process`

프로젝트 분석을 요청하고 결과를 반환합니다.

- **Request Body**:
  ```json
  {
    "path": "string",
    "task_type": "string",
    "file_path": "string | null",
    "show_calls": "boolean | null"
  }
  ```
  - `path` (필수): 분석할 프로젝트의 로컬 절대 경로
  - `task_type` (필수): 수행할 작업의 종류
    - `"merge_py"`: Python 코드 병합
    - `"merge_sh"`: Shell 스크립트 병합
    - `"analyze_structure"`: 프로젝트 전체 구조 분석
    - `"analyze_file_structure"`: 단일 파일 구조 분석
  - `file_path` (선택): `task_type`이 `analyze_file_structure`일 때, 프로젝트 경로 기준의 상대 파일 경로
  - `show_calls` (선택): `task_type`이 `analyze_structure`일 때, 함수 호출 관계 표시 여부 (기본값: `false`)

- **Success Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": "분석 결과 문자열",
    "converted_path": "변환된 WSL 경로 (해당 시)"
  }
  ```

- **Error Response (200 OK)**:
  ```json
  {
    "success": false,
    "error": "에러 메시지",
    "converted_path": null
  }
  ```

## 7. 사용 방법 (How to Use)

1.  웹 브라우저에서 프론트엔드 주소(`http://localhost:5173`)에 접속합니다.
2.  **프로젝트 경로** 입력 필드에 분석하고 싶은 프로젝트의 절대 경로를 입력합니다.
3.  **작업 선택** 드롭다운 메뉴에서 원하는 분석 작업을 선택합니다.
    - '파일 구조 분석' 선택 시, 상세 분석할 파일의 상대 경로를 추가로 입력할 수 있습니다.
    - '프로젝트 구조 분석' 선택 시, '함수 호출 정보 표시' 체크박스로 옵션을 선택할 수 있습니다.
4.  **실행** 버튼을 클릭합니다.
5.  잠시 기다리면 아래 **결과** 란에 분석 내용이 나타납니다.
6.  **복사** 버튼을 눌러 결과를 클립보드에 저장할 수 있습니다.
