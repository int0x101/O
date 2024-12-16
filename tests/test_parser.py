import unittest
from parser import parser
from utils import pre

class TestParser(unittest.TestCase):
    
    def test_var_def(self):
        data = pre("int a = 0")
        results = parser.parse(data)
        self.assertEqual(len(results), 4)

    def test_fun_def(self):
        data = pre("bool is_active():\n  int a = 1")
        results = parser.parse(data)
        results

    def test_class_def(self):
        data = pre("""class User:\n  str name = 0\n  str password = 0\n  int a():\n    int a = 9\n  int b = 0""")
        results = parser.parse(data)
        results




if __name__ == "__main__":
    unittest.main()