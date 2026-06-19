"""Delete-related generic views for the django-scotty framework."""

from typing import Any

from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import DeleteView


class GenericDeleteView(DeleteView):
    """Delete view with htmx support and custom redirects.

    Extends Django's DeleteView to handle deletion confirmation via a
    modal dialog and triggers an HX-Refresh header when the request
    originates from htmx.

    Attributes:
        model: The Django model whose instances are deleted.
        template_name: Path to the confirmation template.
    """

    template_name = "django_tables2/generic_delete_confirm.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add the modal ID (``_mid``) from request params to the context.

        Args:
            **kwargs: Keyword arguments passed to the parent context.

        Returns:
            The enriched context dictionary with the modal identifier.
        """
        context = super().get_context_data(**kwargs)
        context["mid"] = self.request.GET.get("_mid") or self.request.POST.get("_mid")
        return context

    def form_valid(self, form: Any) -> HttpResponse:
        """Perform the delete and return an htmx-aware response.

        For htmx requests the response carries an ``HX-Refresh`` header
        so the client refreshes the table view. Regular POST requests
        follow the standard redirect.

        Args:
            form: The valid confirmation form.

        Returns:
            An HttpResponse, possibly with the HX-Refresh header set.
        """
        response = super().form_valid(form)
        if self.request.htmx:
            htmx_response = HttpResponse()
            htmx_response["HX-Refresh"] = "true"
            return htmx_response
        return response

    def get_success_url(self) -> str:
        """Redirect to the list view after a successful deletion.

        Returns:
            The URL for the list view corresponding to this model.
        """
        return reverse(f"list-view-{self.get_slugname()}")

    @classmethod
    def get_slugname(cls) -> str:
        """Derive the URL slug from the class name.

        Strips the ``deleteview`` suffix and lowers the remaining name.

        Returns:
            The slug string, e.g. ``"category"`` for ``CategoryDeleteView``.
        """
        return cls.__name__.lower().removesuffix("deleteview")
