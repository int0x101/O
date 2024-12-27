import pytest
from Parser.parser import parser


def test_var_def():
    data = 'str a = "hello"'
    results = parser.parse(data)
    results


def test_assignment_equal():
    data = "a = 5"
    results = parser.parse(data)
    assert results[1][0] == ("assignment", "=", "a", ("integer", "5"))


def test_assignment_plus_equal():
    data = "a += 5"
    results = parser.parse(data)
    assert results[1][0] == ("assignment", "+=", "a", ("integer", "5"))


def test_multiline():
    data = "int a = 0\nint b = 1"
    results = parser.parse(data)
    assert results[1][0] == ("var_def", "int", "a", ("integer", "0"))
    assert results[1][1] == ("var_def", "int", "b", ("integer", "1"))


def test_comparison():
    data = "bool is_equal = a == b"
    results = parser.parse(data)
    assert results[1][0] == (
        "var_def",
        "bool",
        "is_equal",
        ("comparison", "==", ("identifier", "a"), ("identifier", "b")),
    )


def test_enum():
    data = "enum a { A, C }"
    results = parser.parse(data)
    assert results[1][0] == ("enum_def", "a", ["A", "C"])


def test_keyword_stmt():
    data = "pass"
    results = parser.parse(data)
    assert results[1][0] == ("pass",)


def test_function_call():
    data = "b(0)"
    results = parser.parse(data)
    assert results[1][0] == ("fun_call", "b", [("integer", "0")])


def test_fun_def():
    data = "int a():\n return 0"
    results = parser.parse(data)
    assert len(results[1]) == 1


def test_fun_def_decorators():
    data = "@b\nint a():\n return 0"
    results = parser.parse(data)
    assert results[1][0] == (
        "fun_def",
        [("decorator", "b")],
        "int",
        "a",
        [],
        [("return", ("integer", "0"))],
    )


def test_class_def():
    data = "class MyClass:\n int size = 0\n int a():\n  pass"
    results = parser.parse(data)
    assert results[1][0] == (
        "class_def",
        [],
        "MyClass",
        None,
        [
            ("var_def", "int", "size", ("integer", "0")),
            ("fun_def", [], "int", "a", [], [("pass",)]),
        ],
    )

# TODO

# def test_class_def_with_decorator():
#     data = "@decorator\nclass MyClass:\n pass"
#     results = parser.parse(data)
#     assert results[1][0] == (
#         "class_def",
#         [("decorator", "decorator")],
#         "MyClass",
#         [],
#         [("pass",)],
#     )


# def test_class_def_with_inheritance():
#     data = "class MyClass extends BaseClass:\n pass"
#     results = parser.parse(data)
#     assert results[1][0] == ("class_def", [], "MyClass", ["BaseClass"], [("pass",)])


# def test_class_def_with_decorator_and_inheritance():
#     data = "@decorator\nclass MyClass extends BaseClass:\n pass"
#     results = parser.parse(data)
#     assert results[1][0] == (
#         "class_def",
#         [("decorator", "decorator")],
#         "MyClass",
#         ["BaseClass"],
#         [("pass",)],
#     )


def test_when_stmt_single():
    data = "when a == b:\n pass"
    results = parser.parse(data)
    assert results[1][0][1] == (
        "when",
        ("comparison", "==", ("identifier", "a"), ("identifier", "b")),
        [("pass",)],
    )


def test_when_stmt_multiple():
    data = "when a == b:\n pass\nwhen c == d:\n pass"
    results = parser.parse(data)
    assert len(results[1][0][1:]) == 2
    assert results[1][0] == (
        "when_stmts",
        (
            "when",
            ("comparison", "==", ("identifier", "a"), ("identifier", "b")),
            [("pass",)],
        ),
        (
            "when",
            ("comparison", "==", ("identifier", "c"), ("identifier", "d")),
            [("pass",)],
        ),
    )
    assert results[1][0][1] == (
        "when",
        ("comparison", "==", ("identifier", "a"), ("identifier", "b")),
        [("pass",)],
    )


def test_when_with_otherwise():
    data = "when a == b:\n pass\notherwise:\n pass"
    results = parser.parse(data)
    assert results[1][0][1:] == (
        (
            "when",
            ("comparison", "==", ("identifier", "a"), ("identifier", "b")),
            [("pass",)],
        ),
        ("otherwise", [("pass",)]),
    )


def test_array_def():
    data = "int[] sizes = [2, 4, 9]"
    results = parser.parse(data)
    assert results[1][0] == (
        "var_def",
        "int[]",
        "sizes",
        ("array_literal", [("integer", "2"),
         ("integer", "4"), ("integer", "9")]),
    )

# TODO: Fix object def
# def test_object_def():
#     data = 'str:int sizes = {"L": 6}'
#     results = parser.parse(data)
#     assert results[1][0] == (
#         "var_def",
#         "{str: int}",
#         "sizes",
#         ("object_literal", [("keypair", "L", ("integer", "6"))]),
#     )


def test_lambda_def():
    data = "int a = int b => 2"
    results = parser.parse(data)
    assert results[1][0] == (
        "var_def",
        "int",
        "a",
        ("lambda", [("int", "b")], ("integer", "2")),
    )


def test_lambda_def_with_multiple_params():
    data = "int x = int a, int b => a + b"
    results = parser.parse(data)
    assert results[1][0] == (
        "var_def",
        "int",
        "x",
        (
            "lambda",
            [("int", "a"), ("int", "b")],
            ("binop", "+", ("identifier", "a"), ("identifier", "b")),
        ),
    )


def test_for_stmt():
    data = "for int i in [2,3,4]:\n pass"
    results = parser.parse(data)
    assert results[1][0] == (
        "for_stmt",
        ("int", "i"),
        ("array_literal", [("integer", "2"),
         ("integer", "3"), ("integer", "4")]),
        [("pass",)],
    )


def test_for_stmt_with_block():
    data = "for int i in [1,2]:\n int a = 0\n int b = 1"
    results = parser.parse(data)
    assert results[1][0] == (
        "for_stmt",
        ("int", "i"),
        ("array_literal", [("integer", "1"), ("integer", "2")]),
        [("var_def", "int", "a", ("integer", "0")),
         ("var_def", "int", "b", ("integer", "1"))],
    )


def test_switch_stmt():
    data = "switch a:\n case 4:\n  return 0"
    results = parser.parse(data)
    assert results[1][0] == (
        "switch_stmt",
        ("identifier", "a"),
        [("case", ("integer", "4"), [("return", ("integer", "0"))])],
    )


def test_switch_stmt_with_multiple_cases():
    data = "switch y:\n case 1:\n  pass\n case 2:\n  pass\n case 3:\n  pass"
    results = parser.parse(data)
    assert len(results[1][0][2]) == 3
    assert results[1][0] == (
        "switch_stmt",
        ("identifier", "y"),
        [
            ("case", ("integer", "1"), [("pass",)]),
            ("case", ("integer", "2"), [("pass",)]),
            ("case", ("integer", "3"), [("pass",)]),
        ],
    )


def test_switch_stmt_with_block():
    data = "switch z:\n case 1:\n  int a = 0\n  int b = 1\n case 2:\n  pass"
    results = parser.parse(data)
    assert results[1][0] == (
        "switch_stmt",
        ("identifier", "z"),
        [
            (
                "case",
                ("integer", "1"),
                [("var_def", "int", "a", ("integer", "0")),
                 ("var_def", "int", "b", ("integer", "1"))],
            ),
            ("case", ("integer", "2"), [("pass",)]),
        ],
    )


def test_try_except():
    data = "try:\n pass\nexcept:\n pass"
    results = parser.parse(data)
    assert results[1][0] == ("try", [("pass",)], [
                             ("except", None, [("pass",)])])


def test_try_except_with_exception():
    data = "try:\n pass\nexcept Exception:\n pass"
    results = parser.parse(data)
    assert results[1][0] == ("try", [("pass",)], [
                             ("except", "Exception", [("pass",)])])


def test_try_multiple_except():
    data = "try:\n pass\nexcept Exception:\n pass\nexcept:\n pass"
    results = parser.parse(data)
    assert results[1][0] == (
        "try",
        [("pass",)],
        [("except", "Exception", [("pass",)]), ("except", None, [("pass",)])],
    )


def test_array_range():
    data = "[1...10]"
    results = parser.parse(data)
    assert results[1][0] == (
        "array_range", ("integer", "1"), ("integer", "10"))


def test_array_range_with_variables():
    data = "[a...b]"
    results = parser.parse(data)
    assert results[1][0] == (
        "array_range", ("identifier", "a"), ("identifier", "b"))


def test_array_range_with_expressions():
    data = "[a + 1...b - 1]"
    results = parser.parse(data)
    assert results[1][0] == (
        "array_range",
        ("binop", "+", ("identifier", "a"), ("integer", "1")),
        ("binop", "-", ("identifier", "b"), ("integer", "1")),
    )


def test_object_unpacking():
    data = '{**other, "name": "hard265"}'
    results = parser.parse(data)
    assert results[1][0] == (
        "object_literal",
        [("unpack", "other"), ("keypair", "name", ("string", "hard265"))],
    )


def test_object_unpacking_multiple():
    data = '{**other1, **other2, "name": "hard265"}'
    results = parser.parse(data)
    assert results[1][0] == (
        "object_literal",
        [("unpack", "other1"), ("unpack", "other2"),
         ("keypair", "name", ("string", "hard265"))],
    )


def test_array_comprehension_basic():
    data = "[x for int x in [1, 2, 3]]"
    results = parser.parse(data)
    assert results[1][0] == (
        "array_comprehension",
        ("identifier", "x"),
        ("int", "x"),
        ("array_literal", [("integer", "1"),
         ("integer", "2"), ("integer", "3")]),
    )


def test_array_comprehension_with_condition():
    data = "[x for int x in [1, 2, 3] when x > 1]"
    results = parser.parse(data)
    assert results[1][0] == (
        "array_comprehension",
        ("identifier", "x"),
        ("int", "x"),
        ("array_literal", [("integer", "1"),
         ("integer", "2"), ("integer", "3")]),
        ("comparison", ">", ("identifier", "x"), ("integer", "1")),
    )