from django import forms
from .models import Task


class TaskForm(forms.ModelForm):

    due_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False
    )

    class Meta:
        model = Task

        fields = [
            "title",
            "description",
            "assigned_to",
            "status",
            "due_date",
            "animal"
        ]

class TaskStatusForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ["status"]