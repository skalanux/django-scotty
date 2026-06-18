class TestGenericDetailViewSlugname:
    def test_slugname(self):
        from django_scotty.views.detail import GenericDetailView

        slug = GenericDetailView.get_slugname()
        assert slug == "generic"
