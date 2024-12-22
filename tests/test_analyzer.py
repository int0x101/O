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


def test_assignment(analyzer):
    var_node = ("var_def", "int", "x")
    analyzer.analyze(var_node)
    assign_node = ("assignment", "x", ("integer", '42'))
    analyzer.analyze(assign_node)
    symbol = analyzer.global_scope.resolve("x")
    assert symbol is not None
    assert symbol.name == "x"
    assert symbol.type == "int"


def test_undefined_variable(analyzer):
    with pytest.raises(Exception) as excinfo:
        node = ("assignment", "y", ("integer", 42))
        analyzer.analyze(node)
    assert "Undefined variable 'y'" in str(excinfo.value)


