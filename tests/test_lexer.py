import unittest
from lexer import lexer
from utils import pre


class TestLexer(unittest.TestCase):
    def test_string_var_def(self):
        data = pre('''str a = "hello"''')
        lexer.input(data)
        tokens = list(lexer)
        self.assertEqual(len(tokens), 5)

    def test_indentation(self):
        data = pre("""int b = 0\n""")
        lexer.input(data)
        tokens = list(lexer)
        self.assertEqual(len(tokens), 5)

    def test_keywords(self):
        data = pre("""int a\nstr b\nbool c\ndouble d\n""")
        lexer.input(data)
        tokens = list(lexer)
        self.assertEqual(len(tokens), 12)

    def test_operators(self):
        data = pre("""a + b - c * d / e % f ** g\n""")
        lexer.input(data)
        tokens = list(lexer)
        self.assertEqual(len(tokens), 14)

    def test_comparisons(self):
        data = pre("""a == b != c < d <= e > f >= g\n""")
        lexer.input(data)
        tokens = list(lexer)
        self.assertEqual(len(tokens), 14)


if __name__ == "__main__":
    unittest.main()
