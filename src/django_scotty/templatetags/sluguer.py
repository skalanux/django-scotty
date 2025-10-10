from django import template
from django.utils.text import slugify

register = template.Library()


@register.filter
def to_slug(value):
    """
    Convierte un string en un slug.
    """
    return slugify(value)
