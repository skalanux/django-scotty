from unittest.mock import MagicMock

from django.core.paginator import EmptyPage
from django.http import Http404
from django.test import RequestFactory


class TestPaginationFixMixin:
    def _make_view(self, parent_get_raises=None):
        from django_scotty.mixins import PaginationFixMixin

        parents = (PaginationFixMixin,)

        if parent_get_raises == "empty_page":
            class _Parent:
                def get(self, request, *args, **kwargs):
                    raise EmptyPage
            parents = (PaginationFixMixin, _Parent)

        elif parent_get_raises == "http404":
            class _Parent:
                def get(self, request, *args, **kwargs):
                    raise Http404
            parents = (PaginationFixMixin, _Parent)

        cls = type("TestView", parents, {})
        instance = cls()
        instance.request = RequestFactory().get("/test/?page=999")
        instance.paginate_by = 10
        instance.get_queryset = MagicMock(return_value=[])
        return instance

    def test_redirects_on_empty_page(self):
        view = self._make_view(parent_get_raises="empty_page")
        response = view.get(view.request)
        assert response.status_code == 302

    def test_redirects_on_http404(self):
        view = self._make_view(parent_get_raises="http404")
        response = view.get(view.request)
        assert response.status_code == 302

    def test_redirects_to_last_page(self):
        view = self._make_view(parent_get_raises="empty_page")
        view.get_queryset = MagicMock(return_value=list(range(25)))
        response = view.get(view.request)
        assert response.status_code == 302
        assert "page=3" in response.url

    def test_redirects_to_page_one_when_empty(self):
        view = self._make_view(parent_get_raises="empty_page")
        view.get_queryset = MagicMock(return_value=[])
        response = view.get(view.request)
        assert response.status_code == 302
        assert "page=1" in response.url
