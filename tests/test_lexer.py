import unittest
from lexer import lexer
from utils import pre


class TestLexer(unittest.TestCase):
    def test_indentation(self):
        data = pre("""class User:\n  str name = 0\n  str password = 0\n  int a():\n    int a = 9""")
        lexer.input(data)
        tokens = list(lexer)
        self.assertEqual(len(tokens), 26)




if __name__ == "__main__":
    unittest.main()
