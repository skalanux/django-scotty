"""Update-related generic views for the django-scotty framework."""

from django.views.generic import UpdateView

from django_scotty.mixins import HtmxFormMixin


class GenericUpdateView(HtmxFormMixin, UpdateView):
    """Update view with htmx modal support.

    Combines Django's UpdateView with HtmxFormMixin to handle form
    submissions via htmx, enabling modal-based edit workflows.

    Attributes:
        model: The Django model whose instances are edited.
        form_class: The form class used for validation and rendering.
        template_name: Template path for the update form.
    """

    @classmethod
    def get_slugname(cls) -> str:
        """Derive the URL slug from the class name.

        Strips the ``updateview`` suffix and lowers the remaining name.

        Returns:
            The slug string, e.g. ``"category"`` for ``CategoryUpdateView``.
        """
        return cls.__name__.lower().removesuffix("updateview")
