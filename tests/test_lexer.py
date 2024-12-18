import unittest
from lexer import lexer
from utils import pre


class TestLexer(unittest.TestCase):
    def test_indentation(self):
        data = pre("""int b = 0\n""")
        lexer.input(data)
        tokens = list(lexer)
        self.assertEqual(len(tokens), 5)




if __name__ == "__main__":
    unittest.main()
