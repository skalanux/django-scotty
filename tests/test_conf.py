from django.test.utils import override_settings

from django_scotty.conf import (
    BUTTON_VARIANT_DEFAULTS,
    generar_id_valido,
    get_button_class,
    get_scotty_setting,
    get_unique_id,
)


def test_generar_id_valido_replaces_dots():
    assert generar_id_valido("test.id") == "test-id"


def test_generar_id_valido_prefixes_digit_start():
    assert generar_id_valido("123abc") == "id-123abc"


def test_generar_id_valido_unchanged():
    assert generar_id_valido("hello") == "hello"


def test_get_unique_id_prefix():
    uid = get_unique_id("pfx-")
    assert uid.startswith("pfx-")
    assert len(uid) > len("pfx-")


def test_get_unique_id_no_prefix():
    uid = get_unique_id()
    assert isinstance(uid, str)
    assert 6 <= len(uid) <= 9


@override_settings(SCOTTY_CONFIG={"custom_key": "custom_value"})
def test_get_scotty_setting_found():
    assert get_scotty_setting("custom_key") == "custom_value"


def test_get_scotty_setting_not_found():
    assert get_scotty_setting("nonexistent", "fallback") == "fallback"


def test_get_scotty_setting_default_none():
    assert get_scotty_setting("nonexistent") is None


@override_settings(SCOTTY_CONFIG={})
def test_get_scotty_setting_empty_config():
    assert get_scotty_setting("anything") is None


def test_get_button_class_default():
    assert get_button_class() == "btn-primary"


def test_get_button_class_outline():
    assert get_button_class("primary", "outline") == "btn-outline-primary"


def test_get_button_class_variant_outline():
    css = get_button_class("danger", "outline")
    assert css == "btn-outline-danger"


def test_get_button_class_variant_solid():
    css = get_button_class("success", "solid")
    assert css == "btn-success"


def test_get_button_class_unknown_variant():
    css = get_button_class("unknown_variant")
    assert css == "btn-primary"


def test_button_variant_defaults_keys():
    variants = sorted(BUTTON_VARIANT_DEFAULTS)
    for variant in variants:
        assert variant in BUTTON_VARIANT_DEFAULTS
        entry = BUTTON_VARIANT_DEFAULTS[variant]
        assert "outline" in entry
        assert "solid" in entry
        assert entry["solid"].startswith("btn-")
        assert entry["outline"].startswith("btn-outline-")


@override_settings(
    SCOTTY_CONFIG={
        "buttons_variants": {"primary": "my-custom-btn"},
    }
)
def test_get_button_class_config_override_flat():
    assert get_button_class("primary") == "my-custom-btn"


@override_settings(
    SCOTTY_CONFIG={
        "buttons_variants": {
            "primary": {"solid": "my-btn-primary", "outline": "my-btn-outline-primary"},
        },
    }
)
def test_get_button_class_config_override_dict():
    assert get_button_class("primary", "solid") == "my-btn-primary"
    assert get_button_class("primary", "outline") == "my-btn-outline-primary"
