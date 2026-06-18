from django.views.generic import CreateView

from django_scotty.mixins import HtmxFormMixin


class GenericCreateView(HtmxFormMixin, CreateView):
    @classmethod
    def get_slugname(cls) -> str:
        return cls.__name__.lower().removesuffix("createview")
