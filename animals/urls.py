from django.urls import path
from .views import (
    AnimalListView,
    AnimalCreateView,
    AnimalUpdateView,
    AnimalDeleteView
)

urlpatterns = [
    path("", AnimalListView.as_view(), name="animal-list"),
    path("create/", AnimalCreateView.as_view(), name="animal-create"),
    path("<int:pk>/edit/", AnimalUpdateView.as_view(), name="animal-update"),
    path("<int:pk>/delete/", AnimalDeleteView.as_view(), name="animal-delete"),
]