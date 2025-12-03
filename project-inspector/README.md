# Project Inspector

로컬 코드 프로젝트를 분석하는 웹 애플리케이션입니다.

## 기능

- **Python 코드 병합**: 프로젝트 내 모든 `.py` 파일을 하나의 파일로 병합
- **Shell 스크립트 병합**: 프로젝트 내 모든 `.sh` 파일을 하나의 파일로 병합  
- **프로젝트 구조 분석**: Python 프로젝트의 클래스와 함수 구조를 마크다운 형식으로 분석

## 설치 및 실행

### Backend 설정

1. Backend 디렉토리로 이동:
```bash
cd backend
```

2. Python 가상환경 생성 및 활성화 (선택사항):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

4. FastAPI 서버 실행:
```bash
uvicorn app.main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

### Frontend 설정

1. Frontend 디렉토리로 이동:
```bash
cd frontend
```

2. 의존성 설치:
```bash
npm install
```

3. 개발 서버 실행:
```bash
npm run dev
```

웹 애플리케이션은 `http://localhost:5173`에서 실행됩니다.

## 사용 방법

1. 웹 브라우저에서 `http://localhost:5173` 접속
2. 분석할 프로젝트의 절대 경로 입력 (예: `/home/user/myproject`)
3. 작업 유형 선택:
   - Python 코드 합치기
   - Shell 스크립트 합치기
   - 프로젝트 구조 분석
4. "실행" 버튼 클릭
5. 결과 확인 및 필요시 클립보드에 복사

## API 엔드포인트

### POST /api/process

프로젝트 분석 요청을 처리합니다.

**Request Body:**
```json
{
  "path": "/path/to/project",
  "task_type": "merge_py" | "merge_sh" | "analyze_structure"
}
```

**Response:**
```json
{
  "success": true,
  "data": "처리 결과 문자열"
}
```

## 프로젝트 구조

```
project-inspector/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 앱 및 API 엔드포인트
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── code_merger.py   # 파일 병합 로직
│   │       └── structure_analyzer.py # 구조 분석 로직
│   ├── requirements.txt         # Python 의존성
│   └── .gitignore
│
├── frontend/                    # SvelteKit 프로젝트
│   ├── src/
│   │   ├── app.html
│   │   └── routes/
│   │       └── +page.svelte     # 메인 UI 컴포넌트
│   ├── static/
│   │   └── favicon.png
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.js
│   └── .gitignore
│
└── README.md
```

## 주의사항

- 분석 시 `__pycache__`, `.git`, `venv`, `.venv`, `node_modules` 폴더는 자동으로 제외됩니다.
- 큰 프로젝트의 경우 처리 시간이 오래 걸릴 수 있습니다.
- 파일 읽기 권한이 있는 경로만 분석 가능합니다.