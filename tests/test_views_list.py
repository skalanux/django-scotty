import pytest
from django.test import RequestFactory

from tests.models import DummyItem


class TestCottonTableViewSlugname:
    def test_slugname_default_suffix(self):
        from django_scotty.views.list import CottonTableView

        slug = CottonTableView.get_slugname()
        assert slug == "cottontable"


class TestDictTableViewSlugname:
    def test_slugname_default_suffix(self):
        from django_scotty.views.list import DictTableView

        slug = DictTableView.get_slugname()
        assert slug == "dicttable"
