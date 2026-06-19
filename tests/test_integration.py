"""Integration tests using Django's TestClient for the full request-response cycle.

Tests exercise the complete stack: URL routing → view → mixins → template render.
"""

from __future__ import annotations

from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from tests.models import DummyItem

pytestmark = [pytest.mark.django_db]


class TestCottonTableViewList:
    """Integration tests for CottonTableView (DummyItemListView)."""

    def test_list_returns_200(
        self,
        client: Client,
        dummy_items: list[DummyItem],
    ) -> None:
        url = reverse("list-view-dummyitem")
        response = client.get(url)
        assert response.status_code == 200

    def test_list_shows_items(
        self, client: Client, dummy_items: list[DummyItem]
    ) -> None:
        url = reverse("list-view-dummyitem")
        response = client.get(url)
        body = response.content.decode()
        for item in dummy_items[:5]:
            assert item.name in body

    def test_list_paginates(
        self,
        client: Client,
        dummy_items: list[DummyItem],
    ) -> None:
        url = reverse("list-view-dummyitem")
        response = client.get(url)
        body = response.content.decode()
        assert "Item 0" in body
        assert "Item 9" in body

    def test_list_page_2(
        self,
        client: Client,
        dummy_items: list[DummyItem],
    ) -> None:
        url = reverse("list-view-dummyitem")
        response = client.get(url, {"page": 2})
        assert response.status_code == 200
        body = response.content.decode()
        assert "Item 10" in body
        assert "Item 14" in body

    def test_list_htmx_returns_partial(
        self,
        client: Client,
        dummy_items: list[DummyItem],
    ) -> None:
        """Htmx request should render only the content block (dummy.html wrapper)."""
        url = reverse("list-view-dummyitem")
        response = client.get(url, HTTP_HX_REQUEST="true")
        body = response.content.decode()
        # dummy.html only has the scotty_content block — no <html> or <body> tags
        assert "<html" not in body
        assert "<body" not in body

    def test_empty_table(self, client: Client) -> None:
        url = reverse("list-view-dummyitem")
        response = client.get(url)
        assert response.status_code == 200

    def test_list_uses_default_template(self, client: Client) -> None:
        """Non-htmx request uses base template with full HTML."""
        url = reverse("list-view-dummyitem")
        response = client.get(url)
        assert "text/html" in response["Content-Type"]


class TestDictTableViewList:
    """Integration tests for DictTableView (DummyItemDictView)."""

    def test_dict_view_returns_200(
        self,
        client: Client,
        dummy_items: list[DummyItem],
    ) -> None:
        url = reverse("list-view-dummyitem-dict")
        response = client.get(url)
        assert response.status_code == 200

    def test_dict_view_shows_items(
        self, client: Client, dummy_items: list[DummyItem]
    ) -> None:
        url = reverse("list-view-dummyitem-dict")
        response = client.get(url)
        body = response.content.decode()
        # DictTableView renders data differently, verify it's present
        for item in dummy_items[:3]:
            assert item.name in body


class TestGenericCreateView:
    """Integration tests for GenericCreateView (DummyItemCreateView)."""

    def test_create_get_returns_200(self, client: Client) -> None:
        url = reverse("create-view-dummyitem")
        response = client.get(url)
        assert response.status_code == 200

    def test_create_post_creates_and_redirects(self, client: Client) -> None:
        url = reverse("create-view-dummyitem")
        data = {
            "name": "New Item",
            "description": "Created via integration test",
            "amount": "99.99",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert DummyItem.objects.filter(name="New Item").exists()

    def test_create_post_updates_db(self, client: Client) -> None:
        url = reverse("create-view-dummyitem")
        count_before = DummyItem.objects.count()
        data = {"name": "Another Item", "description": "desc", "amount": "50.00"}
        client.post(url, data)
        assert DummyItem.objects.count() == count_before + 1

    def test_create_htmx_returns_hx_refresh(
        self,
        client: Client,
        dummy_items: list[DummyItem],
    ) -> None:
        """Htmx POST should return HX-Refresh header instead of redirect."""
        url = reverse("create-view-dummyitem")
        data = {"name": "Htmx Item", "description": "via htmx", "amount": "10.00"}
        response = client.post(url, data, HTTP_HX_REQUEST="true")
        assert response["HX-Refresh"] == "true"

    def test_create_get_htmx_uses_partial(self, client: Client) -> None:
        url = reverse("create-view-dummyitem")
        response = client.get(url, HTTP_HX_REQUEST="true")
        body = response.content.decode()
        assert "<html" not in body
        assert "<body" not in body


class TestGenericUpdateView:
    """Integration tests for GenericUpdateView (DummyItemUpdateView)."""

    def test_update_get_returns_200(
        self, client: Client, dummy_items: list[DummyItem]
    ) -> None:
        item = dummy_items[0]
        url = reverse("update-view-dummyitem", kwargs={"pk": item.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_update_get_shows_current_data(
        self, client: Client, dummy_items: list[DummyItem]
    ) -> None:
        item = dummy_items[0]
        url = reverse("update-view-dummyitem", kwargs={"pk": item.pk})
        response = client.get(url)
        body = response.content.decode()
        # The form should contain the current name
        assert item.name in body

    def test_update_post_updates_and_redirects(
        self, client: Client, dummy_items: list[DummyItem]
    ) -> None:
        item = dummy_items[0]
        url = reverse("update-view-dummyitem", kwargs={"pk": item.pk})
        data: dict[str, Any] = {
            "name": "Updated Name",
            "description": item.description,
            "amount": str(item.amount),
            "active": item.active,
        }
        response = client.post(url, data)
        assert response.status_code == 302
        item.refresh_from_db()
        assert item.name == "Updated Name"

    def test_update_htmx_returns_hx_refresh(
        self,
        client: Client,
        dummy_items: list[DummyItem],
    ) -> None:
        item = dummy_items[0]
        url = reverse("update-view-dummyitem", kwargs={"pk": item.pk})
        data: dict[str, Any] = {
            "name": "Htmx Updated",
            "description": item.description,
            "amount": str(item.amount),
            "active": item.active,
        }
        response = client.post(url, data, HTTP_HX_REQUEST="true")
        assert response["HX-Refresh"] == "true"


class TestGenericDeleteView:
    """Integration tests for GenericDeleteView (DummyItemDeleteView)."""

    def test_delete_get_returns_200(
        self, client: Client, dummy_items: list[DummyItem]
    ) -> None:
        item = dummy_items[0]
        url = reverse("delete-view-dummyitem", kwargs={"pk": item.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_delete_get_shows_object_name(
        self, client: Client, dummy_items: list[DummyItem]
    ) -> None:
        item = dummy_items[0]
        url = reverse("delete-view-dummyitem", kwargs={"pk": item.pk})
        response = client.get(url)
        assert item.name in response.content.decode()

    def test_delete_post_removes_and_redirects(
        self, client: Client, dummy_items: list[DummyItem]
    ) -> None:
        item = dummy_items[0]
        url = reverse("delete-view-dummyitem", kwargs={"pk": item.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert not DummyItem.objects.filter(pk=item.pk).exists()

    def test_delete_post_htmx_returns_hx_refresh(
        self,
        client: Client,
        dummy_items: list[DummyItem],
    ) -> None:
        item = dummy_items[0]
        url = reverse("delete-view-dummyitem", kwargs={"pk": item.pk})
        response = client.post(url, HTTP_HX_REQUEST="true")
        assert response["HX-Refresh"] == "true"


class TestGenericDetailView:
    """Integration tests for GenericDetailView (DummyItemDetailView)."""

    def test_detail_returns_200(
        self, client: Client, dummy_items: list[DummyItem]
    ) -> None:
        item = dummy_items[0]
        url = reverse("detail-view-dummyitem", kwargs={"pk": item.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_detail_shows_object_data(
        self, client: Client, dummy_items: list[DummyItem]
    ) -> None:
        item = dummy_items[0]
        url = reverse("detail-view-dummyitem", kwargs={"pk": item.pk})
        response = client.get(url)
        body = response.content.decode()
        assert item.name in body
        assert item.description in body

    def test_detail_404(self, client: Client) -> None:
        url = reverse("detail-view-dummyitem", kwargs={"pk": 9999})
        response = client.get(url)
        assert response.status_code == 404

    def test_detail_http404_fallback(self, client: Client) -> None:
        """Detail view should return 404 for non-existent object."""
        url = reverse("detail-view-dummyitem", kwargs={"pk": 9999})
        response = client.get(url)
        assert response.status_code == 404


class TestPaginationIntegration:
    """Integration tests for PaginationFixMixin via CottonTableView."""

    def test_page_too_high_redirects(
        self,
        client: Client,
        dummy_items: list[DummyItem],
    ) -> None:
        """Requesting a non-existent page should redirect to a valid page."""
        url = reverse("list-view-dummyitem")
        response = client.get(url, {"page": "999"})
        assert response.status_code == 302

    def test_negative_page_redirects(
        self,
        client: Client,
        dummy_items: list[DummyItem],
    ) -> None:
        url = reverse("list-view-dummyitem")
        response = client.get(url, {"page": "-1"})
        # Paginator raises EmptyPage for negative page numbers
        assert response.status_code == 302

    def test_zero_page_redirects(
        self,
        client: Client,
        dummy_items: list[DummyItem],
    ) -> None:
        url = reverse("list-view-dummyitem")
        response = client.get(url, {"page": "0"})
        assert response.status_code == 302
