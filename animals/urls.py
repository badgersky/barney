from django.urls import path
from .views import (
    AnimalListView,
    AnimalDetailView,
    AnimalCreateView,
    AnimalUpdateView,
    AnimalDeleteView,
    AnimalNoteCreateView,
)

urlpatterns = [
    path("", AnimalListView.as_view(), name="animal-list"),
    path("create/", AnimalCreateView.as_view(), name="animal-create"),
    path("<int:pk>/", AnimalDetailView.as_view(), name="animal-detail"),
    path("<int:pk>/edit/", AnimalUpdateView.as_view(), name="animal-update"),
    path("<int:pk>/delete/", AnimalDeleteView.as_view(), name="animal-delete"),
    path(
        "<int:animal_pk>/notes/add/",
        AnimalNoteCreateView.as_view(),
        name="animal-note-create",
    ),
]
