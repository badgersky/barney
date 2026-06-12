from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import Building
from .forms import BuildingForm
from users.mixins import AdminOrManagerRequiredMixin


class BuildingListView(ListView):
    model = Building
    context_object_name = "buildings"


class BuildingDetailView(DetailView):
    model = Building


class BuildingCreateView(AdminOrManagerRequiredMixin, CreateView):
    model = Building
    form_class = BuildingForm
    success_url = reverse_lazy("building-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class BuildingUpdateView(AdminOrManagerRequiredMixin, UpdateView):
    model = Building
    form_class = BuildingForm
    success_url = reverse_lazy("building-list")


class BuildingDeleteView(AdminOrManagerRequiredMixin, DeleteView):
    model = Building
    success_url = reverse_lazy("building-list")