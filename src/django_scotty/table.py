import logging

import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import SafeText

from django_scotty.constants import BTN_DANGER, BTN_PRIMARY, BTN_WARNING

logger = logging.getLogger(__name__)


__all__ = [
    "ActionTable",
]


class ActionTable(tables.Table):
    def __init__(self, *args, **kwargs):
        self.action_columns = kwargs.pop("available_actions", [])
        self.post_paginate_hook = kwargs.pop("post_paginate_hook", None)
        super().__init__(*args, **kwargs)

    acciones = tables.Column(verbose_name="Acciones", orderable=False, empty_values=())

    def get_ver_link(self, url):
        return SafeText(f'<a href="{url}" class="btn boton-ver"></a>')

    def render_acciones(self, record):
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

        rendered_actions = SafeText("")
        url = reverse(self.url_action_method)
        if len(self.action_columns) == 1:
            accion = self.action_columns[0]
            accion_method = getattr(self.view, accion[0])

            try:
                condition_result = accion_method.condition(record, self.request)
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
                    condition_result = accion_method.condition(record, self.request)
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

    def paginate(self, *args, **kwargs):
        super().paginate(*args, **kwargs)
        if self.page and self.post_paginate_hook:
            self.post_paginate_hook(self.page.object_list)
