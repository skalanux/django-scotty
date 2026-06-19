"""Tests for django-scotty template tags and filters.

Covers the ``to_slug`` filter provided by the ``sluguer`` tag library.
"""

from django.template import Context, Template


def test_to_slug_filter():
    """Verify the ``to_slug`` filter converts a string to a lowercase slug."""
    t = Template("{% load sluguer %}{{ value|to_slug }}")
    rendered = t.render(Context({"value": "Hello World 123!"}))
    assert rendered.strip() == "hello-world-123"
