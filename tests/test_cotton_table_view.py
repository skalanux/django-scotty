import pytest
from django.http import HttpRequest
from django.test import RequestFactory, override_settings

from tests.models import DummyItem


class SampleFilterSet:
    class Meta:
        model = DummyItem
        fields = ["name", "active"]

    def __init__(self, *args, **kwargs):
        from django_filters import FilterSet
        self._filterset = FilterSet(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._filterset, name)


class TestCottonTableViewGetExportFilename:
    def test_generates_filename(self):
        from django_scotty.views.list import CottonTableView

        filename = CottonTableView().get_export_filename("xlsx")
        assert filename == "cottontable.xlsx"


class TestCottonTableViewGetTableKwargs:
    def test_default_not_view_only(self):
        from django_scotty.views.list import CottonTableView

        factory = RequestFactory()
        request = factory.get("/")
        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem

        kwargs = view.get_table_kwargs()
        assert "post_paginate_hook" in kwargs
