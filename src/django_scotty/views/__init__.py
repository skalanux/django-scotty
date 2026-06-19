"""Re-export all generic view classes from the views subpackage.

Provides a single entry point for importing CottonTableView, DictTableView,
GenericDetailView, GenericCreateView, GenericUpdateView, and GenericDeleteView.
"""

from django_scotty.views.create import GenericCreateView
from django_scotty.views.delete import GenericDeleteView
from django_scotty.views.detail import GenericDetailView
from django_scotty.views.list import CottonTableView, DictTableView
from django_scotty.views.update import GenericUpdateView

__all__ = [
    "CottonTableView",
    "DictTableView",
    "GenericDetailView",
    "GenericCreateView",
    "GenericUpdateView",
    "GenericDeleteView",
]
