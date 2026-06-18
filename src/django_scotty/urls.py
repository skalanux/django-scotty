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
