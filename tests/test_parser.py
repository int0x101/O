import unittest
from parser import parser
from utils import pre


class TestParser(unittest.TestCase):

    def test_assignment(self):
        data = pre("int b = 0")
        results = parser.parse(data)
        self.assertEqual(results[0], ("var_def", "int", "b", "0"))

    def test_multiline(self):
        data = pre("int a = 0\nint b = 1")
        results = parser.parse(data)
        self.assertEqual(results[0], ("var_def", "int", "a", "0"))
        self.assertEqual(results[1], ("var_def", "int", "b", "1"))

    def test_comparison(self):
        data = pre("bool is_equal = a == b")
        results = parser.parse(data)
        self.assertEqual(
            results[0],
            (
                "var_def",
                "bool",
                "is_equal",
                ("comparison", "==", ("identifier", "a"), ("identifier", "b")),
            ),
        )

    def test_enum(self):
        data = pre("enum a { A, C }")
        results = parser.parse(data)
        self.assertEqual(results[0], ("enum_def", "a", ["A", "C"]))

    def test_keyword_stmt(self):
        data = pre("pass")
        results = parser.parse(data)
        self.assertEqual(results[0], ("pass",))

    def test_function_call(self):
        data = pre("b(0)")
        results = parser.parse(data)
        self.assertEqual(results[0], ("fun_call", "b", ["0"]))

    def test_fun_def(self):
        data = pre("int a = 0\nint a():\n int b():\n  return 0\n int c():\n  return 0")
        results = parser.parse(data)
        self.assertEqual(len(results), 2)

    def test_fun_def_decorators(self):
        data = pre("@b\nint a():\n return 0")
        results = parser.parse(data)
        self.assertEqual(
            results[0],
            ("fun_def", [("decorator", "b")], "int", "a", [], [("return", "0")]),
        )

    def test_class_def(self):
        data = pre("class MyClass:\n pass")
        results = parser.parse(data)
        self.assertEqual(results[0], ("class_def", [], "class", [], [("pass",)]))

    def test_class_def_with_decorator(self):
        data = pre("@decorator\nclass MyClass:\n pass")
        results = parser.parse(data)
        self.assertEqual(
            results[0],
            ("class_def", [("decorator", "decorator")], "class", [], [("pass",)]),
        )

    def test_class_def_with_inheritance(self):
        data = pre("class MyClass extends BaseClass:\n pass")
        results = parser.parse(data)
        self.assertEqual(
            results[0], ("class_def", [], "class", ["BaseClass"], [("pass",)])
        )

    def test_class_def_with_decorator_and_inheritance(self):
        data = pre("@decorator\nclass MyClass extends BaseClass:\n pass")
        results = parser.parse(data)
        self.assertEqual(
            results[0],
            (
                "class_def",
                [("decorator", "decorator")],
                "class",
                ["BaseClass"],
                [("pass",)],
            ),
        )

    def test_when_stmt_single(self):
        data = pre("when a == b:\n pass")
        results = parser.parse(data)
        self.assertEqual(
            results[0][0],
            (
                "when",
                ("comparison", "==", ("identifier", "a"), ("identifier", "b")),
                [("pass",)],
                None,
            ),
        )

    def test_when_stmt_multiple(self):
        data = pre("when a == b:\n pass\nwhen c == d:\n pass")
        results = parser.parse(data)
        self.assertEqual(len(results[0]), 2)
        self.assertEqual(
            results[0][0],
            (
                "when",
                ("comparison", "==", ("identifier", "a"), ("identifier", "b")),
                [("pass",)],
                None,
            ),
        )
        self.assertEqual(
            results[0][1],
            (
                "when",
                ("comparison", "==", ("identifier", "c"), ("identifier", "d")),
                [("pass",)],
                None,
            ),
        )

    def test_when_with_otherwise(self):
        data = pre("when a == b:\n pass\notherwise:\n pass")
        results = parser.parse(data)
        self.assertEqual(
            results[0][0],
            (
                "when",
                ("comparison", "==", ("identifier", "a"), ("identifier", "b")),
                [("pass",)],
                ("otherwise", [("pass",)]),
            ),
        )


if __name__ == "__main__":
    unittest.main()
