import pytest

from tests.models import DummyItem


@pytest.fixture
def dummy_items(db):  # noqa: ARG001
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
