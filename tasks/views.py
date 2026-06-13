from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Task, Reminder
from .forms import TaskForm, TaskStatusForm, ReminderForm
from users.mixins import AdminOrManagerRequiredMixin


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"

    def get_queryset(self):
        user = self.request.user
        if user.is_admin() or user.is_manager():
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = "task"

    def get_queryset(self):
        user = self.request.user
        if user.is_admin() or user.is_manager():
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reminder_form"] = ReminderForm()
        return context


class TaskCreateView(AdminOrManagerRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("task-detail", args=[self.object.pk])


class TaskUpdateView(AdminOrManagerRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm

    def get_success_url(self):
        return reverse("task-detail", args=[self.object.pk])


class TaskDeleteView(AdminOrManagerRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy("task-list")


class TaskStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskStatusForm
    template_name = "tasks/task_status_form.html"

    def get_queryset(self):
        user = self.request.user
        if user.is_admin() or user.is_manager():
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user)

    def get_success_url(self):
        return reverse("task-detail", args=[self.object.pk])


class ReminderCreateView(AdminOrManagerRequiredMixin, CreateView):
    model = Reminder
    form_class = ReminderForm

    def dispatch(self, request, *args, **kwargs):
        self.task = get_object_or_404(Task, pk=kwargs["task_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.task = self.task
        form.save()
        return redirect("task-detail", pk=self.task.pk)
