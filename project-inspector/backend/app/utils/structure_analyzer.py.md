# `structure_analyzer.py` 파일 분석

## 1. 파일의 핵심 역할

이 파일은 Python 코드를 단순 텍스트가 아닌, **프로그래밍 언어 구조로 이해하고 분석**하는 가장 핵심적인 지능을 담당합니다. 파이썬의 내장 라이브러리인 `ast`(Abstract Syntax Tree, 추상 구문 트리)를 사용하여 코드의 구조(클래스, 함수, 임포트 등)를 파악하고, 이를 사람이 읽기 좋은 마크다운 형식으로 출력합니다.

- **해결하려는 문제**: 개발자가 프로젝트의 전체 또는 특정 파일의 구조를 한눈에 파악하기 어렵다는 문제를 해결합니다. 특히 다른 사람의 코드를 처음 분석하거나, 복잡한 프로젝트의 개요를 이해해야 할 때 매우 유용합니다.

## 2. 주요 구성 요소

### 가. 핵심 로직

- `analyze_structure(...)`: 외부에서 호출되는 메인 함수입니다. `file_path` 인자의 유무에 따라 단일 파일 분석 모드와 디렉토리 전체 분석 모드로 나뉩니다. `os.walk`를 사용해 효율적으로 `.py` 파일을 찾고, 각 파일을 `analyze_python_file` 함수로 넘겨 분석을 수행합니다.

- `analyze_python_file(content: str)`: 코드 문자열을 받아 `ast.parse()`를 통해 추상 구문 트리로 변환합니다. 그 후, 트리의 최상위 노드들을 순회하며 `class`, `function`, `import` 등 주요 구문들을 식별하고 각각의 상세 분석 함수(`extract_class_info`, `extract_function_info`)를 호출합니다.

- `format_file_structure(...)`: `analyze_python_file`이 반환한 분석 데이터(딕셔너리)를 받아, 최종적으로 사용자가 보게 될 마크다운 형식의 문자열로 이쁘게 가공합니다.

### 나. AST 분석 파트

- `extract_class_info(node: ast.ClassDef)`: `ClassDef` 노드를 받아 클래스 이름, 부모 클래스, 데코레이터, 내부에 정의된 메소드와 변수 정보를 추출합니다.

- `extract_function_info(node)`: `FunctionDef` 또는 `AsyncFunctionDef` 노드를 받아 함수 이름, 파라미터, 반환 타입, 데코레이터, 비동기 여부 등을 추출합니다. 이 함수의 가장 중요한 부분은 `CallVisitor`를 호출하여 함수 내부의 다른 함수 호출 관계를 분석하는 것입니다.

- `CallVisitor(ast.NodeVisitor)`: `ast.NodeVisitor`를 상속받아 만든 클래스로, 특정 함수의 AST를 순회(`visit`)하면서 모든 `Call` 노드(함수 호출 구문)를 찾아냅니다. 이를 통해 "`A` 함수가 `B`와 `C` 함수를 호출한다"와 같은 의존성 정보를 파악할 수 있습니다.

## 3. 다른 파일과의 연관성

- **`backend/app/main.py`**: `task_type`이 `analyze_structure` 또는 `analyze_file_structure`일 때, 이 파일의 `analyze_structure` 함수를 직접 호출합니다.
- **`backend/app/utils/constants.py`**: 파일 탐색 시 제외할 폴더 목록이 정의된 `EXCLUDE_DIRS` 상수를 `import`하여 사용합니다.

## 4. 종합 평가

`structure_analyzer.py`는 정규표현식(Regex)과 같은 부정확한 방법 대신 `ast`라는 올바른 도구를 사용하여 Python 코드 분석의 정확성과 안정성을 확보한 매우 잘 작성된 모듈입니다. 특히 `CallVisitor`를 통해 함수 간의 호출 관계까지 분석하는 부분은 이 프로젝트의 핵심적인 인텔리전스를 보여줍니다. 이 모듈 덕분에 "Project Inspector"는 단순 파일 병합 도구를 넘어, 코드에 대한 깊이 있는 통찰력을 제공하는 강력한 분석 도구로 거듭날 수 있습니다.
