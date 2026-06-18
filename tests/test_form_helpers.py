from crispy_forms.helper import FormHelper
from django.template.context import Context

from django_scotty.form_helpers import CloseButton, get_form_buttons


class TestCloseButton:
    def _make_form(self, helper):
        return type("F", (), {"helper": helper})()

    def test_modal_context(self):
        helper = FormHelper()
        helper._usar_modal = True
        f = self._make_form(helper)
        html = CloseButton("").render(f, Context())
        assert 'data-bs-dismiss="modal"' in html
        assert "Cerrar" in html

    def test_full_page_context(self):
        helper = FormHelper()
        helper._usar_modal = False
        helper.back_url = "/some-list/"
        f = self._make_form(helper)
        html = CloseButton("").render(f, Context())
        assert 'href="/some-list/"' in html
        assert "Volver" in html

    def test_full_page_no_back_url(self):
        helper = FormHelper()
        helper._usar_modal = False
        f = self._make_form(helper)
        html = CloseButton("").render(f, Context())
        assert 'href="#"' in html


class TestGetFormButtons:
    def test_returns_div_with_two_children(self):
        buttons = get_form_buttons()
        assert hasattr(buttons, "fields")
        assert len(buttons.fields) == 2
