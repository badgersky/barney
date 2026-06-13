from django.db import migrations


# Gatunki referencyjne. "Koza" jest wymagana przez testy (goat()).
# Rozszerz listę, jeśli test_seed_reference_data_present oczekuje większej liczby.
SPECIES = [
    "Koza",
    "Owca",
    "Krowa",
    "Koń",
    "Świnia",
]


def seed(apps, schema_editor):
    Species = apps.get_model("animals", "Species")
    for name in SPECIES:
        Species.objects.get_or_create(name=name)


def unseed(apps, schema_editor):
    Species = apps.get_model("animals", "Species")
    Species.objects.filter(name__in=SPECIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("animals", "0003_animal_species_animalnote_author"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]