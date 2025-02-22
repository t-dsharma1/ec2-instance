import pytest

from connectai.handlers.utils import string_matcher


class TestStringMatcher:
    """Test string matcher functions."""

    @pytest.mark.parametrize(
        "target, candidates, expected",
        [
            ("B", [], None),
            ("", [], None),
            ("B", ["A", "B", "C"], "B"),
            ("B", {"B": None, "C": None}.keys(), "B"),
            ("D", ["A", "B", "C"], None),
            ("AB", ["A", "B", "C"], None),
        ],
    )
    def test_match_string_exact(self, target, candidates, expected):
        """Test the exact string matching function."""
        assert string_matcher.match_string_exact(target, candidates) == expected

    @pytest.mark.parametrize(
        "target, candidates, is_case_matter, expected",
        [
            ("B", [], False, None),
            ("", [], False, None),
            ("B", ["A", "B", "C"], True, "B"),
            ("B", {"B": None, "C": None}.keys(), True, "B"),
            ("b", ["A", "B", "C"], True, None),
            ("b", ["A", "B", "C"], False, "B"),
            ("customer device information", ["CUSTOMER_DEVICE_INFORMATION"], False, "CUSTOMER_DEVICE_INFORMATION"),
            ("cust device info", ["CUSTOMER_DEVICE_INFORMATION"], False, "CUSTOMER_DEVICE_INFORMATION"),
            ("customer", ["CUSTOMER_DEVICE_INFORMATION"], False, None),
        ],
    )
    def test_match_string_fuzzy(self, target, candidates, is_case_matter, expected):
        """Test the fuzzy string matching function."""
        assert string_matcher.match_string_fuzzy(target, candidates, is_case_matter=is_case_matter) == expected
