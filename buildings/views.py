from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Building, BuildingNote
from .forms import BuildingForm, BuildingNoteForm
from users.mixins import AdminOrManagerRequiredMixin


class BuildingListView(LoginRequiredMixin, ListView):
    model = Building
    context_object_name = "buildings"


class BuildingDetailView(LoginRequiredMixin, DetailView):
    model = Building

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["note_form"] = BuildingNoteForm()
        return context


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


class BuildingNoteCreateView(AdminOrManagerRequiredMixin, CreateView):
    model = BuildingNote
    form_class = BuildingNoteForm

    def dispatch(self, request, *args, **kwargs):
        self.building = get_object_or_404(Building, pk=kwargs["building_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.building = self.building
        form.instance.author = self.request.user
        form.save()
        return redirect("building-detail", pk=self.building.pk)
