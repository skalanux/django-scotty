import uuid

from django.conf import settings

from django_scotty.constants import (
    BTN_PRIMARY,
    BUTTONS_VARIANTS,
    STYLE_SOLID,
    VARIANT_PRIMARY,
)


__all__ = [
    "get_scotty_setting",
    "BUTTON_VARIANT_DEFAULTS",
    "get_button_class",
    "generar_id_valido",
    "get_unique_id",
]


def get_scotty_setting(key, default=None):
    config = getattr(settings, "SCOTTY_CONFIG", {})
    return config.get(key, default)


BUTTON_VARIANT_DEFAULTS = {
    "primary": {"outline": "btn-outline-primary", "solid": "btn-primary"},
    "secondary": {"outline": "btn-outline-secondary", "solid": "btn-secondary"},
    "success": {"outline": "btn-outline-success", "solid": "btn-success"},
    "danger": {"outline": "btn-outline-danger", "solid": "btn-danger"},
    "warning": {"outline": "btn-outline-warning", "solid": "btn-warning"},
    "info": {"outline": "btn-outline-info", "solid": "btn-info"},
    "light": {"outline": "btn-outline-light", "solid": "btn-light"},
    "dark": {"outline": "btn-outline-dark", "solid": "btn-dark"},
}


def get_button_class(variant=VARIANT_PRIMARY, style=STYLE_SOLID):
    variants = get_scotty_setting(BUTTONS_VARIANTS, BUTTON_VARIANT_DEFAULTS)
    entry = variants.get(variant, BUTTON_VARIANT_DEFAULTS.get(variant, BTN_PRIMARY))
    if isinstance(entry, str):
        return entry
    return entry.get(style, BTN_PRIMARY)


def generar_id_valido(base_id):
    id_sanitizado = base_id.replace(".", "-")
    if id_sanitizado and id_sanitizado[0].isdigit():
        return f"id-{id_sanitizado}"
    return id_sanitizado


def get_unique_id(prefix=""):
    component_id = uuid.uuid1().__str__().replace("-", "")[2:8]
    sanitized_id = generar_id_valido(component_id)
    return f"{prefix}{sanitized_id}"
