#!/usr/bin/env python3
"""Test script for function call analysis feature."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.structure_analyzer import analyze_python_file

test_code = '''
import os
import json
from pathlib import Path

def process_data(file_path):
    """Process data from a file."""
    # Simple function call
    print("Processing file:", file_path)
    
    # Attribute call
    data = json.loads(read_file(file_path))
    
    # Nested attribute call
    full_path = os.path.join("/home", "user", file_path)
    
    # Method call on object
    path_obj = Path(full_path)
    exists = path_obj.exists()
    
    # Built-in function
    length = len(data)
    
    return data

def read_file(path):
    """Read file contents."""
    with open(path, 'r') as f:
        return f.read()

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def load_data(self, source):
        """Load data from source."""
        # Method calls
        self.validate_source(source)
        raw_data = self.fetch_data(source)
        
        # External function call
        processed = process_data(raw_data)
        
        # Built-in and module calls
        print(f"Loaded {len(processed)} items")
        json.dumps(processed)
        
        return processed
    
    def validate_source(self, source):
        """Validate the data source."""
        pass
    
    def fetch_data(self, source):
        """Fetch raw data."""
        pass
'''

# Analyze the test code
result = analyze_python_file(test_code)

print("=== Function Call Analysis Test Results ===\n")

# Display module-level functions
for func in result['functions']:
    print(f"Function: {func['name']}")
    if func['calls']:
        print("  Calls:")
        for call in func['calls']:
            print(f"    - {call['name']} (from {call['source']})")
    else:
        print("  No function calls detected")
    print()

# Display class methods
for cls in result['classes']:
    print(f"Class: {cls['name']}")
    for method in cls['methods']:
        print(f"  Method: {method['name']}")
        if method['calls']:
            print("    Calls:")
            for call in method['calls']:
                print(f"      - {call['name']} (from {call['source']})")
        else:
            print("    No function calls detected")
    print()