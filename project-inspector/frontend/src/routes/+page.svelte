<script>
  let projectPath = '';
  let taskType = 'merge_py';
  let filePath = '';
  let showCalls = false;
  let resultText = '';
  let isLoading = false;
  let errorMessage = '';
  let infoMessage = '';
  let convertedPath = '';

  const taskOptions = [
    { value: 'merge_py', label: 'Python 코드 합치기' },
    { value: 'merge_sh', label: 'Shell 스크립트 합치기' },
    { value: 'analyze_structure', label: '프로젝트 구조 분석' },
    { value: 'analyze_file_structure', label: '파일 구조 분석 (상세)' }
  ];

  function isWindowsPath(path) {
    return /^[A-Za-z]:\\/.test(path);
  }

  function previewWslPath(path) {
    if (isWindowsPath(path)) {
      const driveLetter = path[0].toLowerCase();
      return `/mnt/${driveLetter}${path.substring(2).replace(/\\/g, '/')}`;
    }
    return path;
  }

  $: {
    if (isWindowsPath(projectPath)) {
      convertedPath = previewWslPath(projectPath);
      infoMessage = `Windows 경로가 자동으로 변환됩니다: ${convertedPath}`;
    } else {
      convertedPath = '';
      infoMessage = '';
    }
  }

  async function processProject() {
    if (!projectPath.trim()) {
      errorMessage = '프로젝트 경로를 입력해주세요.';
      return;
    }

    isLoading = true;
    errorMessage = '';
    resultText = '';

    // --- Refactoring Start ---
    // API URL을 환경 변수로 관리하는 것을 권장하지만, 우선 중복 로직을 제거합니다.
    const API_BASE_URL = 'http://localhost:8000';

    try {
      const body = {
        path: projectPath,
        task_type: taskType,
        file_path: taskType === 'analyze_file_structure' ? filePath : undefined,
        show_calls: taskType === 'analyze_structure' ? showCalls : undefined,
      };

      const response = await fetch(`${API_BASE_URL}/api/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });
      // --- Refactoring End ---

      const data = await response.json();

      if (data.success) {
        resultText = data.data;
        errorMessage = '';
        if (data.converted_path) {
          infoMessage = `✅ Windows 경로가 자동 변환되었습니다: ${data.converted_path}`;
        }
      } else {
        errorMessage = data.error || '처리 중 오류가 발생했습니다.';
        resultText = '';
      }
    } catch (error) {
      errorMessage = `서버 연결 실패: ${error.message}`;
      resultText = '';
    } finally {
      isLoading = false;
    }
  }

  function clearResults() {
    resultText = '';
    errorMessage = '';
    infoMessage = isWindowsPath(projectPath) ? infoMessage : '';
  }
</script>

<style>
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  }

  h1 {
    color: #333;
    margin-bottom: 2rem;
  }

  .control-panel {
    background: #f5f5f5;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 2rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #555;
  }

  input[type="text"] {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    box-sizing: border-box;
  }

  input[type="text"]:focus {
    outline: none;
    border-color: #4CAF50;
  }

  select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    background: white;
    cursor: pointer;
  }

  select:focus {
    outline: none;
    border-color: #4CAF50;
  }

  input[type="checkbox"] {
    margin-right: 0.5rem;
    transform: scale(1.2);
  }

  label:has(input[type="checkbox"]) {
    display: flex;
    align-items: center;
    cursor: pointer;
  }

  .button-group {
    display: flex;
    gap: 1rem;
  }

  button {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  .btn-primary {
    background: #4CAF50;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: #45a049;
  }

  .btn-secondary {
    background: #757575;
    color: white;
  }

  .btn-secondary:hover {
    background: #616161;
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .result-section {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1.5rem;
  }

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  h2 {
    color: #333;
    margin: 0;
  }

  textarea {
    width: 100%;
    min-height: 400px;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.9rem;
    resize: vertical;
    box-sizing: border-box;
  }

  .loading-message {
    color: #2196F3;
    font-weight: 600;
    padding: 1rem;
    text-align: center;
  }

  .error-message {
    background: #ffebee;
    color: #c62828;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .success-message {
    background: #e8f5e9;
    color: #2e7d32;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .info-message {
    background: #e3f2fd;
    color: #1565c0;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    margin-top: 0.5rem;
    font-size: 0.9rem;
  }

  .copy-button {
    background: #2196F3;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .copy-button:hover {
    background: #1976D2;
  }
</style>

<div class="container">
  <h1>🔍 Project Inspector</h1>
  
  <div class="control-panel">
    <div class="form-group">
      <label for="path-input">프로젝트 경로 (절대 경로)</label>
      <input 
        id="path-input"
        type="text" 
        bind:value={projectPath}
        placeholder="예: /home/user/myproject 또는 C:\Users\myproject"
        disabled={isLoading}
      />
      {#if infoMessage && !errorMessage && !resultText}
        <div class="info-message">
          ℹ️ {infoMessage}
        </div>
      {/if}
    </div>

    {#if taskType === 'analyze_file_structure'}
    <div class="form-group">
      <label for="file-input">파일 경로 (프로젝트 경로 기준 상대 경로)</label>
      <input 
        id="file-input"
        type="text" 
        bind:value={filePath}
        placeholder="예: src/main.py 또는 backend/app/models.py"
        disabled={isLoading}
      />
    </div>
    {/if}

    <div class="form-group">
      <label for="task-select">작업 선택</label>
      <select id="task-select" bind:value={taskType} disabled={isLoading}>
        {#each taskOptions as option}
          <option value={option.value}>{option.label}</option>
        {/each}
      </select>
    </div>

    {#if taskType === 'analyze_structure'}
    <div class="form-group">
      <label>
        <input 
          type="checkbox" 
          bind:checked={showCalls}
          disabled={isLoading}
        />
        함수 호출 정보 표시
      </label>
    </div>
    {/if}

    <div class="button-group">
      <button 
        class="btn-primary"
        on:click={processProject} 
        disabled={isLoading}
      >
        {isLoading ? '처리 중...' : '실행'}
      </button>
      <button 
        class="btn-secondary"
        on:click={clearResults}
        disabled={isLoading}
      >
        결과 지우기
      </button>
    </div>
  </div>

  {#if infoMessage && resultText}
    <div class="info-message">
      {infoMessage}
    </div>
  {/if}

  {#if errorMessage}
    <div class="error-message">
      ⚠️ {errorMessage}
    </div>
  {/if}

  {#if isLoading}
    <div class="loading-message">
      처리 중입니다. 잠시만 기다려주세요...
    </div>
  {/if}

  {#if resultText}
    <div class="result-section">
      <div class="result-header">
        <h2>📄 결과</h2>
        <button 
          class="copy-button"
          on:click={() => {
            navigator.clipboard.writeText(resultText);
            alert('클립보드에 복사되었습니다!');
          }}
        >
          📋 복사
        </button>
      </div>
      <textarea readonly value={resultText}></textarea>
    </div>
  {/if}
</div>