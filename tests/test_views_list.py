"""Tests for slugname derivation on list views.

Verifies that ``get_slugname()`` strips ``TableView`` suffixes correctly.
"""


class TestCottonTableViewSlugname:
    """Tests for ``CottonTableView.get_slugname``."""

    def test_slugname_default_suffix(self):
        """Verify the slug strips the ``TableView`` suffix from CottonTableView."""
        from django_scotty.views.list import CottonTableView

        slug = CottonTableView.get_slugname()
        assert slug == "cottontable"


class TestDictTableViewSlugname:
    """Tests for ``DictTableView.get_slugname``."""

    def test_slugname_default_suffix(self):
        """Verify the slug strips the ``TableView`` suffix from DictTableView."""
        from django_scotty.views.list import DictTableView

        slug = DictTableView.get_slugname()
        assert slug == "dicttable"
