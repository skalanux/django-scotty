from django.template import Context, Template


def test_to_slug_filter():
    t = Template("{% load sluguer %}{{ value|to_slug }}")
    rendered = t.render(Context({"value": "Hello World 123!"}))
    assert rendered.strip() == "hello-world-123"
