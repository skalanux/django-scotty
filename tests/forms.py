"""Form classes used by test views.

Provides the DummyItem ModelForm with crispy-forms layout configuration.
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms

from tests.models import DummyItem


class DummyItemForm(forms.ModelForm):
    """ModelForm for DummyItem with crispy FormHelper."""

    class Meta:
        model = DummyItem
        fields = ["name", "description", "active", "amount"]

    def __init__(self, *args, **kwargs):
        """Initialize the form and attach a crispy FormHelper with field layout.

        Args:
            *args: Positional arguments passed to ModelForm.
            **kwargs: Keyword arguments passed to ModelForm.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("name"),
            Field("description"),
            Field("active"),
            Field("amount"),
        )
