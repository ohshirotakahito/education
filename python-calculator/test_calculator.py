import unittest

from calculator import calculate, format_number


class CalculatorTests(unittest.TestCase):
    def test_operator_precedence(self):
        self.assertEqual(calculate("2 + 3 * 4"), 14)

    def test_parentheses_and_decimal(self):
        self.assertEqual(calculate("(10 - 2.5) / 3"), 2.5)

    def test_display_symbols(self):
        self.assertEqual(calculate("6 × 7 ÷ 2"), 21)

    def test_zero_division(self):
        with self.assertRaisesRegex(ValueError, "0では割れません"):
            calculate("10 / 0")

    def test_rejects_python_code(self):
        with self.assertRaises(ValueError):
            calculate("__import__('os').getcwd()")

    def test_format(self):
        self.assertEqual(format_number(1 / 3), "0.333333333333")

    def test_scientific_functions(self):
        self.assertAlmostEqual(calculate("sin(30)", "DEG"), 0.5)
        self.assertEqual(calculate("sqrt(81)"), 9)
        self.assertEqual(calculate("log(1000)"), 3)
        self.assertEqual(calculate("fact(5)"), 120)

    def test_constants_and_radians(self):
        self.assertAlmostEqual(calculate("cos(pi)", "RAD"), -1)


if __name__ == "__main__":
    unittest.main()
