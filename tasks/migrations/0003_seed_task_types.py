from django.db import migrations


def seed_types(apps, schema_editor):
    TaskType = apps.get_model("tasks", "TaskType")
    data = [
        ("Szczepienie", "HEALTH", "Szczepienie zwierzęcia."),
        ("Kontrola zdrowia", "HEALTH", "Kontrola stanu zdrowia."),
        ("Leczenie", "HEALTH", "Leczenie zwierzęcia."),
        ("Karmienie", "MANAGEMENT", "Karmienie zwierząt."),
        ("Sprzątanie", "MANAGEMENT", "Sprzątanie boksu lub lokalizacji."),
        ("Przeniesienie", "MANAGEMENT", "Przeniesienie zwierzęcia."),
        ("Utrzymanie lokalizacji", "MANAGEMENT", "Prace porządkowe/utrzymaniowe."),
    ]
    for name, category, desc in data:
        TaskType.objects.get_or_create(
            name=name, defaults={"category": category, "description": desc}
        )


def unseed(apps, schema_editor):
    TaskType = apps.get_model("tasks", "TaskType")
    TaskType.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("tasks", "0002_initial")]
    operations = [migrations.RunPython(seed_types, unseed)]
