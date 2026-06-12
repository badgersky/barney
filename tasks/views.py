from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Task
from django.contrib.auth.mixins import LoginRequiredMixin
from users.mixins import AdminOrManagerRequiredMixin
from django.urls import reverse_lazy
from .forms import TaskForm, TaskStatusForm


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"

    def get_queryset(self):
        user = self.request.user

        if user.is_admin() or user.is_manager():
            return Task.objects.all()

        return Task.objects.filter(
            assigned_to=user
        )
    

class TaskCreateView(
    AdminOrManagerRequiredMixin,
    CreateView
):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("task-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    

class TaskUpdateView(
    AdminOrManagerRequiredMixin,
    UpdateView
):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("task-list")


class TaskDeleteView(
    AdminOrManagerRequiredMixin,
    DeleteView
):
    model = Task
    success_url = reverse_lazy("task-list")


class TaskStatusUpdateView(
    LoginRequiredMixin,
    UpdateView
):
    model = Task
    form_class = TaskStatusForm
    success_url = reverse_lazy("task-list")

    def get_queryset(self):
        user = self.request.user

        if user.is_admin() or user.is_manager():
            return Task.objects.all()

        return Task.objects.filter(
            assigned_to=user
        )