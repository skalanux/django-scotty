# Django Scotty

Advanced table views for Django with filters, exports, and bulk actions.

## Features

- 🚀 **Enhanced Table Views**: Built on top of django-tables2 with additional functionality
- 🎯 **Filtering**: Integrated django-filters support with beautiful UI
- 📊 **Export to Excel**: Export table data to XLS/XLSX formats using tablib
- ⚡ **Bulk Actions**: Perform actions on multiple records at once
- 🎨 **Modern UI**: Beautiful templates using django-cotton and Bootstrap
- 🔧 **Customizable**: Easy to extend and customize for your needs

## Installation

Install using pip:

```bash
pip install django-scotty
```

Or using uv:

```bash
uv pip install django-scotty
```

## Quick Start

1. Add `django_scotty` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_cotton',
    'django_tables2',
    'django_filters',
    'django_scotty',
    ...
]
```

2. Create a table view in your `views.py`:

```python
from django_scotty.list_views.helpers import CottonTableView
import django_tables2 as tables
from .models import YourModel

class YourModelTable(tables.Table):
    class Meta:
        model = YourModel
        fields = ['field1', 'field2', 'field3']

class YourModelListView(CottonTableView):
    model = YourModel
    table_class = YourModelTable
    title = 'Your Model List'
    paginate_by = 25
```

3. Add to your `urls.py`:

```python
from django.urls import path
from .views import YourModelListView

urlpatterns = [
    path('your-model/', YourModelListView.as_view(), name='yourmodel-list'),
]
```

## Advanced Features

### Filtering

Add a FilterSet to enable filtering:

```python
import django_filters

class YourModelFilter(django_filters.FilterSet):
    class Meta:
        model = YourModel
        fields = ['field1', 'field2']

class YourModelListView(CottonTableView):
    model = YourModel
    table_class = YourModelTable
    filterset_class = YourModelFilter
```

### Export to Excel

Export functionality is enabled by default. Users can click the "Export to XLS" button.

### Bulk Actions

Define custom actions in your view:

```python
from django_scotty.list_views.helpers import CottonTableView, action

class YourModelListView(CottonTableView):
    model = YourModel
    table_class = YourModelTable
    
    @action(short_description="Mark as processed")
    def mark_processed(self, request, queryset):
        queryset.update(processed=True)
        return self.success_message("Records marked as processed")
```

## Requirements

- Python >= 3.8
- Django >= 3.2
- django-cotton >= 0.9.0
- django-tables2 >= 2.4.0
- tablib[xls,xlsx] >= 3.0.0
- django-filter >= 22.1

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

Built with:
- [Django](https://www.djangoproject.com/)
- [django-tables2](https://django-tables2.readthedocs.io/)
- [django-filter](https://django-filter.readthedocs.io/)
- [django-cotton](https://django-cotton.com/)
- [tablib](https://tablib.readthedocs.io/)
