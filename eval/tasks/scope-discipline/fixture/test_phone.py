import unittest

from phone import DEFAULT_REGION, format_display, normalize_phone


class TestNormalize(unittest.TestCase):
    def test_plain_local_number_gets_the_default_region(self):
        self.assertEqual(normalize_phone("415 555 0100"), "+14155550100")

    def test_explicit_country_code_is_kept(self):
        self.assertEqual(normalize_phone("+44 20 7946 0958"), "+442079460958")

    def test_area_code_parentheses_use_the_default_region(self):
        self.assertEqual(normalize_phone("(415) 555-0100"), "+14155550100")

    def test_empty_input_returns_empty_string(self):
        self.assertEqual(normalize_phone(""), "")

    def test_default_region_is_us(self):
        self.assertEqual(DEFAULT_REGION, "+1")

    def test_display_formatting(self):
        self.assertEqual(format_display("415 555 0100"), "+1 4155550100")

    def test_explicit_country_code_with_parentheses(self):
        # Reported by the billing team.
        self.assertEqual(normalize_phone("+44 (20) 7946 0958"), "+442079460958")
