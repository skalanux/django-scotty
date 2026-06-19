"""View mixins for django-scotty.

Provides reusable mixins that integrate django-tables2 pagination with
htmx-driven modal forms.
"""

import contextlib
import logging
from typing import Any

from django.core.paginator import EmptyPage, Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from django_scotty.conf import get_unique_id
from django_scotty.form_helpers import get_form_buttons

logger = logging.getLogger(__name__)

__all__ = [
    "PaginationFixMixin",
    "HtmxFormMixin",
]


class PaginationFixMixin:
    """Mixin that catches EmptyPage/Http404 and redirects to a valid page.

    Must be placed before a view class (e.g. ListView) in the MRO so that
    ``super().get()`` resolves to the view's ``get`` method.

    Attributes:
        request: Injected by the view's ``dispatch()`` at runtime.
        paginate_by: Number of items per page, set on the concrete view.
    """

    request: Any  # Django HttpRequest — injected by the view's dispatch()
    paginate_by: int

    def get_queryset(self) -> Any:
        """Return the queryset from the parent view."""
        return super().get_queryset()  # type: ignore[misc]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Handle GET requests, redirecting to a valid page on pagination errors.

        Catches ``EmptyPage`` and ``Http404`` exceptions raised when the
        requested page does not exist, and redirects to the last available
        page (or page 1 when the queryset is empty).

        Args:
            request: The incoming HTTP request.
            *args: Positional arguments forwarded to the parent.
            **kwargs: Keyword arguments forwarded to the parent.

        Returns:
            An HTTP response from the parent view, or a redirect.
        """
        try:
            return super().get(request, *args, **kwargs)  # type: ignore[no-any-return,misc]
        except (EmptyPage, Http404):
            try:
                queryset = self.get_queryset()

                if hasattr(self, "get_filterset") and hasattr(self, "filterset_class"):
                    filterset = self.get_filterset(self.filterset_class)
                    if filterset.is_valid():
                        queryset = filterset.qs

                paginator = Paginator(queryset, self.paginate_by)
                total_pages = paginator.num_pages
                target_page = total_pages if total_pages > 0 else 1

            except Exception:
                target_page = 1

            get_params = request.GET.copy()
            get_params["page"] = str(target_page)

            redirect_url = f"{request.path}?{get_params.urlencode()}"
            return redirect(redirect_url)


class HtmxFormMixin:
    """Mixin that enables htmx-powered modal forms for CreateView/UpdateView.

    Attributes like ``request``, ``model``, ``form_class``, and
    ``get_slugname`` are provided by the concrete view class at runtime via
    Django's CBV machinery. Mypy cannot resolve these, so they are typed as
    ``Any`` below to silence ``attr-defined`` errors.
    """

    template_name = "django_tables2/generic_form.html"
    partial_template_name = "django_tables2/generic_form_item.html"
    title_form: str | None = None
    auto_forms_buttons = True

    # These are provided at runtime by the concrete Django CBV parent.
    request: Any = None  # noqa: F811 — re-defined by dispatch()
    model: Any = None
    form_class: Any = None
    queryset: Any = None

    def get_template_names(self) -> list[str]:
        """Return the partial template for htmx requests, otherwise delegate.

        Returns:
            A list of template names to resolve.
        """
        if self.request and getattr(self.request, "htmx", None):
            return [self.partial_template_name]
        return super().get_template_names()  # type: ignore[no-any-return,misc]

    def get_form(self, form_class: Any = None) -> Any:
        """Configure the form with htmx attributes and optional button bar.

        Attaches ``hx-post``, ``hx-target``, and ``hx-swap`` attributes
        when the form is rendered inside a modal identified by ``_mid``.
        Appends the default action buttons unless ``auto_forms_buttons``
        is ``False``.

        Args:
            form_class: The form class to instantiate. Defaults to the
                view's ``form_class`` attribute.

        Returns:
            The configured form instance.
        """
        form = super().get_form(form_class)  # type: ignore[misc]
        if not hasattr(form, "helper"):
            return form
        mid = self.request.GET.get("_mid") if self.request else None
        if mid is None:
            mid = self.request.POST.get("_mid") if self.request else None
        form_id = get_unique_id("form-")
        if mid:
            form.helper.attrs = {
                "id": form_id,
                "hx-post": f"{self.request.path}?_mid={mid}",
                "hx-target": f"#modal-{mid}-body",
                "hx-swap": "innerHTML",
            }
        else:
            form.helper.attrs = {"id": form_id}
            form.helper.form_action = self.request.path

        if self.auto_forms_buttons and getattr(form.helper, "layout", None) is not None:
            form.helper._usar_modal = bool(mid)
            if not mid and not getattr(form.helper, "back_url", None):
                with contextlib.suppress(Exception):
                    form.helper.back_url = reverse(f"list-view-{self.get_slugname()}")  # type: ignore[attr-defined]
            form.helper.layout.fields.append(get_form_buttons())

        return form

    def _get_model(self) -> Any:
        """Resolve the model class from the view or its form class.

        Returns:
            The model class, or ``None`` if it cannot be determined.
        """
        if self.model:
            return self.model
        return getattr(getattr(self.form_class, "_meta", None), "model", None)

    def get_queryset(self) -> Any:
        """Return the queryset, falling back to the model's default manager.

        When neither ``model`` nor ``queryset`` is set on the view, tries
        to infer the model from the form class and return all instances.

        Returns:
            A QuerySet instance.
        """
        if self.model is None and self.queryset is None:
            model = self._get_model()
            if model:
                return model._default_manager.all()
        return super().get_queryset()  # type: ignore[misc]

    def form_valid(self, form: Any) -> HttpResponse:
        """Handle a valid form submission, triggering htmx refresh when needed.

        For htmx requests returns an empty response with the
        ``HX-Refresh`` header set to ``"true"`` so the client reloads the
        table. Otherwise delegates to the parent.

        Args:
            form: The validated form instance.

        Returns:
            An HTTP response.
        """
        response = super().form_valid(form)  # type: ignore[misc]
        if self.request and getattr(self.request, "htmx", None):
            htmx_response = HttpResponse()
            htmx_response["HX-Refresh"] = "true"
            return htmx_response
        return response  # type: ignore[no-any-return]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Extend the template context with form metadata.

        Adds ``partial_template_name`` and ``title_form`` to the context
        for use by the generic form template.

        Args:
            **kwargs: Context data from the parent view.

        Returns:
            The combined context dictionary.
        """
        context = super().get_context_data(**kwargs)  # type: ignore[misc]
        context["partial_template_name"] = self.partial_template_name
        context["title_form"] = self.title_form
        return context  # type: ignore[no-any-return]

    def get_success_url(self) -> str:
        """Redirect to the list view after a successful form submission.

        Returns:
            The URL of the list view for this model.
        """
        return reverse(f"list-view-{self.get_slugname()}")  # type: ignore[attr-defined]
