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
