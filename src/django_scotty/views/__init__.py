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
