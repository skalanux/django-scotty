# Django Scotty

[![CI](https://github.com/jmschillaci/django-scotty/actions/workflows/ci.yml/badge.svg)](https://github.com/jmschillaci/django-scotty/actions/workflows/ci.yml)
[![Python Versions](https://img.shields.io/badge/python-3.12%20|%203.13-blue)](https://github.com/jmschillaci/django-scotty)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Advanced table views for Django with CRUD operations, filtering, export, and htmx-powered modals.

Built on top of [django-tables2](https://django-tables2.readthedocs.io/), [django-filter](https://django-filter.readthedocs.io/), and [django-cotton](https://django-cotton.com/).

---

## Features

- **CRUD Views** — Ready-to-use Create, Read, Update, Delete views with a consistent look
- **Table Views** — Filterable, sortable, paginated table views via django-tables2
- **Filtering** — Integrated django-filters with Bootstrap 5 UI
- **Export to Excel** — One-click export to XLSX via tablib
- **htmx Modals** — Create/Update forms in modals with zero custom JS
- **Pagination Fix** — Invalid page numbers redirect gracefully instead of 404/500
- **Bulk Actions** — Define custom actions on table rows
- **Modern UI** — django-cotton components + Bootstrap 5 + crispy-forms

---

## Requirements

- Python >= 3.12
- Django >= 5.1 (via django-cotton constraint)
- django-cotton >= 2.1
- django-tables2 >= 2.7
- django-filter >= 25.1
- django-crispy-forms >= 2.4 + crispy-bootstrap5
- tablib >= 3.8 (with XLSX support)

---

## Installation

```bash
pip install django-scotty
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install django-scotty
```

Add the required apps to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "django_cotton",
    "django_tables2",
    "django_filters",
    "django_scotty",
    ...
]
```

---

## Quick Start

### List View (table)

```python
# views.py
import django_tables2 as tables
from django_scotty.views import CottonTableView
from .models import Product


class ProductTable(tables.Table):
    class Meta:
        model = Product
        fields = ["name", "price", "stock", "category"]


class ProductListView(CottonTableView):
    model = Product
    table_class = ProductTable
    title = "Products"
    paginate_by = 25
```

```python
# urls.py
from django.urls import path
from .views import ProductListView

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
]
```

### Create View

```python
from django_scotty.views import GenericCreateView
from .models import Product
from .forms import ProductForm


class ProductCreateView(GenericCreateView):
    model = Product
    form_class = ProductForm
    title_form = "New Product"
```

### Update View

```python
from django_scotty.views import GenericUpdateView


class ProductUpdateView(GenericUpdateView):
    model = Product
    form_class = ProductForm
    title_form = "Edit Product"
```

### Delete View

```python
from django_scotty.views import GenericDeleteView


class ProductDeleteView(GenericDeleteView):
    model = Product
```

### Detail View

```python
from django_scotty.views import GenericDetailView


class ProductDetailView(GenericDetailView):
    model = Product
```

### URL auto-discovery

For a cleaner setup, gather all views from a `scotty/` directory in your app:

```python
# urls.py
from django_scotty.urls import load_scotty_urls, add_urls
from myapp import scotty

urlpatterns = [
    *add_urls([scotty]),
]

# or auto-discover from an app:
urlpatterns = [
    *load_scotty_urls("myapp"),
]
```

---

## Filtering

Add a `FilterSet` and wire it to your list view:

```python
import django_filters


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            "name": ["exact", "icontains"],
            "category": ["exact"],
            "price": ["gte", "lte"],
        }


class ProductListView(CottonTableView):
    model = Product
    table_class = ProductTable
    filterset_class = ProductFilter
    paginate_by = 25
```

---

## htmx Modal Forms

`GenericCreateView` and `GenericUpdateView` render inside an htmx-powered Bootstrap modal by default when the request includes the `HX-Request` header.

On success, they return an `HX-Refresh` response that tells the parent page to reload the table. No JavaScript required beyond the htmx library.

```python
class ProductCreateView(GenericCreateView):
    model = Product
    form_class = ProductForm
    title_form = "New Product"
    auto_forms_buttons = True  # adds Save / Cancel buttons automatically
```

---

## Export

Every `CottonTableView` includes a built-in "Export to XLSX" button. The export uses [tablib](https://tablib.readthedocs.io/) and respects the current filter/sort state.

Customize the filename:

```python
class ProductListView(CottonTableView):
    model = Product
    table_class = ProductTable
    export_name = "products_report"  # default: slugified model name
```

---

## Configuration

Set `SCOTTY_CONFIG` in your Django settings:

```python
SCOTTY_CONFIG = {
    "BUTTON_VARIANT": "primary",       # default button variant
    "BUTTON_VARIANT_DANGER": "danger", # delete button variant
    "BUTTON_STYLE": "solid",           # solid (filled) or outline
}
```

Available variants: `primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark`.

---

## Development

### Setup

```bash
# Clone the repo
git clone https://github.com/jmschillaci/django-scotty.git
cd django-scotty

# Install with dev dependencies
uv sync --group dev
```

### Run tests

```bash
# Full suite
uv run pytest -v --cov=src/django_scotty

# With tox (requires tox and the Python versions installed)
tox
tox -e lint        # ruff checks only
tox -e type        # mypy only
tox -e py312       # tests on Python 3.12 only
```

### Lint & type check

```bash
uv run ruff check src/django_scotty tests
uv run ruff format --check src/django_scotty tests
uv run mypy src/django_scotty
```

---

## Requirements

Full dependency list in [`pyproject.toml`](pyproject.toml).

| Dependency | Minimum Version |
|---|---|
| Python | 3.12 |
| Django | 5.1+ |
| django-cotton | 2.1 |
| django-tables2 | 2.7 |
| django-filter | 25.1 |
| django-crispy-forms | 2.4 |
| crispy-bootstrap5 | 2024.10 |
| tablib[xlsx] | 3.8 |
| django-htmx | 1.26 |

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Add tests for your changes
4. Ensure all checks pass (`uv run pytest`, `uv run mypy`, `uv run ruff check`)
5. Submit a Pull Request

---

## License

MIT — see [LICENSE](LICENSE).

---

## Credits

Built with:

- [Django](https://www.djangoproject.com/)
- [django-tables2](https://django-tables2.readthedocs.io/)
- [django-filter](https://django-filter.readthedocs.io/)
- [django-cotton](https://django-cotton.com/)
- [django-crispy-forms](https://django-crispy-forms.readthedocs.io/)
- [tablib](https://tablib.readthedocs.io/)
- [htmx](https://htmx.org/)
