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
    """

    request: Any  # Django HttpRequest — injected by the view's dispatch()
    paginate_by: int

    def get_queryset(self) -> Any:
        return super().get_queryset()  # type: ignore[misc]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
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
        if self.request and getattr(self.request, "htmx", None):
            return [self.partial_template_name]
        return super().get_template_names()  # type: ignore[no-any-return,misc]

    def get_form(self, form_class: Any = None) -> Any:
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
        if self.model:
            return self.model
        return getattr(getattr(self.form_class, "_meta", None), "model", None)

    def get_queryset(self) -> Any:
        if self.model is None and self.queryset is None:
            model = self._get_model()
            if model:
                return model._default_manager.all()
        return super().get_queryset()  # type: ignore[misc]

    def form_valid(self, form: Any) -> HttpResponse:
        response = super().form_valid(form)  # type: ignore[misc]
        if self.request and getattr(self.request, "htmx", None):
            htmx_response = HttpResponse()
            htmx_response["HX-Refresh"] = "true"
            return htmx_response
        return response  # type: ignore[no-any-return]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)  # type: ignore[misc]
        context["partial_template_name"] = self.partial_template_name
        context["title_form"] = self.title_form
        return context  # type: ignore[no-any-return]

    def get_success_url(self) -> str:
        return reverse(f"list-view-{self.get_slugname()}")  # type: ignore[attr-defined]
