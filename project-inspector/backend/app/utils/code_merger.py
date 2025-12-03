import os
from pathlib import Path
import io

from app.utils.constants import EXCLUDE_DIRS

MAX_FILE_SIZE = 1024 * 1024  # 1MB per file
MAX_TOTAL_SIZE = 10 * 1024 * 1024  # 10MB total

def merge_files(path: str, extension: str) -> str:
    root_path = Path(path)
    if not root_path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    output = io.StringIO()
    files_found = []
    failed_files = []
    total_size = 0
    skipped_large = 0

    for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for filename in filenames:
            if not filename.endswith(extension):
                continue

            file_path = Path(dirpath) / filename
            try:
                file_size = file_path.stat().st_size
                if file_size > MAX_FILE_SIZE:
                    skipped_large += 1
                    continue

                if total_size + file_size > MAX_TOTAL_SIZE:
                    output.write(f"\n# === Reached size limit. Processed {len(files_found)} files ===\n")
                    break

                relative_path = file_path.relative_to(root_path)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                header = f"\n# === File: {relative_path} ===\n\n"
                output.write(header)
                output.write(content)
                output.write('\n')

                files_found.append(str(relative_path))
                total_size += file_size

            except Exception as e:
                failed_files.append(f"{relative_path} (Error: {e})")
                continue

        if total_size > MAX_TOTAL_SIZE:
            break

    if not files_found:
        return f"No {extension} files found in the specified directory."

    result = output.getvalue()
    output.close()

    summary = f"# Merged {len(files_found)} {extension} files\n"
    summary += f"# Total size: {total_size / 1024:.1f} KB\n"
    if skipped_large > 0:
        summary += f"# Skipped {skipped_large} files larger than {MAX_FILE_SIZE // 1024}KB.\n"
    if failed_files:
        summary += f"# Failed to process {len(failed_files)} files:\n"
        for failed in failed_files:
            summary += f"# - {failed}\n"

    return summary + "\n" + result

def merge_python_files(path: str) -> str:
    return merge_files(path, '.py')

def merge_shell_files(path: str) -> str:
    return merge_files(path, '.sh')