"""URL auto-discovery for django-scotty views.

Provides utilities to automatically register URL patterns by scanning
modules for django-scotty view subclasses.
"""

import importlib
import inspect
import logging
import os
import pkgutil
from types import ModuleType

from django.urls import path
from django.urls.resolvers import URLPattern

from django_scotty.views import (
    CottonTableView,
    DictTableView,
    GenericCreateView,
    GenericDeleteView,
    GenericDetailView,
    GenericUpdateView,
)

logger = logging.getLogger(__name__)

__all__ = [
    "add_urls",
    "load_scotty_urls",
]


def add_urls(views_modules: list[ModuleType]) -> list[URLPattern]:
    """Register URL patterns for all django-scotty views found in modules.

    Scans each module for subclasses of CottonTableView, DictTableView,
    GenericDetailView, GenericCreateView, GenericUpdateView, and
    GenericDeleteView, registering standard CRUD URL patterns.

    Args:
        views_modules: List of Python modules to scan for view classes.

    Returns:
        A list of URLPattern instances ready to be included in
        ``urlpatterns``.
    """
    urlpatterns: list[URLPattern] = []
    for module in views_modules:
        for _name, cls in inspect.getmembers(module, inspect.isclass):
            if (
                _name != "CottonTableView"
                and (issubclass(cls, CottonTableView) or issubclass(cls, DictTableView))
                and hasattr(cls, "as_view")
            ):
                trimed_view_name = cls.get_slugname()
                urlpatterns.append(
                    path(
                        f"{trimed_view_name}/",
                        cls.as_view(),
                        name=f"list-view-{trimed_view_name}",
                    )
                )
            if issubclass(cls, GenericDetailView):
                trimed_view_name = cls.get_slugname()
                urlpatterns.append(
                    path(
                        f"{trimed_view_name}/<int:pk>/",
                        cls.as_view(model=cls.model),
                        name=f"detail-view-{trimed_view_name}",
                    )
                )
            if _name != "GenericCreateView" and issubclass(cls, GenericCreateView):
                trimed_view_name = cls.get_slugname()
                urlpatterns.append(
                    path(
                        f"{trimed_view_name}/crear/",
                        cls.as_view(),
                        name=f"create-view-{trimed_view_name}",
                    )
                )
            if _name != "GenericUpdateView" and issubclass(cls, GenericUpdateView):
                trimed_view_name = cls.get_slugname()
                urlpatterns.append(
                    path(
                        f"{trimed_view_name}/<int:pk>/editar/",
                        cls.as_view(),
                        name=f"update-view-{trimed_view_name}",
                    )
                )
            if _name != "GenericDeleteView" and issubclass(cls, GenericDeleteView):
                trimed_view_name = cls.get_slugname()
                urlpatterns.append(
                    path(
                        f"{trimed_view_name}/<int:pk>/eliminar/",
                        cls.as_view(),
                        name=f"delete-view-{trimed_view_name}",
                    )
                )
    return urlpatterns


def load_scotty_urls(app_name: str | None = None) -> list[URLPattern]:
    """Auto-discover and register django-scotty views for an application.

    Looks for a ``scotty/`` directory inside the given app and imports
    every module found there, registering their view subclasses as URL
    patterns.

    Args:
        app_name: The Django application name. If ``None``, it is inferred
            from the caller's module path.

    Returns:
        A list of URLPattern instances for all discovered views.
    """
    if app_name is None:
        caller_frame = inspect.stack()[1]
        caller_module = inspect.getmodule(caller_frame[0])
        caller_module_name = caller_module.__name__
        app_name = caller_module_name.split(".")[0]

    app_module = importlib.import_module(app_name)
    app_path = os.path.dirname(app_module.__file__)
    scotty_dir = os.path.join(app_path, "scotty")

    collected_urls: list[URLPattern] = []

    if os.path.isdir(scotty_dir):
        for module_info in pkgutil.iter_modules([scotty_dir]):
            module_name = module_info.name
            if module_name == "__init__":
                continue

            full_module_path = f"{app_name}.scotty.{module_name}"

            modules_list: list[ModuleType] = []
            try:
                module = importlib.import_module(full_module_path)
                modules_list.append(module)
            except Exception as err:
                logging.error(
                    f"[SCOTTY LOADER] Error importing {full_module_path} {err}"
                )
            collected_urls += add_urls(modules_list)

    return collected_urls
