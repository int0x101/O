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


if __name__ == "__main__":
    unittest.main()
