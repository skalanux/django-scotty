"""Test models for django-scotty.

Provides DummyItem, a minimal Django model used by all test views and fixtures.
"""

from django.db import models


class DummyItem(models.Model):
    """A minimal test model with common field types for CRUD and list tests.

    Attributes:
        name: CharField for the item name.
        description: TextField with an optional description.
        active: BooleanField indicating active status.
        amount: DecimalField for numeric amount values.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    active = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        app_label = "tests"
        ordering = ["pk"]

    def __str__(self):
        """Return the human-readable representation of the item.

        Returns:
            str: The item name.
        """
        return self.name
