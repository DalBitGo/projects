# Shared constants for the utils package

EXCLUDE_DIRS: set[str] = {
    '__pycache__', 
    '.git', 
    'venv', 
    '.venv', 
    'node_modules', 
    'env', 
    '.env', 
    '.tox', 
    'dist', 
    'build', 
    '*.egg-info'
}
