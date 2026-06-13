from django import forms
from .models import Animal, AnimalNote


class AnimalForm(forms.ModelForm):

    birth_date = forms.DateField(
        label="Data urodzenia",
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
    )

    class Meta:
        model = Animal
        fields = [
            "name",
            "identifier",
            "species",
            "sex",
            "building",
            "health_status",
            "birth_date",
        ]


class AnimalNoteForm(forms.ModelForm):
    class Meta:
        model = AnimalNote
        fields = ["content"]
        labels = {"content": "Nowa notatka"}
        widgets = {"content": forms.Textarea(attrs={"rows": 3})}
