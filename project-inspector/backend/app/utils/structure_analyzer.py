import ast
import os
from pathlib import Path
from app.utils.constants import EXCLUDE_DIRS

def analyze_structure(path: str, file_path: Optional[str] = None, show_calls: bool = False) -> str:
    """
    Analyze Python code structure.

    Args:
        path: Root directory path
        file_path: Optional specific file path relative to root for single file analysis
        show_calls: Whether to show function calls in the output
    """
    root_path = Path(path)
    if not root_path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    structure_data = []
    failed_files = []

    if file_path:
        # Single file analysis logic remains the same
        full_file_path = root_path / file_path
        if not full_file_path.exists():
            raise ValueError(f"File does not exist: {full_file_path}")
        if full_file_path.suffix != '.py':
            raise ValueError(f"File is not a Python file: {full_file_path}")
        
        try:
            with open(full_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            file_structure = analyze_python_file(content)
            structure_entry = format_file_structure(file_path, file_structure, detailed=True, show_calls=show_calls)
            if structure_entry:
                structure_data.append(structure_entry)
        except Exception as e:
            failed_files.append(f"{file_path} (Error: {e})")
    else:
        # Use os.walk for efficient directory traversal
        for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

            for filename in filenames:
                if not filename.endswith(".py"):
                    continue

                current_file_path = Path(dirpath) / filename
                relative_path = current_file_path.relative_to(root_path)
                try:
                    with open(current_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    file_structure = analyze_python_file(content)
                    structure_entry = format_file_structure(str(relative_path), file_structure, detailed=False, show_calls=show_calls)
                    if structure_entry:
                        structure_data.append(structure_entry)
                except Exception as e:
                    failed_files.append(f"{relative_path} (Error: {e})")
                    continue

    if not structure_data and not failed_files:
        return "No Python files found or no classes/functions detected."

    summary = f"# Analyzed {len(structure_data)} Python files.\n"
    if failed_files:
        summary += f"# Failed to analyze {len(failed_files)} files:\n"
        for failed in failed_files:
            summary += f"# - {failed}\n"
    
    return summary + "\n" + '\n'.join(structure_data)

def format_file_structure(file_path: str, file_structure: Dict[str, Any], detailed: bool = False, show_calls: bool = False) -> str:
    """Format file structure for display."""
    if not file_structure['classes'] and not file_structure['functions']:
        return ""
    
    structure_entry = f"## {file_path}\n"
    
    # Add imports if detailed mode
    if detailed and file_structure.get('imports'):
        structure_entry += "### Imports:\n"
        for imp in file_structure['imports']:
            structure_entry += f"- {imp}\n"
        structure_entry += "\n"
    
    # Add global variables if detailed mode
    if detailed and file_structure.get('global_vars'):
        structure_entry += "### Global Variables:\n"
        for var in file_structure['global_vars']:
            structure_entry += f"- {var}\n"
        structure_entry += "\n"
    
    # Add classes
    for class_info in file_structure['classes']:
        structure_entry += f"- class {class_info['name']}"
        if class_info.get('bases'):
            bases = ', '.join(class_info['bases'])
            structure_entry += f"({bases})"
        structure_entry += ":\n"
        
        # Add class variables if detailed
        if detailed and class_info.get('class_vars'):
            for var in class_info['class_vars']:
                structure_entry += f"  - {var} (class variable)\n"
        
        # Add methods
        for method in class_info['methods']:
            params = ', '.join(method['params'])
            decorator_prefix = ""
            if method.get('decorators'):
                decorator_prefix = f"[{', '.join(method['decorators'])}] "
            async_prefix = "async " if method.get('is_async') else ""
            structure_entry += f"  - {decorator_prefix}{async_prefix}def {method['name']}({params})"
            if detailed and method.get('return_type'):
                structure_entry += f" -> {method['return_type']}"
            structure_entry += "\n"
            
            # Add function calls if present and either detailed mode or show_calls is enabled
            if (detailed or show_calls) and method.get('calls'):
                structure_entry += "    - calls:\n"
                for call in method['calls']:
                    if call['source'] == 'self':
                        structure_entry += f"      - {call['name']}\n"
                    else:
                        structure_entry += f"      - {call['name']} (from: {call['source']})\n"
    
    # Add module-level functions
    for func in file_structure['functions']:
        params = ', '.join(func['params'])
        decorator_prefix = ""
        if func.get('decorators'):
            decorator_prefix = f"[{', '.join(func['decorators'])}] "
        async_prefix = "async " if func.get('is_async') else ""
        structure_entry += f"- {decorator_prefix}{async_prefix}def {func['name']}({params})"
        if detailed and func.get('return_type'):
            structure_entry += f" -> {func['return_type']}"
        structure_entry += "\n"
        
        # Add function calls if present and either detailed mode or show_calls is enabled
        if (detailed or show_calls) and func.get('calls'):
            structure_entry += "  - calls:\n"
            for call in func['calls']:
                if call['source'] == 'self':
                    structure_entry += f"    - {call['name']}\n"
                else:
                    structure_entry += f"    - {call['name']} (from: {call['source']})\n"
    
    return structure_entry

def analyze_python_file(content: str) -> Dict[str, Any]:
    """Analyze a Python file and extract its structure."""
    result = {
        'imports': [],
        'global_vars': [],
        'classes': [],
        'functions': []
    }
    
    try:
        tree = ast.parse(content)
    except:
        return result
    
    # Process top-level nodes only (not using ast.walk which flattens everything)
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # Extract imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result['imports'].append(f"import {alias.name}")
            else:
                module = node.module or ''
                for alias in node.names:
                    result['imports'].append(f"from {module} import {alias.name}")
        
        elif isinstance(node, ast.Assign):
            # Extract global variables
            for target in node.targets:
                if isinstance(target, ast.Name):
                    result['global_vars'].append(target.id)
        
        elif isinstance(node, ast.ClassDef):
            # Extract class information
            class_info = extract_class_info(node)
            result['classes'].append(class_info)
        
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Extract module-level function information
            func_info = extract_function_info(node)
            result['functions'].append(func_info)
    
    return result

def extract_class_info(node: ast.ClassDef) -> Dict[str, Any]:
    """Extract information from a class definition."""
    class_info = {
        'name': node.name,
        'bases': [],
        'decorators': [],
        'class_vars': [],
        'methods': []
    }
    
    # Extract base classes
    for base in node.bases:
        if isinstance(base, ast.Name):
            class_info['bases'].append(base.id)
        elif isinstance(base, ast.Attribute):
            class_info['bases'].append(ast.unparse(base))
    
    # Extract decorators
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name):
            class_info['decorators'].append(decorator.id)
        elif isinstance(decorator, ast.Attribute):
            class_info['decorators'].append(ast.unparse(decorator))
        elif isinstance(decorator, ast.Call):
            class_info['decorators'].append(ast.unparse(decorator))
    
    # Process class body
    for item in node.body:
        if isinstance(item, ast.Assign):
            # Class variables
            for target in item.targets:
                if isinstance(target, ast.Name):
                    class_info['class_vars'].append(target.id)
        
        elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Methods
            method_info = extract_function_info(item)
            class_info['methods'].append(method_info)
    
    return class_info

def extract_function_info(node) -> Dict[str, Any]:
    """Extract information from a function/method definition."""
    func_info = {
        'name': node.name,
        'params': [],
        'decorators': [],
        'is_async': isinstance(node, ast.AsyncFunctionDef),
        'return_type': None,
        'calls': []  # List of CalledFunction dictionaries
    }
    
    # Extract parameters
    for arg in node.args.args:
        param = arg.arg
        if arg.annotation:
            param += f": {ast.unparse(arg.annotation)}"
        func_info['params'].append(param)
    
    # Handle *args
    if node.args.vararg:
        param = f"*{node.args.vararg.arg}"
        if node.args.vararg.annotation:
            param += f": {ast.unparse(node.args.vararg.annotation)}"
        func_info['params'].append(param)
    
    # Handle **kwargs
    if node.args.kwarg:
        param = f"**{node.args.kwarg.arg}"
        if node.args.kwarg.annotation:
            param += f": {ast.unparse(node.args.kwarg.annotation)}"
        func_info['params'].append(param)
    
    # Extract decorators
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name):
            func_info['decorators'].append(decorator.id)
        elif isinstance(decorator, ast.Attribute):
            func_info['decorators'].append(ast.unparse(decorator))
        elif isinstance(decorator, ast.Call):
            # Extract decorator name from Call
            if isinstance(decorator.func, ast.Name):
                func_info['decorators'].append(decorator.func.id)
            else:
                func_info['decorators'].append(ast.unparse(decorator.func))
    
    # Extract return type annotation
    if node.returns:
        func_info['return_type'] = ast.unparse(node.returns)
    
    # Extract function calls from the function body
    visitor = CallVisitor()
    visitor.visit(node)
    
    # Convert the set of calls to a list of CalledFunction dictionaries
    func_info['calls'] = [
        {'name': name, 'source': source}
        for name, source in sorted(visitor.calls)
    ]
    
    return func_info


class CallVisitor(ast.NodeVisitor):
    """AST visitor to extract function calls from a function body."""
    
    def __init__(self):
        """Initialize the visitor with an empty set of calls."""
        self.calls: set = set()
    
    def visit_Call(self, node: ast.Call) -> None:
        """Extract function call information.
        
        This method will extract the name and source of function calls.
        """
        if isinstance(node.func, ast.Name):
            # Simple function call like my_func()
            name = node.func.id
            source = 'self'
            self.calls.add((name, source))
        elif isinstance(node.func, ast.Attribute):
            # Method or attribute call like os.path.join()
            name = node.func.attr
            source = self._extract_source(node.func.value)
            if source:
                self.calls.add((name, source))
        
        # Continue visiting child nodes
        self.generic_visit(node)
    
    def _extract_source(self, node) -> str:
        """Recursively extract the source from an attribute chain."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            parent = self._extract_source(node.value)
            if parent:
                return f"{parent}.{node.attr}"
        return ""