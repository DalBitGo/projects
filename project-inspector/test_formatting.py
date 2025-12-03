#!/usr/bin/env python3
"""Test the formatted output with function calls."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.structure_analyzer import analyze_python_file, format_file_structure

test_code = '''
import json
from utils.structure_analyzer import analyze_structure
from utils.code_merger import merge_code

def process_project(request: ProcessRequest):
    """Process a project request."""
    result = run_with_timeout(lambda: analyze_structure(request.path))
    data = json.loads(result)
    return merge_code(data)

def run_with_timeout(func, timeout=30):
    """Run a function with timeout."""
    return func()

class ProjectManager:
    def analyze(self, path: str):
        """Analyze a project."""
        self.validate_path(path)
        structure = analyze_structure(path)
        merged = merge_code(structure)
        print(f"Analysis complete for {path}")
        return merged
    
    def validate_path(self, path):
        """Validate the given path."""
        if not path:
            raise ValueError("Path cannot be empty")
'''

# Analyze the test code
file_structure = analyze_python_file(test_code)

# Format with detailed=True to see the calls
formatted_output = format_file_structure("example.py", file_structure, detailed=True)

print("=== Formatted Output with Function Calls ===\n")
print(formatted_output)