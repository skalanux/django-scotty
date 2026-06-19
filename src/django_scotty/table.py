"""Table classes for django-scotty.

Provides an extended django-tables2 ``Table`` with built-in action
buttons (edit, delete, custom actions) and view-related metadata.
"""

import logging
from typing import Any

import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import SafeText

from django_scotty.constants import BTN_DANGER, BTN_PRIMARY, BTN_WARNING

logger = logging.getLogger(__name__)

__all__ = [
    "ActionTable",
]


class ActionTable(tables.Table):
    """Extends django-tables2 Table with an acciones column and action buttons.

    Attributes:
        view: The parent view instance, set at runtime.
        updateview_class: View class for the edit action.
        update_url_name: URL name for the edit endpoint.
        deleteview_class: View class for the delete action.
        delete_url_name: URL name for the delete endpoint.
        usar_modal: Whether actions should open in modals.
        unique_id: Unique identifier for modal scoping.
        url_action_method: URL name for custom action endpoints.
        title: Table display title.
        subtitle: Optional table subtitle.
        view_only: When True, hides all action buttons.
        show_boton_nuevo: Whether to show a "new" button.
        create_url: URL for the create action.
        empty_text: Message shown when the table has no rows.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the table with action configuration.

        Pops custom keyword arguments before passing the rest to the
        parent ``Table`` initializer.

        Args:
            *args: Positional arguments forwarded to ``tables.Table``.
            **kwargs: Keyword arguments, may include ``available_actions``
                and ``post_paginate_hook``.
        """
        self.action_columns = kwargs.pop("available_actions", [])
        self.post_paginate_hook = kwargs.pop("post_paginate_hook", None)
        super().__init__(*args, **kwargs)

    acciones = tables.Column(verbose_name="Acciones", orderable=False, empty_values=())

    # Attributes set dynamically at runtime by the view
    view: Any = None
    updateview_class: Any = None
    update_url_name: str | None = None
    deleteview_class: Any = None
    delete_url_name: str | None = None
    usar_modal: bool = False
    unique_id: str = ""
    url_action_method: str | None = None
    title: str = ""
    subtitle: str | None = None
    view_only: bool = False
    show_boton_nuevo: bool = False
    create_url: str | None = None
    empty_text: str = ""

    def get_ver_link(self, url: str) -> SafeText:
        """Render a "view" link button for the given URL.

        Args:
            url: The target URL for the link.

        Returns:
            A safe HTML anchor element.
        """
        return SafeText(f'<a href="{url}" class="btn boton-ver"></a>')

    def render_acciones(self, record: Any) -> SafeText:  # type: ignore[override]
        """Render the action buttons column for a single record.

        Builds edit, delete, and custom action buttons depending on which
        view classes and URL names are configured on the table. Custom
        actions with a ``condition`` callable are only rendered when the
        condition passes. Multiple custom actions are grouped into a
        dropdown menu.

        Args:
            record: The row object being rendered.

        Returns:
            Safe HTML containing the action buttons.
        """
        rendered_edit = SafeText("")
        if getattr(self, "updateview_class", None) is not None:
            try:
                edit_url = reverse(self.update_url_name, kwargs={"pk": record.pk})
                if getattr(self, "usar_modal", False):
                    modal_id = f"modal-{self.unique_id}"
                    rendered_edit = SafeText(
                        f'<button class="btn {BTN_WARNING} btn-sm"'
                        f' hx-get="{edit_url}?_mid={self.unique_id}"'
                        f' hx-target="#{modal_id}-body"'
                        f' hx-swap="innerHTML"'
                        f' data-bs-toggle="modal"'
                        f' data-bs-target="#{modal_id}">Editar</button>'
                    )
                else:
                    rendered_edit = SafeText(
                        f'<button class="btn {BTN_WARNING} btn-sm"'
                        f' hx-get="{edit_url}"'
                        f' hx-target="#main-content"'
                        f' hx-swap="innerHTML"'
                        f' hx-push-url="true">Editar</button>'
                    )
            except Exception as err:
                logging.error(f"[SCOTTY LOADER] Error rendering edit button {err}")

        rendered_delete = SafeText("")
        if getattr(self, "deleteview_class", None) is not None:
            try:
                delete_url = reverse(self.delete_url_name, kwargs={"pk": record.pk})
                delete_mid = f"delete-{self.unique_id}"
                modal_id = f"modal-{delete_mid}"
                rendered_delete = SafeText(
                    f'<button class="btn {BTN_DANGER} btn-sm ms-1"'
                    f' hx-get="{delete_url}?_mid={delete_mid}"'
                    f' hx-target="#{modal_id}-body"'
                    f' hx-swap="innerHTML"'
                    f' data-bs-toggle="modal"'
                    f' data-bs-target="#{modal_id}">Eliminar</button>'
                )
            except Exception:
                pass

        if getattr(self, "url_action_method", None) is None:
            return rendered_edit + rendered_delete

        url = reverse(self.url_action_method)
        if len(self.action_columns) == 1:
            accion = self.action_columns[0]
            accion_method = getattr(self.view, accion[0])

            try:
                condition_result = accion_method.condition(record, self.view.request)
                if not condition_result:
                    return rendered_edit + rendered_delete
            except Exception:
                return rendered_edit + rendered_delete

            show_confirm = getattr(accion_method, "show_confirm", False)
            confirm_attr = (
                'hx-confirm="¿Está seguro que desea realizar esta acción?"'
                if show_confirm
                else ""
            )
            hx_post_url = f"{url}?pk={record.pk}&action={accion[0]}"
            button_html = SafeText(
                f"""<button hx-post="{hx_post_url}"
                    hx-trigger="click"
                    hx-swap="outerHTML"
                    class="btn {BTN_PRIMARY}"
                    hx-indicator="#spinner-load"
                    type="btn"
                    {confirm_attr}>{accion[1]}</button>"""
            )
            return rendered_edit + rendered_delete + SafeText(button_html)
        elif len(self.action_columns) > 1:
            rendered_actions = SafeText("")
            for accion in self.action_columns:
                accion_method = getattr(self.view, accion[0])

                try:
                    condition_result = accion_method.condition(
                        record, self.view.request
                    )
                    if not condition_result:
                        continue
                except Exception:
                    pass

                show_confirm = getattr(accion_method, "show_confirm", False)
                confirm_attr = (
                    'hx-confirm="¿Está seguro que desea realizar esta acción?"'
                    if show_confirm
                    else ""
                )
                action_html = f"""<li>
                    <a hx-post=\"{url}?pk={record.pk}&action={accion[0]}\"
                    hx-trigger=\"click\"
                    hx-swap=\"outerHTML\"
                    hx-indicator=\"#spinner-load\"
                    class=\"dropdown-item\"
                    {confirm_attr}>{accion[1]}</a>
                    </li>"""
                rendered_actions += SafeText(action_html)

            if not rendered_actions:
                return rendered_edit + rendered_delete

            return (
                rendered_edit
                + rendered_delete
                + SafeText(f"""
                            <div class="btn-group">
                            <button type="button"
                            class="btn {BTN_PRIMARY} dropdown-toggle"
                            data-bs-toggle="dropdown" aria-expanded="false">
                                Acciones
                            </button>
                            <ul class="dropdown-menu">
                                {rendered_actions}
                            </ul>
                            </div>""")
            )
        else:
            return rendered_edit + rendered_delete

    def paginate(self, *args: Any, **kwargs: Any) -> None:
        """Paginate the table and invoke the post-paginate hook if set.

        Calls the optional ``post_paginate_hook`` callback with the
        current page's object list after pagination completes.

        Args:
            *args: Positional arguments forwarded to ``Table.paginate()``.
            **kwargs: Keyword arguments forwarded to ``Table.paginate()``.
        """
        super().paginate(*args, **kwargs)
        if self.page and self.post_paginate_hook:
            self.post_paginate_hook(self.page.object_list)
