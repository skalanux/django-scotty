from django_scotty.views.create import GenericCreateView
from django_scotty.views.delete import GenericDeleteView
from django_scotty.views.update import GenericUpdateView


class TestGenericCreateViewSlugname:
    def test_slugname_removes_createview(self):
        slug = GenericCreateView.get_slugname()
        assert slug == "generic"


class TestGenericUpdateViewSlugname:
    def test_slugname_removes_updateview(self):
        slug = GenericUpdateView.get_slugname()
        assert slug == "generic"


class TestGenericDeleteViewSlugname:
    def test_slugname_removes_deleteview(self):
        slug = GenericDeleteView.get_slugname()
        assert slug == "generic"
