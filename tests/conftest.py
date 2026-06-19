"""Test fixtures and configuration for django-scotty tests.

Provides shared fixtures used across test modules.
"""

import pytest

from tests.models import DummyItem


@pytest.fixture
def dummy_items(db):  # noqa: ARG001
    """Create 15 DummyItem instances for pagination and list tests.

    Args:
        db: Django database fixture.

    Returns:
        list[DummyItem]: A list of 15 DummyItem objects named Item 0..Item 14.
    """
    items = [
        DummyItem.objects.create(
            name=f"Item {i}",
            description=f"Description {i}",
            active=(i % 2 == 0),
            amount=i * 10,
        )
        for i in range(15)
    ]
    return items
