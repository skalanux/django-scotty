# Development Guide for Django Scotty

## Building the Package with uv

### Prerequisites

Install `uv` if you haven't already:

```bash
pip install uv
```

### Building the Package

1. **Clean previous builds** (optional):

```bash
rm -rf dist/ build/ *.egg-info
```

2. **Build the package**:

```bash
uv build
```

This will create both `.tar.gz` (source distribution) and `.whl` (wheel) files in the `dist/` directory.

### Installing Locally for Testing

To test the package locally before publishing:

```bash
# Install in editable mode for development
uv pip install -e .

# Or install from the built wheel
uv pip install dist/django_scotty-0.1.0-py3-none-any.whl
```

### Testing in a Django Project

1. Create a test Django project:

```bash
django-admin startproject testproject
cd testproject
```

2. Install django-scotty:

```bash
uv pip install /path/to/django-scotty/dist/django_scotty-0.1.0-py3-none-any.whl
```

3. Add to `INSTALLED_APPS` in `settings.py`:

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

4. Create a test view and verify everything works.

## Publishing to PyPI

### Test PyPI (Recommended First)

1. Register at [TestPyPI](https://test.pypi.org/account/register/)

2. Create an API token at https://test.pypi.org/manage/account/token/

3. Upload to TestPyPI:

```bash
uv publish --publish-url https://test.pypi.org/legacy/ --token YOUR_TOKEN
```

4. Test installation from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ django-scotty
```

### Production PyPI

1. Register at [PyPI](https://pypi.org/account/register/)

2. Create an API token at https://pypi.org/manage/account/token/

3. Upload to PyPI:

```bash
uv publish --token YOUR_TOKEN
```

Or use environment variables:

```bash
export UV_PUBLISH_TOKEN=your_token_here
uv publish
```

### Alternative: Using twine

If you prefer the traditional approach:

```bash
pip install twine

# Upload to TestPyPI
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Upload to PyPI
twine upload dist/*
```

## Version Management

Update the version in `pyproject.toml` and `django_scotty/__init__.py` before building:

```toml
# pyproject.toml
[project]
version = "0.2.0"
```

```python
# django_scotty/__init__.py
__version__ = '0.2.0'
```

## Development Workflow

1. Make your changes
2. Update version number
3. Update CHANGELOG.md (create one if needed)
4. Build: `uv build`
5. Test locally
6. Publish to TestPyPI
7. Test from TestPyPI
8. Publish to PyPI
9. Create a git tag: `git tag v0.2.0 && git push --tags`

## Updating Dependencies

Dependencies are specified in `pyproject.toml`:

```toml
dependencies = [
    "django>=3.2",
    "django-cotton>=0.9.0",
    ...
]
```

After updating, rebuild the package.

## Running Tests

Add tests in a `tests/` directory and run with pytest:

```bash
uv pip install -e ".[dev]"
pytest
```
