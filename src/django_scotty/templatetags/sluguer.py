"""Template filters for django-scotty.

Provides custom template tags used across django-scotty templates.
"""

from django import template
from django.utils.text import slugify

register = template.Library()


@register.filter
def to_slug(value: str) -> str:
    """Convert a string into a URL-friendly slug.

    Args:
        value: The string to slugify.

    Returns:
        The slugified version of the input string.
    """
    return slugify(value)
