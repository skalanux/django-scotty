from django.urls import path

from tests.views import (
    DummyItemCreateView,
    DummyItemDeleteView,
    DummyItemDetailView,
    DummyItemDictView,
    DummyItemListView,
    DummyItemUpdateView,
)

urlpatterns = [
    path("items/", DummyItemListView.as_view(), name="list-view-dummyitem"),
    path("items/create/", DummyItemCreateView.as_view(), name="create-view-dummyitem"),
    path(
        "items/<int:pk>/update/",
        DummyItemUpdateView.as_view(),
        name="update-view-dummyitem",
    ),
    path(
        "items/<int:pk>/delete/",
        DummyItemDeleteView.as_view(),
        name="delete-view-dummyitem",
    ),
    path(
        "items/<int:pk>/",
        DummyItemDetailView.as_view(),
        name="detail-view-dummyitem",
    ),
    path("items-dict/", DummyItemDictView.as_view(), name="list-view-dummyitem-dict"),
]
