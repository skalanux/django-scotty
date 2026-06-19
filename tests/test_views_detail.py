"""Tests for slugname derivation on the detail view.

Verifies that ``get_slugname()`` strips the ``DetailView`` suffix correctly.
"""


class TestGenericDetailViewSlugname:
    """Tests for ``GenericDetailView.get_slugname``."""

    def test_slugname(self):
        """Verify the slug strips the ``DetailView`` suffix."""
        from django_scotty.views.detail import GenericDetailView

        slug = GenericDetailView.get_slugname()
        assert slug == "generic"
