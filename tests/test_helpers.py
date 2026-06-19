"""Tests for the deprecated django_scotty.helpers module.

Verifies that importing the helpers module emits a DeprecationWarning.
"""

import warnings


def test_helpers_deprecation_warning():
    """Verify importing ``django_scotty.helpers`` raises a DeprecationWarning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        import django_scotty.helpers  # noqa: F401

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()
