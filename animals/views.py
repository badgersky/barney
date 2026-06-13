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

from .models import Animal, AnimalNote
from .forms import AnimalForm, AnimalNoteForm
from users.mixins import AdminOrManagerRequiredMixin


class AnimalListView(LoginRequiredMixin, ListView):
    model = Animal
    template_name = "animals/animal_list.html"
    context_object_name = "animals"


class AnimalDetailView(LoginRequiredMixin, DetailView):
    model = Animal
    template_name = "animals/animal_detail.html"
    context_object_name = "animal"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["note_form"] = AnimalNoteForm()
        return context


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


class AnimalNoteCreateView(AdminOrManagerRequiredMixin, CreateView):
    model = AnimalNote
    form_class = AnimalNoteForm

    def dispatch(self, request, *args, **kwargs):
        self.animal = get_object_or_404(Animal, pk=kwargs["animal_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.animal = self.animal
        form.instance.author = self.request.user
        form.save()
        return redirect("animal-detail", pk=self.animal.pk)
