import ast
from stubmerge.visitor import is_more_informative_type
from stubmerge import merge_annotations

def parse_type(expr: str):
    return ast.parse(expr, mode="eval").body

def test_none_vs_type():
    assert not is_more_informative_type(None, parse_type("int"))
    assert is_more_informative_type(parse_type("int"), None)

def test_any_vs_type():
    assert not is_more_informative_type(parse_type("Any"), parse_type("int"))
    assert is_more_informative_type(parse_type("int"), parse_type("Any"))

def test_incomplete_vs_type():
    assert not is_more_informative_type(parse_type("Incomplete"), parse_type("str"))
    assert is_more_informative_type(parse_type("str"), parse_type("Incomplete"))

def test_any_vs_incomplete():
    assert not is_more_informative_type(parse_type("Any"), parse_type("Incomplete"))
    assert not is_more_informative_type(parse_type("Incomplete"), parse_type("Any"))

def test_union_with_any():
    assert not is_more_informative_type(parse_type("Any | int"), parse_type("int"))
    assert is_more_informative_type(parse_type("int"), parse_type("Any | int"))
    assert not is_more_informative_type(parse_type("Any | str"), parse_type("str"))
    assert is_more_informative_type(parse_type("str"), parse_type("Any | str"))

def test_union_with_incomplete():
    assert not is_more_informative_type(parse_type("int | Incomplete"), parse_type("int"))
    assert is_more_informative_type(parse_type("int"), parse_type("int | Incomplete"))
    assert not is_more_informative_type(parse_type("str | Incomplete"), parse_type("str"))
    assert is_more_informative_type(parse_type("str"), parse_type("str | Incomplete"))

def test_union_placeholders_vs_real_type():
    assert not is_more_informative_type(parse_type("Any | Incomplete"), parse_type("str"))
    assert is_more_informative_type(parse_type("str"), parse_type("Any | Incomplete"))
    assert not is_more_informative_type(parse_type("Any | Incomplete"), parse_type("int | str"))
    assert is_more_informative_type(parse_type("int | str"), parse_type("Any | Incomplete"))

def get_func_annotation(module_ast, func_name):
    for node in module_ast.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return node.returns
    return None

def test_merge_annotations_overrides_return_type():
    src = """
from typing import Any

def foo(x: int) -> Any:
    return x
"""
    annot = """
from typing import Any

def foo(x: int) -> int:
    return x
"""
    src_ast = ast.parse(src)
    annot_ast = ast.parse(annot)
    merged = merge_annotations(src_ast, annot_ast)
    ret = get_func_annotation(merged, "foo")
    assert isinstance(ret, ast.Name)
    assert ret.id == "int"

def test_merge_annotations_does_not_override_with_any():
    src = """
from typing import Any

def bar(x: int) -> int:
    return x
"""
    annot = """
from typing import Any

def bar(x: int) -> Any:
    return x
"""
    src_ast = ast.parse(src)
    annot_ast = ast.parse(annot)
    merged = merge_annotations(src_ast, annot_ast)
    ret = get_func_annotation(merged, "bar")
    assert isinstance(ret, ast.Name)
    assert ret.id == "int"

def test_merge_annotations_argument_type():
    src = """
from typing import Any

def baz(x: Any) -> int:
    return 42
"""
    annot = """
from typing import Any

def baz(x: str) -> int:
    return 42
"""
    src_ast = ast.parse(src)
    annot_ast = ast.parse(annot)
    merged = merge_annotations(src_ast, annot_ast)
    for node in merged.body:
        if isinstance(node, ast.FunctionDef) and node.name == "baz":
            arg = node.args.args[0]
            assert isinstance(arg.annotation, ast.Name)
            assert arg.annotation.id == "str"
