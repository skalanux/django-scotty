"""Tests for slugname derivation on CRUD views.

Verifies that ``get_slugname()`` strips the ``CreateView``, ``UpdateView``,
and ``DeleteView`` suffixes correctly.
"""

from django_scotty.views.create import GenericCreateView
from django_scotty.views.delete import GenericDeleteView
from django_scotty.views.update import GenericUpdateView


class TestGenericCreateViewSlugname:
    """Tests for ``GenericCreateView.get_slugname``."""

    def test_slugname_removes_createview(self):
        """Verify the slug strips the ``CreateView`` suffix."""
        slug = GenericCreateView.get_slugname()
        assert slug == "generic"


class TestGenericUpdateViewSlugname:
    """Tests for ``GenericUpdateView.get_slugname``."""

    def test_slugname_removes_updateview(self):
        """Verify the slug strips the ``UpdateView`` suffix."""
        slug = GenericUpdateView.get_slugname()
        assert slug == "generic"


class TestGenericDeleteViewSlugname:
    """Tests for ``GenericDeleteView.get_slugname``."""

    def test_slugname_removes_deleteview(self):
        """Verify the slug strips the ``DeleteView`` suffix."""
        slug = GenericDeleteView.get_slugname()
        assert slug == "generic"
