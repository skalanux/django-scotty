"""Create-related generic views for the django-scotty framework."""

from django.views.generic import CreateView

from django_scotty.mixins import HtmxFormMixin


class GenericCreateView(HtmxFormMixin, CreateView):
    """Create view with htmx modal support.

    Combines Django's CreateView with HtmxFormMixin to handle form
    submissions via htmx, enabling modal-based creation workflows.

    Attributes:
        model: The Django model to create instances of.
        form_class: The form class used for validation and rendering.
        template_name: Template path for the create form.
    """

    @classmethod
    def get_slugname(cls) -> str:
        """Derive the URL slug from the class name.

        Strips the ``createview`` suffix and lowers the remaining name.

        Returns:
            The slug string, e.g. ``"category"`` for ``CategoryCreateView``.
        """
        return cls.__name__.lower().removesuffix("createview")
