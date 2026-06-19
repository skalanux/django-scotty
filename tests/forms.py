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
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("name"),
            Field("description"),
            Field("active"),
            Field("amount"),
        )
