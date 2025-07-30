import ast
import pytest
from stubmerge import merge_annotations

def ast_equal(a: ast.AST, b: ast.AST):
    return ast.dump(a, annotate_fields=True) == ast.dump(b, annotate_fields=True)

@pytest.mark.parametrize(
    "src, annot, expected",
    [
        # Return type override
        ("""
from typing import Any

def foo(x: int) -> Any:
    return x
""",
         """
from typing import Any

def foo(x: int) -> int:
    return x
""",
         """
from typing import Any

def foo(x: int) -> int:
    return x
"""),
        # Do not override with Any
        ("""
from typing import Any

def bar(x: int) -> int:
    return x
""",
         """
from typing import Any

def bar(x: int) -> Any:
    return x
""",
         """
from typing import Any

def bar(x: int) -> int:
    return x
"""),
        # Argument type override
        ("""
from typing import Any

def baz(x: Any) -> int:
    return 42
""",
         """
from typing import Any

def baz(x: str) -> int:
    return 42
""",
         """
from typing import Any

def baz(x: str) -> int:
    return 42
"""),
        # Union types
        ("""
from typing import Any

def foo(x: int) -> Any | int:
    return x
""",
         """
from typing import Any

def foo(x: int) -> int | str:
    return x
""",
         """
from typing import Any

def foo(x: int) -> int | str:
    return x
"""),
        # Incomplete
        ("""
from _typeshed import Incomplete

def foo(x: Incomplete) -> Incomplete:
    return x
""",
         """
from _typeshed import Incomplete

def foo(x: int) -> int:
    return x
""",
         """
from _typeshed import Incomplete

def foo(x: int) -> int:
    return x
"""),
        # Union with Incomplete
        ("""
from _typeshed import Incomplete

def foo(x: int | Incomplete) -> Incomplete | str:
    return x
""",
         """
from _typeshed import Incomplete

def foo(x: int | str) -> str:
    return x
""",
         """
from _typeshed import Incomplete

def foo(x: int | str) -> str:
    return x
"""),
    ]
)
def test_merge_annotations_param(src: str, annot: str, expected: str):
    src_ast = ast.parse(src)
    annot_ast = ast.parse(annot)
    expected_ast = ast.parse(expected)
    merged = merge_annotations(src_ast, annot_ast)
    assert ast_equal(merged, expected_ast)
