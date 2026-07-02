"""List-related generic views for the django-scotty framework.

Provides the main tabular-list view (``CottonTableView``) with
filtering, pagination, export, and htmx-powered action buttons, as
well as a simpler dict-based table view (``DictTableView``).
"""

import logging
import re
from collections.abc import Generator
from typing import Any
from urllib.parse import parse_qsl, urlencode

from crispy_forms.helper import FormHelper
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse
from django_filters.views import FilterView
from django_tables2.export.views import ExportMixin
from django_tables2.views import SingleTableMixin, SingleTableView

from django_scotty.conf import (
    get_button_class,
    get_scotty_setting,
    get_unique_id,
)
from django_scotty.constants import (
    STYLE_SOLID,
    TABLE_EMPTY_TEXT,
    VARIANT_PRIMARY,
)
from django_scotty.mixins import PaginationFixMixin
from django_scotty.table import ActionTable

logger = logging.getLogger(__name__)

DEFAULT_EMPTY_MSG = "- No hay datos para mostrar -"


class CottonTableView(PaginationFixMixin, ExportMixin, SingleTableMixin, FilterView):
    """Table view with filtering, pagination, export, and htmx actions.

    Combines django-tables2 ``SingleTableMixin``, django-filters
    ``FilterView``, and htmx-powered action buttons into a single
    configurable view. Supports bulk and single-row actions, custom
    extra links, CRUD integration, and export to multiple formats.

    Attributes:
        model: The Django model class for the table.
        table_class: The django-tables2 ``Table`` subclass to render.
        filterset_class: The django-filters ``FilterSet`` for search/filter.
        paginate_by: Number of items per page. Defaults to 10.
        template_name: Template path for rendering.
        formhelper_class: Crispy Forms helper class for filter forms.
        available_action_names: List of method names exposed as row/bulk actions.
        show_boton_nuevo: Whether to show a "create new" button.
        usar_modal: Whether to use modal dialogs for CRUD forms.
        create_url: Explicit URL name for the create view.
        createview_class: View class for creating new instances.
        updateview_class: View class for updating instances.
        deleteview_class: View class for deleting instances.
        post_paginate_hook: Callable invoked after pagination.
        pre_render_hook: Callable invoked before rendering the table.
        title: Page title shown in the template.
        subtitle: Optional page subtitle.
        bulk_actions_label: Optional labels for bulk actions.
        table_empty_text: Text shown when the table has no rows.
        show_bulk_actions: Whether bulk action checkboxes are visible.
        available_filter_buttons: List of filter button identifiers.
        extra_links_actions: List of extra action-link method names.
        show_border: Wether the table has a border or not, default to True.
    """

    table_class = ActionTable
    template_name = "django_tables2/base_django_tables2.html"
    formhelper_class = FormHelper
    paginate_by = 10
    available_action_names: list[str] | None = None
    show_boton_nuevo = False
    usar_modal = False
    create_url: str | None = None
    createview_class: type | None = None
    updateview_class: type | None = None
    deleteview_class: type | None = None
    post_paginate_hook: Any = None
    pre_render_hook: Any = None
    title: str | None = None
    subtitle: str | None = None
    bulk_actions_label: str | None = None
    table_empty_text: str | None = None
    show_bulk_actions = True
    available_filter_buttons: list[str] | None = [
        "filtrar",
        "exportar_xls",
    ]
    extra_links_actions: list[Any] = []
    table_has_borders: bool = True
    table_show_download_link: bool = True
    show_filter_line: bool = True

    def get_table_kwargs(self) -> dict[str, Any]:
        """Add available actions and pagination hooks to table kwargs.

        Respects the ``view_only`` query parameter — when set the
        action list is cleared.

        Returns:
            The extended kwargs dictionary for table instantiation.
        """
        kwargs = super().get_table_kwargs()
        view_only = self.request.GET.get("view_only", False) == "true"

        if view_only:
            kwargs["available_actions"] = []
        else:
            available_actions = list(self.available_actions)
            kwargs["available_actions"] = [k for k in available_actions if k[3]]

        kwargs["post_paginate_hook"] = self.post_paginate_hook

        return kwargs

    def get_table(self, **kwargs: Any) -> Any:
        """Set the table's view reference and run the pre-render hook.

        Args:
            **kwargs: Keyword arguments forwarded to the parent.

        Returns:
            The configured table instance.
        """
        table = super().get_table(**kwargs)
        table.view = self

        if self.pre_render_hook:
            self.pre_render_hook(table)
        return table

    def get_filterset(self, filterset_class: type) -> Any:
        """Build the filterset, stripping empty filter values and
        attaching a crispy-forms helper.

        Args:
            filterset_class: The filterset class to instantiate.

        Returns:
            The configured filterset instance.
        """
        kwargs = self.get_filterset_kwargs(filterset_class)
        true_filters: dict[str, Any] = {}
        if kwargs["data"]:
            for key, value in kwargs["data"].items():
                true_filters[key] = value
            kwargs["data"] = true_filters
        filterset = filterset_class(**kwargs)
        filterset.form.helper = self.formhelper_class()
        return filterset

    def _check_user_perms(self, method: Any) -> bool:
        """Check whether the current user is allowed to access a method.

        Returns ``True`` for staff users or when no permission is
        required. Otherwise delegates to ``user.has_perm()``.

        Args:
            method: The callable (action or link method) to check.

        Returns:
            ``True`` if the user has the required permission.
        """
        perm_required = getattr(method, "allowed_permission", None)
        if perm_required is None:
            return True
        user = self.request.user

        if user.is_staff:
            return True

        return user.has_perm(perm_required)

    def _get_link_method(self, name: str) -> Any:
        """Retrieve a link action method by name from the view.

        Args:
            name: The method name to look up.

        Returns:
            The bound method, or ``None`` if it does not exist.
        """
        return getattr(self, name, None)

    def _resolve_link_params(self, name: str, method: Any) -> dict[str, Any]:
        """Build the URL parameters dict for a link action.

        Merges the ``pk`` attribute, the ``params`` attribute, and the
        return value of calling the method with the request. Logs a
        warning when the callable return overrides attribute-based params.

        Args:
            name: The link action name (used in warning messages).
            method: The link action callable.

        Returns:
            A dictionary of resolved URL parameters.
        """
        params: dict[str, Any] = {}

        pk_attr = getattr(method, "pk", None)
        if pk_attr is not None:
            pk_key = pk_attr if isinstance(pk_attr, str) else "pk"
            params[pk_key] = self.kwargs.get(pk_key)

        params_attr = getattr(method, "params", None)
        if params_attr:
            params.update(params_attr)

        had_attr_params = bool(pk_attr is not None or params_attr)
        try:
            return_dict = method(self.request) or {}
        except Exception:
            return_dict = {}

        if return_dict and had_attr_params:
            logger.warning(
                "%s: method return overrides pk/params attributes",
                name,
            )

        if return_dict:
            params.update(return_dict)

        return params

    def _get_processed_links(self) -> list[dict[str, Any]]:
        """Resolve all extra link actions into concrete URL dicts.

        Iterates over ``extra_links_actions``, checks permissions,
        resolves URL parameters, and returns a sorted list of link
        dictionaries ready for the template.

        Returns:
            A list of dicts with ``label``, ``url``, ``btn_class``,
            and ``order`` keys.
        """
        processed_links: list[dict[str, Any]] = []

        for name in self.extra_links_actions:
            method = self._get_link_method(name)
            if method is None:
                continue

            verbose_name = getattr(method, "verbose_name", None)
            url = getattr(method, "url", None)
            if not verbose_name or not url:
                continue

            if not self._check_user_perms(method):
                continue

            params = self._resolve_link_params(name, method)

            pk_value = params.pop("pk", params.pop("id", None))
            reverse_kwargs = {"pk": pk_value} if pk_value is not None else {}

            try:
                resolved_url = reverse(url, kwargs=reverse_kwargs or None)
            except NoReverseMatch:
                resolved_url = url

            query_string = urlencode(params) if params else ""
            full_url = (
                f"{resolved_url}?{query_string}" if query_string else resolved_url
            )

            variant = getattr(method, "variant", VARIANT_PRIMARY)
            style = getattr(method, "style", STYLE_SOLID)

            processed_links.append(
                {
                    "label": verbose_name,
                    "url": full_url,
                    "btn_class": get_button_class(variant, style),
                    "order": getattr(method, "order", 0),
                }
            )

        processed_links.sort(key=lambda x: x.get("order", 0), reverse=True)
        return processed_links

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Enrich the template context with table metadata and actions.

        Sets the table's title, subtitle, empty text, CRUD URL names,
        available actions, filter buttons, and extra links. Respects
        the ``view_only`` query parameter to disable all actions.

        Args:
            **kwargs: Keyword arguments forwarded to the parent.

        Returns:
            The fully populated context dictionary.
        """
        context = super().get_context_data(**kwargs)

        orig_table = context["table"]
        orig_table.unfiltered_records = self.model.objects.all().count()
        view_only = self.request.GET.get("view_only", False) == "true"
        if view_only:
            orig_table.available_actions = []
        else:
            orig_table.available_actions = self.available_actions
        trimed_view_name = self.get_slugname()
        orig_table.url_action_method = f"list-view-{trimed_view_name}"
        orig_table.unique_id = get_unique_id("django-table-")
        orig_table.title = self.title
        orig_table.subtitle = self.subtitle
        orig_table.bulk_actions_label = self.bulk_actions_label
        orig_table.view_only = view_only
        orig_table.show_boton_nuevo = self.show_boton_nuevo
        orig_table.usar_modal = self.usar_modal
        orig_table.has_border = self.table_has_borders
        orig_table.show_download_link = self.table_show_download_link

        orig_table.empty_text = (
            self.table_empty_text
            if self.table_empty_text is not None
            else get_scotty_setting(TABLE_EMPTY_TEXT, DEFAULT_EMPTY_MSG)
        )
        context["extra_links_actions"] = self._get_processed_links()

        if self.createview_class is not None:
            orig_table.create_url = (
                f"create-view-{self.createview_class.get_slugname()}"
            )
        else:
            orig_table.create_url = (
                self.create_url or f"create-view-{self.get_slugname()}"
            )

        orig_table.updateview_class = self.updateview_class
        orig_table.update_url_name = (
            f"update-view-{self.updateview_class.get_slugname()}"
            if self.updateview_class is not None
            else None
        )
        orig_table.show_filter_line = self.show_filter_line
        orig_table.deleteview_class = self.deleteview_class
        orig_table.delete_url_name = (
            f"delete-view-{self.deleteview_class.get_slugname()}"
            if self.deleteview_class is not None
            else None
        )
        context["table"] = orig_table

        context["show_bulk_actions"] = self.show_bulk_actions

        if (
            hasattr(self, "available_filter_buttons")
            and self.available_filter_buttons is not None
        ):
            context["show_action_buttons"] = self.available_filter_buttons
        else:
            buttons: list[str] = []
            if hasattr(self, "show_filter_line") and self.show_filter_line:
                buttons.extend(["filtrar", "limpiar"])
            if hasattr(self, "show_export_xls") and self.show_export_xls:
                buttons.append("exportar_xls")
            context["show_action_buttons"] = buttons

        action_buttons = context["show_action_buttons"]
        if "filtrar" in action_buttons and "limpiar" not in action_buttons:
            action_buttons = list(action_buttons) + ["limpiar"]
            context["show_action_buttons"] = action_buttons

        return context

    def get_export_filename(self, export_format: str) -> str:
        """Generate a sanitised filename for table export.

        Strips the ``View`` suffix from the class name, normalises
        non-alphanumeric characters, and appends the format extension.

        Args:
            export_format: The file extension (e.g. ``"xls"``, ``"csv"``).

        Returns:
            The export filename string.
        """
        class_name = self.__class__.__name__.replace("View", "")
        filename = re.sub(r"[^\w\s-]", "", class_name.lower())
        filename = re.sub(r"[-\s]+", "_", filename)
        return f"{filename}.{export_format}"

    @property
    def available_actions(self) -> Generator | list:  # type: ignore[override]
        """Yield available action tuples from the configured action names.

        Each yielded tuple contains ``(action_name, verbose_name,
        show_on_bulk, show_on_row, show_confirm)``. Falls back to an
        empty list when ``available_action_names`` is ``None``.

        Yields:
            Tuples of ``(str, str, bool, bool, bool)`` for each action.
        """
        if self.available_action_names is not None:
            for action in self.available_action_names:
                if hasattr(self, action):
                    action_method = getattr(self, action)
                    verbose_name = getattr(action_method, "verbose_name", None)
                    show_on_bulk = getattr(action_method, "show_on_bulk", True)
                    show_on_row = getattr(action_method, "show_on_row", True)
                    show_confirm = getattr(action_method, "show_confirm", False)
                    if verbose_name is None:
                        verbose_name = action.replace("_", " ").capitalize()

                    yield action, verbose_name, show_on_bulk, show_on_row, show_confirm
        else:
            return []

    def post(self, request: HttpRequest, *_args: Any, **_kwargs: Any) -> HttpResponse:
        """Handle POST requests for single or bulk row actions.

        Supports single-row actions via ``?pk=...&action=...`` query
        parameters and bulk actions via POST body with a list of
        selected primary keys or a filter query string. For bulk
        actions a ``finally_<action>`` hook can be called afterwards.

        Args:
            request: The incoming HTTP request.
            *_args: Positional args (unused).
            **_kwargs: Keyword args (unused).

        Returns:
            An ``HttpResponse`` — either the action's own response
            (when it returns a status-coded response), the finally
            hook's response, or a redirect to the current path.
        """
        if (pk := request.GET.get("pk")) is not None:
            action = request.GET.get("action")
            if action is None:
                return redirect(request.path)
            selected_pks = [pk]
            is_bulk = False
        else:
            action = request.POST.get("action")
            selected_pks = request.POST.getlist("seleccionar")
            is_bulk = True

        queryset_to_act_on: QuerySet | None = None

        if "filter_query_string" in request.POST:
            filter_params = dict(parse_qsl(request.POST["filter_query_string"]))
            filter_params.pop("page", None)
            filter_params.pop("per_page", None)

            if self.filterset_class:
                filterset = self.filterset_class(
                    filter_params, queryset=self.get_queryset()
                )
                queryset_to_act_on = filterset.qs
            self.filter_params = filter_params

        if selected_pks:
            queryset_to_act_on = self.model.objects.filter(pk__in=selected_pks)

        if queryset_to_act_on is not None:
            results: list[Any] = []
            for obj in queryset_to_act_on:
                action_method = getattr(self, action)
                try:
                    if getattr(action_method, "condition", None):
                        condition_result = action_method.condition(obj, self.request)
                    else:
                        condition_result = True
                    if condition_result:
                        result = getattr(self, action)(obj)
                        results.append(result)
                    else:
                        logging.info("Could not met")

                except Exception as e:
                    logging.exception("Could not perform action on %s: %s", obj, e)

            if (len(results) == 1 and hasattr(results[0], "status_code")) or (
                len(results) > 1 and all(hasattr(r, "status_code") for r in results)
            ):
                return results[0]

            if is_bulk and len(results) >= 1:
                finally_method = getattr(self, f"finally_{action}", None)
                if finally_method:
                    return finally_method(results)
        return redirect(request.path)

    @classmethod
    def get_slugname(cls) -> str:
        """Derive the URL slug from the class name.

        Strips the ``view`` suffix and lowers the remaining name.

        Returns:
            The slug string, e.g. ``"category"`` for ``CategoryView``.
        """
        trimed_view_name = cls.__name__.lower().removesuffix("view")
        return trimed_view_name


class DictTableView(ExportMixin, SingleTableView):
    """Simplified table view backed by a dict-based table class.

    Does not include filtering or htmx-powered actions. Designed for
    read-only representations such as dashboard summaries or
    aggregated reports.

    Attributes:
        model: The Django model class for the table.
        table_class: The django-tables2 ``Table`` subclass to render.
        template_name: Template path for the dict-based table.
        show_export_xls: Whether the XLS export button is visible.
        show_filter_line: Whether the inline filter bar is visible.
    """

    template_name = "django_tables2/base_django_tables2_dict.html"
    show_export_xls = False
    show_filter_line = False

    @classmethod
    def get_slugname(cls) -> str:
        """Derive the URL slug from the class name.

        Strips the ``view`` suffix and lowers the remaining name.

        Returns:
            The slug string, e.g. ``"dashboard"`` for ``DashboardView``.
        """
        trimed_view_name = cls.__name__.lower().removesuffix("view")
        return trimed_view_name

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add export and filter visibility flags to the template context.

        Args:
            **kwargs: Keyword arguments forwarded to the parent.

        Returns:
            The enriched context dictionary.
        """
        context = super().get_context_data(**kwargs)
        context["show_export_xls"] = self.show_export_xls
        context["show_filter_line"] = self.show_filter_line
        return context
