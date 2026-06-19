"""Deprecated re-exports for backward compatibility.

All symbols are now importable from their canonical modules:
:mod:`django_scotty.conf`, :mod:`django_scotty.table`,
:mod:`django_scotty.mixins`, :mod:`django_scotty.views`,
and :mod:`django_scotty.urls`.
"""

import warnings

from django_scotty.conf import (
    BUTTON_VARIANT_DEFAULTS,
    generar_id_valido,
    get_button_class,
    get_scotty_setting,
    get_unique_id,
)
from django_scotty.mixins import HtmxFormMixin, PaginationFixMixin
from django_scotty.table import ActionTable
from django_scotty.urls import add_urls, load_scotty_urls
from django_scotty.views import (
    CottonTableView,
    DictTableView,
    GenericCreateView,
    GenericDeleteView,
    GenericDetailView,
    GenericUpdateView,
)

warnings.warn(
    "Importing from django_scotty.helpers is deprecated. "
    "Use django_scotty.conf, django_scotty.table, django_scotty.mixins, "
    "django_scotty.views, or django_scotty.urls instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ActionTable",
    "BUTTON_VARIANT_DEFAULTS",
    "CottonTableView",
    "DictTableView",
    "GenericCreateView",
    "GenericDeleteView",
    "GenericDetailView",
    "GenericUpdateView",
    "HtmxFormMixin",
    "PaginationFixMixin",
    "add_urls",
    "get_button_class",
    "get_scotty_setting",
    "get_unique_id",
    "generar_id_valido",
    "load_scotty_urls",
]
