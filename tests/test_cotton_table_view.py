"""Tests for CottonTableView internals.

Covers export filename generation and table kwargs construction.
"""

from django.test import RequestFactory

from tests.models import DummyItem


class SampleFilterSet:
    """A minimal filterset wrapper that delegates to django-filter's FilterSet.

    Used as a lightweight stand-in for filter integration tests.
    """

    class Meta:
        model = DummyItem
        fields = ["name", "active"]

    def __init__(self, *args, **kwargs):
        """Initialize the underlying django-filter FilterSet.

        Args:
            *args: Positional arguments forwarded to FilterSet.
            **kwargs: Keyword arguments forwarded to FilterSet.
        """
        from django_filters import FilterSet

        self._filterset = FilterSet(*args, **kwargs)

    def __getattr__(self, name):
        """Delegate attribute access to the underlying FilterSet.

        Args:
            name: The attribute name.

        Returns:
            Any: The attribute from the inner FilterSet.
        """
        return getattr(self._filterset, name)


class TestCottonTableViewGetExportFilename:
    """Tests for ``CottonTableView.get_export_filename``."""

    def test_generates_filename(self):
        """Verify the export filename matches the default slug pattern."""
        from django_scotty.views.list import CottonTableView

        filename = CottonTableView().get_export_filename("xlsx")
        assert filename == "cottontable.xlsx"


class TestCottonTableViewGetTableKwargs:
    """Tests for ``CottonTableView.get_table_kwargs``."""

    def test_default_not_view_only(self):
        """Verify table kwargs include ``post_paginate_hook`` by default."""
        from django_scotty.views.list import CottonTableView

        factory = RequestFactory()
        request = factory.get("/")
        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem

        kwargs = view.get_table_kwargs()
        assert "post_paginate_hook" in kwargs
