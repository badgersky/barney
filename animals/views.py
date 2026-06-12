from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import Animal
from .forms import AnimalForm
from users.mixins import AdminOrManagerRequiredMixin


class AnimalListView(ListView):
    model = Animal
    template_name = "animals/animal_list.html"


class AnimalCreateView(AdminOrManagerRequiredMixin, CreateView):
    model = Animal
    form_class = AnimalForm
    template_name = "animals/animal_form.html"
    success_url = reverse_lazy("animal-list")


class AnimalUpdateView(AdminOrManagerRequiredMixin, UpdateView):
    model = Animal
    form_class = AnimalForm
    template_name = "animals/animal_form.html"
    success_url = reverse_lazy("animal-list")


class AnimalDeleteView(AdminOrManagerRequiredMixin, DeleteView):
    model = Animal
    template_name = "animals/animal_confirm_delete.html"
    success_url = reverse_lazy("animal-list")