import ast
from stubmerge.visitor import is_more_informative_type

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
