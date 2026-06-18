from django.views.generic import UpdateView

from django_scotty.mixins import HtmxFormMixin


class GenericUpdateView(HtmxFormMixin, UpdateView):
    @classmethod
    def get_slugname(cls) -> str:
        return cls.__name__.lower().removesuffix("updateview")
