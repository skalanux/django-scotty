import contextlib
import logging

from django.core.paginator import EmptyPage, Paginator
from django.http import Http404, HttpResponse
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
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
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
    template_name = "django_tables2/generic_form.html"
    partial_template_name = "django_tables2/generic_form_item.html"
    title_form = None
    auto_forms_buttons = True

    def get_template_names(self):
        if self.request.htmx:
            return [self.partial_template_name]
        return super().get_template_names()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not hasattr(form, "helper"):
            return form
        mid = self.request.GET.get("_mid") or self.request.POST.get("_mid")
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
                    form.helper.back_url = reverse(
                        f"list-view-{self.get_slugname()}"
                    )
            form.helper.layout.fields.append(get_form_buttons())

        return form

    def _get_model(self):
        if self.model:
            return self.model
        return getattr(getattr(self.form_class, "_meta", None), "model", None)

    def get_queryset(self):
        if self.model is None and self.queryset is None:
            model = self._get_model()
            if model:
                return model._default_manager.all()
        return super().get_queryset()

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.htmx:
            htmx_response = HttpResponse()
            htmx_response["HX-Refresh"] = "true"
            return htmx_response
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["partial_template_name"] = self.partial_template_name
        context["title_form"] = self.title_form
        return context

    def get_success_url(self):
        return reverse(f"list-view-{self.get_slugname()}")
