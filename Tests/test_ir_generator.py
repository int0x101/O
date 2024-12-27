import pytest
from Compiler.ir_generator import IRGenerator
from llvmlite import ir


@pytest.fixture
def generator():
    return IRGenerator()


def test_var_def(generator):
    ast = [
        ('fun_def', [], 'int', 'main', [], [
            ('var_def', 'str', 'a', ('string', 'hello'))
        ])
    ]
    results = generator.generate(ast)
    assert '%"a" = alloca i8*' in results
    assert 'store i8* hello, i8** %"a"' in results


def test_assignment(generator):
    ast = [
        ('fun_def', [], 'int', 'main', [], [
            ('var_def', 'int', 'a', ('integer', '2')),
            ("assignment", "+=", "a", ("integer", "4"))
        ])
    ]
    results = generator.generate(ast)
    assert '%"a" = alloca i32' in results
    assert 'store i32 2, i32* %"a"' in results
    assert '%"a_add" = add i32 %"a.1", 4' in results


def test_comparison_equal(generator):
    ast = [
        ('fun_def', [], 'int', 'main', [], [
            ('var_def', 'int', 'a', ('integer', '1')),
            ('var_def', 'int', 'b', ('integer', '1')),
            ('when_stmts', [
                ('when', ('comparison', '==', ('identifier', 'a'), ('identifier', 'b')), [
                    ('var_def', 'int', 'c', ('integer', '10'))
                ]),
                ('otherwise', [
                    ('var_def', 'int', 'c', ('integer', '20'))
                ])
            ])
        ])
    ]
    results = generator.generate(ast)
    assert '%".4" = icmp eq i32 %"a.1", %"b.1"' in results


def test_fun_call(generator):
    ast = [
        ('fun_def', [], 'int', 'main', [], [
            ('fun_def', [], 'int', 'foo', [], [
                ('return', ('integer', '42'))
            ]),
            ('fun_call', 'foo', [])
        ])
    ]
    results = generator.generate(ast)
    assert 'define i32 @"foo"()' in results
    assert 'ret i32 42' in results
    assert '%"foo_call" = call i32 @"foo"()' in results


def test_fun_call_with_args(generator):
    ast = [
        ('fun_def', [], 'int', 'main', [], [
            ('fun_def', [], 'int', 'add', [('int', 'a'), ('int', 'b')], [
                ('return', ('binop', '+', ('identifier', 'a'), ('identifier', 'b')))
            ]),
        ])
    ]
    results = generator.generate(ast)
    assert 'define i32 @"add"(i32 %".1", i32 %".2")' in results
    assert '%".8" = add i32 %"a", %"b"' in results


def test_class_def(generator):
    ast = [
        ('class_def', [], 'MyClass', None, [
            ('var_def', 'int', 'x', ('integer', '0')),
            ('var_def', 'double', 'y', ('double', '0.0')),
            ('class_ctor_def', [], [('int', 'a'), ('double', 'b')], [
                ('assignment', '=', 'x', ('identifier', 'a')),
                ('assignment', '=', 'y', ('identifier', 'b'))
            ]),
            ('fun_def', [], 'int', 'get_x', [], [
                ('return', ('identifier', 'x'))
            ]),
            ('fun_def', [], 'double', 'get_y', [], [
                ('return', ('identifier', 'y'))
            ])
        ])
    ]
    results = generator.generate(ast)
    assert '%"MyClass" = type {i32, double}' in results
    assert 'define %"MyClass"* @"MyClass_ctor"(i32 %".1", double %".2")' in results
    assert 'define i32 @"MyClass_get_x"(%"MyClass"* %".1")' in results
    assert 'define double @"MyClass_get_y"(%"MyClass"* %".1")' in results


def test_when_stmts(generator):
    ast = [
        ('fun_def', [], 'int', 'main', [], [
            ('when_stmts', [
                ('when', ('comparison', '==', ('integer', '1'), ('integer', '1')), [
                    ('var_def', 'int', 'a', ('integer', '10'))
                ]),
                ('otherwise', [
                    ('var_def', 'int', 'a', ('integer', '20'))
                ])
            ])
        ])
    ]
    results = generator.generate(ast)
    assert '%".2" = icmp eq i32 1, 1' in results


def test_for_stmt(generator):
    ast = [
        ('fun_def', [], 'int', 'main', [], [
            ('for_stmt', ('int', 'i'), ('array_literal', [('integer', '2'), ('integer', '3')]), [
                ('var_def', 'int', 'a', ('identifier', 'i'))
            ])
        ])
    ]
    results = generator.generate(ast)
    assert '%"index" = alloca i32' in results
    assert 'br label %"loop"' in results
    assert 'loop:' in results
    assert '%"next_index" = add i32 %"index.1", 1' in results
    assert 'br i1 %".10", label %"loop", label %"after_loop"' in results


def test_switch_stmt(generator):
    ast = [
        ('fun_def', [], 'int', 'main', [], [
            ('var_def', 'int', 'a', ('integer', '1')),
            (
                "switch_stmt",
                ("identifier", "a"),
                [
                    ("case", ("integer", "4"), [("return", ("integer", "0"))]),
                    ("case", ("integer", "1"), [("return", ("integer", "0"))]),
                ],
            )
        ])
    ]
    results = generator.generate(ast)
    assert 'switch i32 %"a.1", label %"switch_default" [i32 4, label %"case_4" i32 1, label %"case_1"]' in results