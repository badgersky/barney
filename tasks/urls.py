from django.urls import path
from .views import (
    TaskListView,
    TaskCreateView,
    TaskUpdateView,
    TaskDeleteView,
    TaskStatusUpdateView
)

urlpatterns = [
    path("", TaskListView.as_view(), name="task-list"),

    path(
        "create/",
        TaskCreateView.as_view(),
        name="task-create"
    ),

    path(
        "<int:pk>/edit/",
        TaskUpdateView.as_view(),
        name="task-update"
    ),

    path(
        "<int:pk>/delete/",
        TaskDeleteView.as_view(),
        name="task-delete"
    ),

    path(
        "<int:pk>/status/",
        TaskStatusUpdateView.as_view(),
        name="task-status"
    )
]