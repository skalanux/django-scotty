from django.urls import reverse_lazy
from django_filters import FilterSet

from django_scotty.table import ActionTable
from django_scotty.views.create import GenericCreateView
from django_scotty.views.delete import GenericDeleteView
from django_scotty.views.detail import GenericDetailView
from django_scotty.views.list import CottonTableView, DictTableView
from django_scotty.views.update import GenericUpdateView
from tests.forms import DummyItemForm
from tests.models import DummyItem


class DummyItemTable(ActionTable):
    """Test table for DummyItem — mirrors production usage of ActionTable."""

    class Meta:
        model = DummyItem


class DummyItemFilterSet(FilterSet):
    """Minimal filterset for DummyItem list view."""

    class Meta:
        model = DummyItem
        fields = ["name", "active"]


class DummyItemListView(CottonTableView):
    model = DummyItem
    table_class = DummyItemTable
    filterset_class = DummyItemFilterSet

    @classmethod
    def get_slugname(cls) -> str:
        return "dummyitem"


class DummyItemCreateView(GenericCreateView):
    model = DummyItem
    form_class = DummyItemForm
    success_url = reverse_lazy("list-view-dummyitem")

    @classmethod
    def get_slugname(cls) -> str:
        return "dummyitem"


class DummyItemUpdateView(GenericUpdateView):
    model = DummyItem
    form_class = DummyItemForm
    success_url = reverse_lazy("list-view-dummyitem")

    @classmethod
    def get_slugname(cls) -> str:
        return "dummyitem"


class DummyItemDeleteView(GenericDeleteView):
    model = DummyItem
    success_url = reverse_lazy("list-view-dummyitem")

    @classmethod
    def get_slugname(cls) -> str:
        return "dummyitem"


class DummyItemDetailView(GenericDetailView):
    model = DummyItem

    @classmethod
    def get_slugname(cls) -> str:
        return "dummyitem"


class DummyItemDictView(DictTableView):
    model = DummyItem
    table_class = DummyItemTable

    @classmethod
    def get_slugname(cls) -> str:
        return "dummyitem-dict"
