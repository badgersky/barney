from django import forms
from .models import Task, Reminder


class TaskForm(forms.ModelForm):

    due_date = forms.DateField(
        label="Termin",
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "task_type",
            "assigned_to",
            "animal",
            "building",
            "status",
            "due_date",
        ]

    def clean(self):
        cleaned = super().clean()
        animal = cleaned.get("animal")
        building = cleaned.get("building")
        if not animal and not building:
            raise forms.ValidationError(
                "Zadanie musi dotyczyć zwierzęcia albo lokalizacji."
            )
        return cleaned


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["status"]


class ReminderForm(forms.ModelForm):

    date = forms.DateField(
        label="Data przypomnienia",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = Reminder
        fields = ["date", "message"]
