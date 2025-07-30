import ast
import pytest
from dataclasses import dataclass
from stubmerge import merge_annotations

@dataclass
class MergeCase:
    src: str
    annot: str
    expected: str

def ast_equal(a: ast.AST, b: ast.AST):
    return ast.dump(a, annotate_fields=True) == ast.dump(b, annotate_fields=True)

@pytest.mark.parametrize(
    "case",
    [
        MergeCase(
            src="""
from typing import Any

def foo(x: int) -> Any:
    return x
""",
            annot="""
from typing import Any

def foo(x: int) -> int:
    return x
""",
            expected="""
from typing import Any

def foo(x: int) -> int:
    return x
"""
        ),
        MergeCase(
            src="""
from typing import Any

def bar(x: int) -> int:
    return x
""",
            annot="""
from typing import Any

def bar(x: int) -> Any:
    return x
""",
            expected="""
from typing import Any

def bar(x: int) -> int:
    return x
"""
        ),
        MergeCase(
            src="""
from typing import Any

def baz(x: Any) -> int:
    return 42
""",
            annot="""
from typing import Any

def baz(x: str) -> int:
    return 42
""",
            expected="""
from typing import Any

def baz(x: str) -> int:
    return 42
"""
        ),
        MergeCase(
            src="""
from typing import Any

def foo(x: int) -> Any | int:
    return x
""",
            annot="""
from typing import Any

def foo(x: int) -> int | str:
    return x
""",
            expected="""
from typing import Any

def foo(x: int) -> int | str:
    return x
"""
        ),
        MergeCase(
            src="""
from _typeshed import Incomplete

def foo(x: Incomplete) -> Incomplete:
    return x
""",
            annot="""
from _typeshed import Incomplete

def foo(x: int) -> int:
    return x
""",
            expected="""
from _typeshed import Incomplete

def foo(x: int) -> int:
    return x
"""
        ),
        MergeCase(
            src="""
from _typeshed import Incomplete

def foo(x: int | Incomplete) -> Incomplete | str:
    return x
""",
            annot="""
from _typeshed import Incomplete

def foo(x: int | str) -> str:
    return x
""",
            expected="""
from _typeshed import Incomplete

def foo(x: int | str) -> str:
    return x
"""
        ),
        MergeCase(
            src="""
def foo(x):
    return x
""",
            annot="""
from typing import Any

def foo(x: Any):
    return x
""",
            expected="""
def foo(x: Any):
    return x
"""
        ),
    ]
)
def test_merge_annotations_param(case: MergeCase):
    src_ast = ast.parse(case.src)
    annot_ast = ast.parse(case.annot)
    expected_ast = ast.parse(case.expected)
    merged = merge_annotations(src_ast, annot_ast)
    assert ast_equal(merged, expected_ast)
