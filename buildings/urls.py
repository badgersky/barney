from django.urls import path

from .views import (
    BuildingListView,
    BuildingDetailView,
    BuildingCreateView,
    BuildingUpdateView,
    BuildingDeleteView
)

urlpatterns = [
    path("", BuildingListView.as_view(), name="building-list"),
    path("<int:pk>/", BuildingDetailView.as_view(), name="building-detail"),
    path("create/", BuildingCreateView.as_view(), name="building-create"),
    path("<int:pk>/update/", BuildingUpdateView.as_view(), name="building-update"),
    path("<int:pk>/delete/", BuildingDeleteView.as_view(), name="building-delete"),
]