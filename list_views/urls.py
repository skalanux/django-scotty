"""URL patterns for django_scotty.

Example usage:
    
    # In your app's urls.py:
    from django_scotty.list_views.helpers import add_urls
    from . import views_module1, views_module2
    
    views_modules = [
        views_module1,
        views_module2,
    ]
    
    urlpatterns = add_urls(views_modules)
"""

from .helpers import add_urls

# Default empty urlpatterns
# Users should create their own URL patterns in their Django app
urlpatterns = []
