from django.db import migrations


# Typy zadań referencyjne. Model TaskType ma kategorie HEALTH i MANAGEMENT.
# Test wymaga przynajmniej jednego TaskType w kategorii HEALTH.
TASK_TYPES = [
    ("Szczepienie", "HEALTH"),
    ("Badanie weterynaryjne", "HEALTH"),
    ("Leczenie", "HEALTH"),
    ("Przegląd ogrodzenia", "MANAGEMENT"),
    ("Sprzątanie wybiegu", "MANAGEMENT"),
]


def seed(apps, schema_editor):
    TaskType = apps.get_model("tasks", "TaskType")
    for name, category in TASK_TYPES:
        TaskType.objects.get_or_create(name=name, defaults={"category": category})


def unseed(apps, schema_editor):
    TaskType = apps.get_model("tasks", "TaskType")
    TaskType.objects.filter(name__in=[n for n, _ in TASK_TYPES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]