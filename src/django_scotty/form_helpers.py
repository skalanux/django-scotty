"""Form layout helpers for django-scotty.

Provides reusable crispy-forms layout components such as close/back
buttons and the default form button bar.
"""

from typing import Any

from crispy_forms.layout import HTML, Div, Submit
from django.template.context import Context


class CloseButton(HTML):
    """Render a Close/Back button depending on modal usage."""

    def render(self, form: Any, context: Context, **kwargs: Any) -> str:
        """Render a close or back button depending on modal context.

        When the form is displayed inside a modal, renders a Bootstrap
        dismiss button. Otherwise renders a link back to the previous URL.

        Returns:
            The rendered HTML string.
        """
        usar_modal = getattr(form.helper, "_usar_modal", False)
        if usar_modal:
            html = (
                '<button type="button" class="btn btn-outline-primary"'
                ' data-bs-dismiss="modal">Cerrar</button>'
            )
        else:
            back_url = getattr(form.helper, "back_url", "#")
            html = f'<a href="{back_url}" class="btn btn-outline-primary">Volver</a>'
        self.html = html
        return super().render(form, context, **kwargs)


def get_form_buttons() -> Div:
    """Build the default form button bar with close/back and submit buttons.

    Returns:
        A crispy-forms ``Div`` layout object containing the buttons.
    """
    return Div(
        CloseButton(""),
        Submit("submit", "Guardar", css_class="btn btn-primary"),
        css_class="d-flex justify-content-between gap-2 mt-3",
    )
