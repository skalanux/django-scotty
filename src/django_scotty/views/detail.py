from typing import Any

from django.views.generic import DetailView


class GenericDetailView(DetailView):
    template_name = "django_tables2/generic_detail.html"
    exclude_fields: list[str] = ["id"]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        instance = context["object"]

        field_list: list[dict[str, Any]] = []
        for field in instance._meta.get_fields():
            if not field.concrete or field.many_to_many:
                continue

            if field.name in self.exclude_fields:
                continue

            value = getattr(instance, field.name)

            get_display_method = f"get_{field.name}_display"
            if hasattr(instance, get_display_method):
                value = getattr(instance, get_display_method)()

            if value is None:
                value = "—"

            if isinstance(value, bool):
                value = "Sí" if value else "No"

            try:
                field_list.append(
                    {
                        "label": field.verbose_name.capitalize(),
                        "value": value,
                    }
                )
            except Exception:
                field_list.append(
                    {
                        "label": field.name.capitalize(),
                        "value": value,
                    }
                )

        context["field_list"] = field_list
        context["title"] = (
            f"Detalle de {instance._meta.verbose_name.capitalize()} {instance.id}"
        )
        return context

    @classmethod
    def get_slugname(cls) -> str:
        trimed_view_name = cls.__name__.lower().removesuffix("detailview")
        return trimed_view_name
