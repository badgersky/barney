from django import forms
from .models import Building, BuildingNote


class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ["name", "type"]


class BuildingNoteForm(forms.ModelForm):
    class Meta:
        model = BuildingNote
        fields = ["content"]
        labels = {"content": "Nowa notatka"}
        widgets = {"content": forms.Textarea(attrs={"rows": 3})}
