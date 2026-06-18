from typing import Any

from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import DeleteView


class GenericDeleteView(DeleteView):
    template_name = "django_tables2/generic_delete_confirm.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["mid"] = self.request.GET.get("_mid") or self.request.POST.get("_mid")
        return context

    def form_valid(self, form: Any) -> HttpResponse:
        response = super().form_valid(form)
        if self.request.htmx:
            htmx_response = HttpResponse()
            htmx_response["HX-Refresh"] = "true"
            return htmx_response
        return response

    def get_success_url(self) -> str:
        return reverse(f"list-view-{self.get_slugname()}")

    @classmethod
    def get_slugname(cls) -> str:
        return cls.__name__.lower().removesuffix("deleteview")
