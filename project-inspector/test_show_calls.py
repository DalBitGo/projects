#!/usr/bin/env python3
"""Test the show_calls functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.structure_analyzer import analyze_structure

# Test with show_calls=False (default behavior)
print("=== Without show_calls (기본 동작) ===")
result_without = analyze_structure('.', 'backend/app/main.py', show_calls=False)
print(result_without[:1000])
print("\n" + "="*50 + "\n")

# Test with show_calls=True (new functionality)
print("=== With show_calls=True (함수 호출 정보 표시) ===")
result_with = analyze_structure('.', 'backend/app/main.py', show_calls=True)
print(result_with[:1000])
print("\n" + "="*50 + "\n")

# Test with a simple example
test_code = '''
import json

def simple_function():
    data = json.loads('{"key": "value"}')
    print("Hello World")
    return data
'''

# Create temporary file and test
with open('/tmp/test_example.py', 'w') as f:
    f.write(test_code)

print("=== Simple example without calls ===")
from app.utils.structure_analyzer import analyze_python_file, format_file_structure
file_structure = analyze_python_file(test_code)
result_no_calls = format_file_structure("test.py", file_structure, detailed=False, show_calls=False)
print(result_no_calls)

print("=== Simple example with calls ===")
result_with_calls = format_file_structure("test.py", file_structure, detailed=False, show_calls=True)
print(result_with_calls)