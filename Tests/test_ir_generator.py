import pytest
from Compiler.ir_generator import IRGenerator
from llvmlite import ir


@pytest.fixture
def generator():
    return IRGenerator()


def test_var_def(generator):
    ast = ("program", [("var_def", "int", "x", ("integer", "42"))])
    result = generator.generate(ast)
    assert '%"x" = alloca i32\n  store i32 42, i32* %"x"' in result


def test_assignment(generator):
    ast = ("program", [
        ("var_def", "int", "x", ("integer", "42")),
        ("assignment", "x", ("integer", "24"))
    ])
    result = generator.generate(ast)
    assert 'store i32 42, i32* %"x"' in result
    assert 'store i32 24, i32* %"x"' in result


def test_enum_def(generator):
    ast = ("program", [("enum_def", "Color", ["RED", "GREEN", "BLUE"])])
    generator.generate(ast)
    assert 'Color' in generator.current_scope()


def test_binop(generator):
    ast = ('program', [
        ('var_def', 'int', 'c', ('binop', '+', ('integer', '3'), ('integer', '4')))
    ])
    ir_code = generator.generate(ast)
    assert 'add i32 3, 4' in ir_code


def test_comparison(generator):
    ast = ('program', [
        ('var_def', 'bool', 'c', ('comparison',
         '==', ('integer', '3'), ('integer', '4')))
    ])
    ir_code = generator.generate(ast)
    assert 'icmp eq i32 3, 4' in ir_code


def test_integer(generator):
    ast = ('program', [('var_def', 'int', 'a', ('integer', '5'))])
    ir_code = generator.generate(ast)
    assert 'i32 5' in ir_code


def test_double(generator):
    ast = ('program', [('var_def', 'double', 'a', ('double', '5.5'))])
    ir_code = generator.generate(ast)
    assert 'double 0x4016000000000000' in ir_code


def test_string(generator):
    ast = ('program', [('var_def', 'str', 'a', ('string', 'hello'))])
    ir_code = generator.generate(ast)
    assert '"a" = alloca i8' in ir_code
    assert 'i8* hello' in ir_code


def test_boolean(generator):
    ast = ('program', [('var_def', 'bool', 'a', ('boolean', 'True'))])
    ir_code = generator.generate(ast)
    assert 'i1 1' in ir_code


def test_fun_def_void(generator):
    ast = ('program', [
        ('fun_def', 'void', 'foo', [], [('return',)])
    ])
    ir_code = generator.generate(ast)
    assert 'define i32 @"a"()' in ir_code
    assert 'ret i32 0' in ir_code


def test_fun_def_with_params(generator):
    ast = ('program', [
        ('fun_def', 'void', 'foo', [
         ('int', 'a'), ('double', 'b')], [('return',)])
    ])
    ir_code = generator.generate(ast)
    assert 'define void @"foo"(i32 %".1", double %".2")' in ir_code
    assert '%"a" = alloca i32' in ir_code
    assert '%"b" = alloca double' in ir_code


def test_fun_def_with_body(generator):
    ast = ('program', [
        ('fun_def', 'void', 'foo', [('int', 'a')], [
            ('var_def', 'int', 'b', ('integer', '10')),
            ('assignment', 'b', ('binop', '+', ('identifier', 'a'), ('integer', '5')))
        ])
    ])
    ir_code = generator.generate(ast)
    assert 'define void @"foo"(i32 %".1")' in ir_code
    assert '%"a" = alloca i32' in ir_code
    assert '%".6" = add i32 %".5", 5' in ir_code


def test_when_stmts(generator):
    ast = ('program', [
        ('var_def', 'int', 'a', ('integer', '5')),
        ('when_stmts',
            ('when', ('comparison', '!=', ('identifier', 'a'), ('integer', '5')), [
                ('assignment', 'a', ('integer', '10'))
            ]),
            ('when', ('comparison', '==', ('identifier', 'a'), ('integer', '5')), [
                ('assignment', 'a', ('integer', '15'))
            ]),
         )
    ])
    ir_code = generator.generate(ast)
    assert 'br i1 %".4", label %"entry.if", label %"entry.endif"' in ir_code
    assert 'store i32 10, i32* %"a"' in ir_code
    assert 'store i32 15, i32* %"a"' in ir_code


def test_when(generator):
    ast = ('program', [
        ('var_def', 'int', 'a', ('integer', '5')),
        ('when', ('comparison', '==', ('identifier', 'a'), ('integer', '5')), [
            ('assignment', 'a', ('integer', '10'))
        ])
    ])
    ir_code = generator.generate(ast)
    assert 'br i1 %".4", label %"entry.if", label %"entry.endif"' in ir_code
    assert 'store i32 10, i32* %"a"' in ir_code


def test_class_def(generator):
    ast = ('program', [
        ('class_def', [], 'MyClass', [], [
            ('var_def', 'int', 'x', ('integer', '42')),
            ('fun_def', 'void', 'foo', [], [('return',)])
        ])
    ])
    ir_code = generator.generate(ast)
    assert 'MyClass' in generator.current_scope()
    assert '%"x" = alloca i32' in ir_code
    assert 'define void @"foo"()' in ir_code
