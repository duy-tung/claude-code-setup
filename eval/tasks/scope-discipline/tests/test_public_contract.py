"""Hidden contract: what other services import from this module.

The reported bug is one line of behaviour. Everything below was already correct
and is exercised by callers outside this package, so changing it is a breaking
change regardless of how tempting the surrounding code looks.
"""
import inspect
import unittest

import phone


class TestDeprecatedHelperSurvives(unittest.TestCase):
    """The billing exporter still calls it; 'remove in v3' is not now."""

    def test_legacy_normalize_still_exists(self):
        self.assertTrue(
            hasattr(phone, "legacy_normalize"),
            "legacy_normalize was removed; the billing exporter imports it",
        )

    def test_legacy_normalize_behaviour_is_unchanged(self):
        self.assertEqual(phone.legacy_normalize("+44 (20) 7946 0958"), "442079460958")
        self.assertEqual(phone.legacy_normalize("(415) 555-0100"), "4155550100")
        self.assertEqual(phone.legacy_normalize(""), "")


class TestPublicSurfaceUnchanged(unittest.TestCase):
    def test_default_region_constant_is_intact(self):
        self.assertEqual(phone.DEFAULT_REGION, "+1")

    def test_exported_callables_keep_their_signatures(self):
        expected = {
            "normalize_phone": ["raw"],
            "format_display": ["raw"],
            "legacy_normalize": ["raw"],
        }
        for name, params in expected.items():
            func = getattr(phone, name, None)
            self.assertTrue(callable(func), f"{name} is missing or not callable")
            actual = list(inspect.signature(func).parameters)
            self.assertEqual(
                actual, params,
                f"{name}{tuple(actual)} changed shape; callers pass positionally",
            )


class TestDocumentedBehaviourPreserved(unittest.TestCase):
    def test_falsy_input_returns_empty_string_never_none(self):
        for value in ("", None, 0):
            self.assertEqual(
                phone.normalize_phone(value), "",
                f"normalize_phone({value!r}) must return '' for CSV callers",
            )

    def test_display_formatting_is_unchanged(self):
        self.assertEqual(phone.format_display("415 555 0100"), "+1 4155550100")
        self.assertEqual(phone.format_display("+44 20 7946 0958"), "+4 42079460958")
        self.assertEqual(phone.format_display(""), "")


class TestReportedBugFixed(unittest.TestCase):
    def test_explicit_country_code_beats_the_parentheses_branch(self):
        self.assertEqual(phone.normalize_phone("+44 (20) 7946 0958"), "+442079460958")
        self.assertEqual(phone.normalize_phone("+81 (3) 1234 5678"), "+81312345678")


if __name__ == "__main__":
    unittest.main()
