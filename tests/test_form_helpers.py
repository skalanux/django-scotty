"""Tests for django_scotty.form_helpers.

Covers CloseButton rendering in modal and full-page contexts, and the
get_form_buttons helper layout.
"""

from crispy_forms.helper import FormHelper
from django.template.context import Context

from django_scotty.form_helpers import CloseButton, get_form_buttons


class TestCloseButton:
    """Tests for the ``CloseButton`` layout object in different form contexts."""

    def _make_form(self, helper):
        """Create a minimal form-like object with the given helper.

        Args:
            helper: A crispy-forms FormHelper instance.

        Returns:
            type: A dummy form object whose ``helper`` attribute is set.
        """
        return type("F", (), {"helper": helper})()

    def test_modal_context(self):
        """Verify the close button renders Bootstrap dismiss
        attributes in modal mode."""
        helper = FormHelper()
        helper._usar_modal = True
        f = self._make_form(helper)
        html = CloseButton("").render(f, Context())
        assert 'data-bs-dismiss="modal"' in html
        assert "Cerrar" in html

    def test_full_page_context(self):
        """Verify the close button renders a back link in full-page mode."""
        helper = FormHelper()
        helper._usar_modal = False
        helper.back_url = "/some-list/"
        f = self._make_form(helper)
        html = CloseButton("").render(f, Context())
        assert 'href="/some-list/"' in html
        assert "Volver" in html

    def test_full_page_no_back_url(self):
        """Verify the close button renders ``href=\"#\"`` when no back_url is set."""
        helper = FormHelper()
        helper._usar_modal = False
        f = self._make_form(helper)
        html = CloseButton("").render(f, Context())
        assert 'href="#"' in html


class TestGetFormButtons:
    """Tests for the ``get_form_buttons`` helper function."""

    def test_returns_div_with_two_children(self):
        """Verify ``get_form_buttons`` returns a layout object with two fields."""
        buttons = get_form_buttons()
        assert hasattr(buttons, "fields")
        assert len(buttons.fields) == 2
