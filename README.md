# StubMerge

StubMerge is a Python library for merging type annotations from one AST (such as a stub or annotation file) into another Python source AST. It is useful for improving type information in codebases or stub files.

The motivating use case for developing this was to merge the comprehensive types produced by mypy's `stubgen --inspect-mode` with the more accurate types produced by MonkeyType.

## Basic Example

Suppose you have two Python sources:

**Source file:**
```python
def foo(x: Any) -> Any:
    return x
```

**Annotation file:**
```python
from typing import Any

def foo(x: int) -> int:
    return x
```

You can merge the more informative annotations from the annotation file into the source file:

```python
import ast
from stubmerge import merge_annotations

source_code = """
def foo(x: Any) -> Any:
    return x
"""
annotation_code = """
from typing import Any

def foo(x: int) -> int:
    return x
"""

source_ast = ast.parse(source_code)
annotation_ast = ast.parse(annotation_code)
merged_ast = merge_annotations(source_ast, annotation_ast)

# To convert the merged AST back to code (Python 3.9+):
import ast
print(ast.unparse(merged_ast))
```

**Output:**
```python
def foo(x: int) -> int:
    return x
```

## Installation
```bash
uv add `git+https://github.com/WEHI-ResearchComputing/StubMerge
```

## Testing
Run tests with pytest:
```bash
uv run pytest
```

## License
MIT
