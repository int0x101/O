import pytest
from lexer import lexer

def test_var_def():
    data = '''str a = "hello"'''
    lexer.input(data)
    tokens = list(lexer)
    assert len(tokens) == 4

def test_function_def():
    data = '''int main():\n pass'''
    lexer.input(data)
    tokens = list(lexer)
    assert len(tokens) == 8

def test_operators():
    data = """a + b - c * d / e % f ** g"""
    lexer.input(data)
    tokens = list(lexer)
    assert len(tokens) == 13

def test_comparisons():
    data = """a == b != c < d <= e > f >= g"""
    lexer.input(data)
    tokens = list(lexer)
    assert len(tokens) == 13

def test_template_string():
    data = 't"Hello! {name}"'
    lexer.input(data)
    tokens = list(lexer)
    assert len(tokens) == 1
    assert tokens[0].type == "TEMPLATE_STRING"
    assert tokens[0].value == 'Hello! {name}'

def test_inline_condition():
    data = "a == b ? x ! y"
    lexer.input(data)
    tokens = list(lexer)
    assert len(tokens) == 7
    assert tokens[3].type == "QUESTION"
    assert tokens[5].type == "EXCLAMATION"
