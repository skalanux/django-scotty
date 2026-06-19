"""Test views for django-scotty.

Defines concrete subclasses of the generic views (list, create, update, delete,
detail, dict) backed by DummyItem, used by integration and unit tests.
"""

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
    """Concrete list view for DummyItem using CottonTableView."""

    model = DummyItem
    table_class = DummyItemTable
    filterset_class = DummyItemFilterSet

    @classmethod
    def get_slugname(cls) -> str:
        """Return the slug name for this view.

        Returns:
            str: The slug ``"dummyitem"``.
        """
        return "dummyitem"


class DummyItemCreateView(GenericCreateView):
    """Concrete create view for DummyItem using GenericCreateView."""

    model = DummyItem
    form_class = DummyItemForm
    success_url = reverse_lazy("list-view-dummyitem")

    @classmethod
    def get_slugname(cls) -> str:
        """Return the slug name for this view.

        Returns:
            str: The slug ``"dummyitem"``.
        """
        return "dummyitem"


class DummyItemUpdateView(GenericUpdateView):
    """Concrete update view for DummyItem using GenericUpdateView."""

    model = DummyItem
    form_class = DummyItemForm
    success_url = reverse_lazy("list-view-dummyitem")

    @classmethod
    def get_slugname(cls) -> str:
        """Return the slug name for this view.

        Returns:
            str: The slug ``"dummyitem"``.
        """
        return "dummyitem"


class DummyItemDeleteView(GenericDeleteView):
    """Concrete delete view for DummyItem using GenericDeleteView."""

    model = DummyItem
    success_url = reverse_lazy("list-view-dummyitem")

    @classmethod
    def get_slugname(cls) -> str:
        """Return the slug name for this view.

        Returns:
            str: The slug ``"dummyitem"``.
        """
        return "dummyitem"


class DummyItemDetailView(GenericDetailView):
    """Concrete detail view for DummyItem using GenericDetailView."""

    model = DummyItem

    @classmethod
    def get_slugname(cls) -> str:
        """Return the slug name for this view.

        Returns:
            str: The slug ``"dummyitem"``.
        """
        return "dummyitem"


class DummyItemDictView(DictTableView):
    """Concrete dict list view for DummyItem using DictTableView."""

    model = DummyItem
    table_class = DummyItemTable

    @classmethod
    def get_slugname(cls) -> str:
        """Return the slug name for this view.

        Returns:
            str: The slug ``"dummyitem-dict"``.
        """
        return "dummyitem-dict"
