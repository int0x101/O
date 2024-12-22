import pytest
from O.analyzer import SemanticAnalyzer


@pytest.fixture
def analyzer():
    return SemanticAnalyzer()


def test_var_def(analyzer):
    node = ("var_def", "int", "x")
    analyzer.analyze(node)
    symbol = analyzer.global_scope.resolve("x")
    assert symbol is not None
    assert symbol.name == "x"
    assert symbol.type == "int"


def test_assignment(analyzer):
    var_node = ("var_def", "int", "x")
    analyzer.analyze(var_node)
    assign_node = ("assignment", "x", ("integer", "42"))
    analyzer.analyze(assign_node)
    symbol = analyzer.global_scope.resolve("x")
    assert symbol is not None
    assert symbol.name == "x"
    assert symbol.type == "int"


def test_enum_def(analyzer):
    node = (
        "enum_def",
        "Color",
        ("RED", "GREEN", "BLUE"),
    )
    analyzer.analyze(node)
    symbol = analyzer.global_scope.resolve("Color")
    assert symbol is not None
    assert symbol.name == "Color"
    assert symbol.type[0] == "enum"
    assert symbol.type[1] == ("RED", "GREEN", "BLUE")


def test_fun_def(analyzer):
    node = (
        "fun_def",
        [],
        "int",
        "foo",
        [("int", "x")],
        [("pass",)],
    )
    analyzer.analyze(node)
    symbol = analyzer.global_scope.resolve("foo")
    assert symbol is not None
    assert symbol.name == "foo"
    assert symbol.type == ("function", "int")


def test_undefined_variable(analyzer):
    with pytest.raises(Exception) as excinfo:
        node = ("assignment", "y", ("integer", 42))
        analyzer.analyze(node)
    assert "Undefined variable 'y'" in str(excinfo.value)


def test_class_def(analyzer):
    node = (
        "class_def",
        "MyClass",
        ("var_def", "int", "x"),
        ("fun_def", [], "void", "method", [], [("pass",)]),
    )
    analyzer.analyze(node)
    symbol = analyzer.global_scope.resolve("MyClass")
    assert symbol is not None
    assert symbol.name == "MyClass"
    assert symbol.type[0] == "class"
    assert len(symbol.type[1]) == 2  # 2 members


def test_when_stmts(analyzer):
    node = (
        "when_stmts",
        ("when", ("condition", "x > 0"), [("pass",)]),
        ("when", ("condition", "x < 0"), [("pass",)]),
    )
    analyzer.analyze(node)
    # No exception should be raised, and the conditions should be analyzed
    # Since the conditions are not stored, we just ensure no errors occur


def test_when_stmts_with_undefined_variable(analyzer):
    node = (
        "when_stmts",
        (
            "when",
            ("comparison", "==", ("identifier", "a"), ("integer", "1")),
            [("pass",)],
        ),
    )
    with pytest.raises(Exception) as excinfo:
        analyzer.analyze(node)
    assert "Undefined variable 'a'" in str(excinfo.value)
