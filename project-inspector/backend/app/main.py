from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Optional
import traceback
import re
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import functools

from app.utils.code_merger import merge_python_files, merge_shell_files
from app.utils.structure_analyzer import analyze_structure

app = FastAPI(title="Project Inspector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessRequest(BaseModel):
    path: str
    task_type: Literal["merge_py", "merge_sh", "analyze_structure", "analyze_file_structure"]
    file_path: Optional[str] = None  # For file-specific structure analysis
    show_calls: Optional[bool] = False  # For showing function calls in structure analysis

class ProcessResponse(BaseModel):
    success: bool
    data: Optional[str] = None
    error: Optional[str] = None
    converted_path: Optional[str] = None

def convert_windows_to_wsl_path(path: str) -> str:
    """Convert Windows path to WSL path if needed"""
    # Check if it's a Windows path (C:\ or D:\ etc.)
    windows_path_pattern = r'^[A-Za-z]:\\.*'
    
    if re.match(windows_path_pattern, path):
        # Replace C:\ with /mnt/c/, D:\ with /mnt/d/, etc.
        drive_letter = path[0].lower()
        wsl_path = f"/mnt/{drive_letter}{path[2:]}"
        # Replace backslashes with forward slashes
        wsl_path = wsl_path.replace('\\', '/')
        return wsl_path
    
    # Check if it's already a valid path or needs no conversion
    return path

# Create a thread pool executor
executor = ThreadPoolExecutor(max_workers=2)

async def run_with_timeout(func, *args, timeout_seconds=30):
    """Run a blocking function with timeout in thread pool"""
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(executor, func, *args)
    try:
        result = await asyncio.wait_for(future, timeout=timeout_seconds)
        return result
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")

# --- Refactoring Start ---

def _run_merge_py(path, **kwargs):
    return merge_python_files(path)

def _run_merge_sh(path, **kwargs):
    return merge_shell_files(path)

def _run_analyze_structure(path, show_calls=False, **kwargs):
    return analyze_structure(path, show_calls=show_calls)

def _run_analyze_file_structure(path, file_path, **kwargs):
    if not file_path:
        raise ValueError("file_path is required for analyze_file_structure task")
    return analyze_structure(path, file_path=file_path)

# Task dispatcher using a dictionary (Strategy Pattern)
TASK_DISPATCHER = {
    "merge_py": {
        "func": _run_merge_py,
        "timeout": 30
    },
    "merge_sh": {
        "func": _run_merge_sh,
        "timeout": 30
    },
    "analyze_structure": {
        "func": _run_analyze_structure,
        "timeout": 60
    },
    "analyze_file_structure": {
        "func": _run_analyze_file_structure,
        "timeout": 60
    }
}

# --- Refactoring End ---

@app.post("/api/process", response_model=ProcessResponse)
async def process_project(request: ProcessRequest):
    try:
        original_path = request.path
        converted_path = convert_windows_to_wsl_path(original_path)

        if not os.path.exists(converted_path):
            return ProcessResponse(
                success=False,
                error=f"Path does not exist: {converted_path}" +
                      (f" (converted from: {original_path})" if original_path != converted_path else "")
            )

        task = TASK_DISPATCHER.get(request.task_type)
        if not task:
            raise ValueError(f"Unknown task type: {request.task_type}")

        try:
            # Dynamically call the function based on the task type
            result = await run_with_timeout(
                task["func"],
                path=converted_path,
                file_path=request.file_path,
                show_calls=request.show_calls,
                timeout_seconds=task["timeout"]
            )
        except TimeoutError:
            return ProcessResponse(
                success=False,
                error=f"처리 시간이 너무 오래 걸립니다. (제한시간: {task['timeout']}초)"
            )

        return ProcessResponse(
            success=True,
            data=result,
            converted_path=converted_path if original_path != converted_path else None
        )

    except ValueError as e:
        return ProcessResponse(success=False, error=str(e))
    except Exception as e:
        # For security, log the full error to the server console instead of sending it to the client
        print(f"An unexpected error occurred: {e}\n{traceback.format_exc()}")
        return ProcessResponse(success=False, error="서버 내부에서 예상치 못한 오류가 발생했습니다.")

@app.get("/")
async def root():
    return {"message": "Project Inspector API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}