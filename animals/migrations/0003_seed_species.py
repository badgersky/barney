from django.db import migrations


def seed_species(apps, schema_editor):
    Species = apps.get_model("animals", "Species")
    for name in ["Krowa", "Świnia", "Koń", "Kura", "Koza", "Owca", "Kaczka", "Gęś"]:
        Species.objects.get_or_create(name=name)


def unseed(apps, schema_editor):
    Species = apps.get_model("animals", "Species")
    Species.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("animals", "0002_initial")]
    operations = [migrations.RunPython(seed_species, unseed)]
