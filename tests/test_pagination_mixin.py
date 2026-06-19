"""Tests for PaginationFixMixin.

Verifies that invalid or out-of-range page numbers are handled by redirecting
to a valid page instead of crashing.
"""

from unittest.mock import MagicMock

from django.core.paginator import EmptyPage
from django.http import Http404
from django.test import RequestFactory


class TestPaginationFixMixin:
    """Tests for ``PaginationFixMixin`` redirect behavior on pagination errors.

    Covers EmptyPage and Http404 exceptions raised by the parent ``get()``.
    """

    def _make_view(self, parent_get_raises=None):
        """Build a view instance that mixes in PaginationFixMixin.

        Optionally configures a parent class whose ``get()`` raises a specific
        exception (EmptyPage or Http404).

        Args:
            parent_get_raises: ``"empty_page"``, ``"http404"``, or ``None``.

        Returns:
            object: A view instance ready to call ``get()`` on.
        """
        from django_scotty.mixins import PaginationFixMixin

        parents = (PaginationFixMixin,)

        if parent_get_raises == "empty_page":

            class _Parent:
                def get(self, *_args: object, **_kwargs: object) -> None:  # noqa: ARG002
                    """Mock parent ``get()`` that raises ``EmptyPage``."""
                    raise EmptyPage

            parents = (PaginationFixMixin, _Parent)

        elif parent_get_raises == "http404":

            class _Parent:
                def get(self, *_args: object, **_kwargs: object) -> None:  # noqa: ARG002
                    """Mock parent ``get()`` that raises ``Http404``."""
                    raise Http404

            parents = (PaginationFixMixin, _Parent)

        cls = type("TestView", parents, {})
        instance = cls()
        instance.request = RequestFactory().get("/test/?page=999")
        instance.paginate_by = 10
        instance.get_queryset = MagicMock(return_value=[])
        return instance

    def test_redirects_on_empty_page(self):
        """Verify an EmptyPage exception results in a 302 redirect."""
        view = self._make_view(parent_get_raises="empty_page")
        response = view.get(view.request)
        assert response.status_code == 302

    def test_redirects_on_http404(self):
        """Verify an Http404 exception from pagination results in a 302 redirect."""
        view = self._make_view(parent_get_raises="http404")
        response = view.get(view.request)
        assert response.status_code == 302

    def test_redirects_to_last_page(self):
        """Verify the redirect URL points to the last valid page when data exists."""
        view = self._make_view(parent_get_raises="empty_page")
        view.get_queryset = MagicMock(return_value=list(range(25)))
        response = view.get(view.request)
        assert response.status_code == 302
        assert "page=3" in response.url

    def test_redirects_to_page_one_when_empty(self):
        """Verify the redirect URL points to page 1 when the queryset is empty."""
        view = self._make_view(parent_get_raises="empty_page")
        view.get_queryset = MagicMock(return_value=[])
        response = view.get(view.request)
        assert response.status_code == 302
        assert "page=1" in response.url
