# `main.py` 파일 분석

## 1. 파일의 핵심 역할

이 파일은 **프로젝트의 메인 API 서버** 역할을 합니다. FastAPI 프레임워크를 사용하여 웹 서버를 구축하고, 프론트엔드로부터 들어오는 모든 분석 요청을 받아 처리하는 관문(Gateway)입니다.

- **해결하려는 문제**: 프론트엔드(웹 브라우저)와 순수 Python으로 작성된 분석 유틸리티(`code_merger`, `structure_analyzer`) 사이의 다리 역할을 합니다. HTTP 프로토콜을 통해 외부에서 안전하게 내부 분석 기능을 호출할 수 있도록 해줍니다.

## 2. 주요 구성 요소

### 가. FastAPI 애플리케이션 설정

- `app = FastAPI(...)`: FastAPI 앱 인스턴스를 생성합니다.
- `app.add_middleware(CORSMiddleware, ...)`: 프론트엔드 개발 서버(`localhost:5173`)와 통신할 수 있도록 CORS(Cross-Origin Resource Sharing) 정책을 설정합니다.

### 나. 데이터 모델 (Pydantic Models)

- `ProcessRequest`: API 요청 시 받아들일 데이터의 형식을 정의합니다. `path`, `task_type` 등의 필드를 지정하여, FastAPI가 자동으로 들어오는 요청의 유효성을 검사하도록 합니다.
- `ProcessResponse`: API가 프론트엔드로 응답할 데이터의 형식을 정의합니다. `success`, `data`, `error` 필드를 통해 일관된 응답 구조를 유지합니다.

### 다. 핵심 API 엔드포인트

- `@app.post("/api/process")`: `/api/process` 경로로 들어오는 POST 요청을 처리하는 메인 핸들러입니다.
- `async def process_project(request: ProcessRequest)`: 요청을 받아 실제 분석을 수행하는 비동기 함수입니다.
    - **경로 변환**: `convert_windows_to_wsl_path` 함수를 호출하여 Windows 경로를 WSL 경로로 변환합니다.
    - **작업 분배 (Dispatcher)**: `TASK_DISPATCHER` 딕셔너리를 사용해 `task_type`에 맞는 실제 분석 함수를 찾아 실행합니다. (이전의 `if/elif` 구조에서 리팩토링됨)
    - **타임아웃 처리**: `run_with_timeout` 함수로 분석 함수를 감싸, 정해진 시간(30초/60초) 내에 작업이 끝나지 않으면 타임아웃 오류를 반환하여 서버 전체가 멈추는 것을 방지합니다.
    - **오류 처리**: `try-except` 블록을 통해 경로가 존재하지 않거나, 타임아웃이 발생하거나, 기타 예상치 못한 서버 내부 오류가 발생했을 때 일관된 `ProcessResponse` 형식으로 에러를 반환합니다.

## 3. 다른 파일과의 연관성

- **`frontend/src/routes/+page.svelte`**: 이 파일의 `fetch` 요청을 직접적으로 받아 처리하는 서버입니다.
- **`backend/app/utils/code_merger.py`**: `task_type`이 `merge_py` 또는 `merge_sh`일 때, 이 파일의 `merge_python_files`, `merge_shell_files` 함수를 호출합니다.
- **`backend/app/utils/structure_analyzer.py`**: `task_type`이 `analyze_structure` 또는 `analyze_file_structure`일 때, 이 파일의 `analyze_structure` 함수를 호출합니다.
- **`backend/app/utils/constants.py`**: 직접적인 연관은 없지만, `main.py`가 호출하는 유틸리티 함수들이 이 파일의 `EXCLUDE_DIRS` 상수를 사용합니다.

## 4. 종합 평가

`main.py`는 API 서버의 컨트롤 타워로서, 요청 유효성 검사, 작업 분배, 비동기 처리, 오류 핸들링 등 웹 서버가 갖춰야 할 핵심적인 기능들을 잘 구현하고 있습니다. 특히 `TASK_DISPATCHER`를 사용한 구조는 새로운 분석 기능이 추가되더라도 유연하게 확장할 수 있는 좋은 설계입니다.
