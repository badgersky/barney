"""
Wypełnia bazę danych przykładowymi danymi demonstracyjnymi.

Użycie:
    python manage.py seed_demo

Komenda jest idempotentna — można ją uruchamiać wielokrotnie, nie tworzy
duplikatów (korzysta z get_or_create na polach unikalnych). Gatunki i typy
zadań pochodzą z migracji seedujących, więc muszą być już w bazie.

Domyślne hasło wszystkich kont: demo12345
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from animals.models import Animal, AnimalNote, Species
from buildings.models import Building, BuildingNote
from tasks.models import Reminder, Task, TaskType

User = get_user_model()

PASSWORD = "demo12345"


class Command(BaseCommand):
    help = "Wypełnia bazę przykładowymi danymi (użytkownicy, zwierzęta, zadania, notatki)."

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()

        # ---------------------------------------------------------------
        # 1. Użytkownicy (po jednym na każdą rolę)
        # ---------------------------------------------------------------
        users = {}
        people = [
            # username,      first,      last,         role,       admin?
            ("admin",      "Anna",     "Adamczyk",   User.Role.ADMIN,   True),
            ("wlasciciel", "Wojciech", "Lis",        User.Role.MANAGER, False),
            ("pracownik",  "Piotr",    "Nowak",      User.Role.WORKER,  False),
        ]
        for username, first, last, role, is_admin in people:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": f"{username}@barney.local",
                    "role": role,
                    "is_staff": is_admin,
                    "is_superuser": is_admin,
                },
            )
            if created:
                user.set_password(PASSWORD)
                user.save()
            users[username] = user
        self.stdout.write(self.style.SUCCESS(f"Użytkownicy: {len(users)}"))

        admin = users["admin"]
        manager = users["wlasciciel"]
        worker = users["pracownik"]

        # ---------------------------------------------------------------
        # 2. Lokalizacje (zwierzęta gdzieś muszą mieszkać)
        # ---------------------------------------------------------------
        buildings = {}
        building_data = [
            ("Stajnia Główna",     Building.Type.STABLE,  manager),
            ("Boks nr 1",          Building.Type.STALL,   manager),
            ("Zagroda Wschodnia",  Building.Type.PEN,     admin),
            ("Wybieg Południowy",  Building.Type.PADDOCK, manager),
        ]
        for name, btype, creator in building_data:
            obj, _ = Building.objects.get_or_create(
                name=name,
                defaults={"type": btype, "created_by": creator},
            )
            buildings[name] = obj
        self.stdout.write(self.style.SUCCESS(f"Lokalizacje: {len(buildings)}"))

        # ---------------------------------------------------------------
        # 3. Zwierzęta (gatunki pochodzą z migracji 0004_seed_species)
        # ---------------------------------------------------------------
        def species(name):
            return Species.objects.get(name=name)

        animals = {}
        animal_data = [
            # identifier, name,        gatunek,   płeć,            stan zdrowia,                lokalizacja,           wiek (dni)
            ("PL-001", "Barney",     "Koza",    Animal.Sex.MALE,   Animal.HealthStatus.HEALTHY,   "Stajnia Główna",     900),
            ("PL-002", "Matylda",    "Owca",    Animal.Sex.FEMALE, Animal.HealthStatus.TREATMENT, "Boks nr 1",          1200),
            ("PL-003", "Bażyl",      "Krowa",   Animal.Sex.MALE,   Animal.HealthStatus.HEALTHY,   "Zagroda Wschodnia",  1800),
            ("PL-004", "Klara",      "Koń",     Animal.Sex.FEMALE, Animal.HealthStatus.SICK,      "Stajnia Główna",     2500),
            ("PL-005", "Gienek",     "Świnia",  Animal.Sex.MALE,   Animal.HealthStatus.HEALTHY,   "Wybieg Południowy",  400),
            ("PL-006", "Rogal",      "Koza",    Animal.Sex.MALE,   Animal.HealthStatus.TREATMENT, "Zagroda Wschodnia",  600),
            ("PL-007", "Stokrotka",  "Krowa",   Animal.Sex.FEMALE, Animal.HealthStatus.HEALTHY,   "Zagroda Wschodnia",  1500),
            ("PL-008", "",           "Owca",    Animal.Sex.UNKNOWN, Animal.HealthStatus.HEALTHY,   "Boks nr 1",          150),
        ]
        for ident, name, sp, sex, health, building_name, age_days in animal_data:
            obj, _ = Animal.objects.get_or_create(
                identifier=ident,
                defaults={
                    "name": name,
                    "species": species(sp),
                    "sex": sex,
                    "health_status": health,
                    "building": buildings.get(building_name),
                    "birth_date": today - timedelta(days=age_days),
                },
            )
            animals[ident] = obj
        self.stdout.write(self.style.SUCCESS(f"Zwierzęta: {len(animals)}"))

        # ---------------------------------------------------------------
        # 4. Notatki zwierząt (historia z autorem)
        # ---------------------------------------------------------------
        animal_notes = [
            ("PL-002", "Lekka kulawizna na lewej tylnej. Obserwacja.",              worker),
            ("PL-002", "Podano środek przeciwzapalny, poprawa widoczna.",           manager),
            ("PL-004", "Brak apetytu od dwóch dni, wezwany weterynarz.",            worker),
            ("PL-004", "Diagnoza: infekcja. Rozpoczęto antybiotykoterapię.",        manager),
            ("PL-006", "Zaplanowano odrobaczanie w przyszłym tygodniu.",            manager),
            ("PL-001", "Stan bardzo dobry, waga w normie.",                         worker),
        ]
        note_count = 0
        for ident, content, author in animal_notes:
            _, created = AnimalNote.objects.get_or_create(
                animal=animals[ident],
                content=content,
                defaults={"author": author},
            )
            note_count += int(created)
        self.stdout.write(self.style.SUCCESS(f"Notatki zwierząt: {note_count}"))

        # ---------------------------------------------------------------
        # 5. Notatki lokalizacji
        # ---------------------------------------------------------------
        building_notes = [
            ("Stajnia Główna",    "Wymieniono ściółkę w całym pomieszczeniu.",      worker),
            ("Wybieg Południowy", "Ogrodzenie wymaga naprawy w sektorze północnym.", manager),
        ]
        bnote_count = 0
        for bname, content, author in building_notes:
            _, created = BuildingNote.objects.get_or_create(
                building=buildings[bname],
                content=content,
                defaults={"author": author},
            )
            bnote_count += int(created)
        self.stdout.write(self.style.SUCCESS(f"Notatki lokalizacji: {bnote_count}"))

        # ---------------------------------------------------------------
        # 6. Zadania (typy z migracji 0003_seed_tasktypes)
        # ---------------------------------------------------------------
        def task_type(name):
            return TaskType.objects.filter(name=name).first()

        task_data = [
            # tytuł, typ, status, termin (offset dni), przypisane, autor, zwierzę, lokalizacja
            ("Szczepienie Barneya",        "Szczepienie",          Task.Status.PLANNED,   +2,  worker,  manager, "PL-001", None),
            ("Kontrola leczenia Matyldy",  "Leczenie",             Task.Status.PLANNED,   -1,  worker,  manager, "PL-002", None),
            ("Badanie weterynaryjne Klary","Badanie weterynaryjne",Task.Status.PLANNED,   +1,  manager, manager, "PL-004", None),
            ("Odrobaczanie Rogala",        "Leczenie",             Task.Status.PLANNED,   +7,  worker,  manager, "PL-006", None),
            ("Sprzątanie wybiegu",         "Sprzątanie wybiegu",   Task.Status.DONE,      -3,  worker,  manager, None,     "Wybieg Południowy"),
            ("Przegląd ogrodzenia zagrody","Przegląd ogrodzenia",  Task.Status.PLANNED,   -5,  worker,  admin,   None,     "Zagroda Wschodnia"),
        ]
        tasks = {}
        for title, tt, status, offset, assignee, creator, ident, bname in task_data:
            obj, _ = Task.objects.get_or_create(
                title=title,
                defaults={
                    "task_type": task_type(tt),
                    "status": status,
                    "due_date": today + timedelta(days=offset),
                    "assigned_to": assignee,
                    "created_by": creator,
                    "animal": animals.get(ident) if ident else None,
                    "building": buildings.get(bname) if bname else None,
                },
            )
            tasks[title] = obj
        self.stdout.write(self.style.SUCCESS(f"Zadania: {len(tasks)}"))

        # ---------------------------------------------------------------
        # 7. Przypomnienia dla wybranych zadań
        # ---------------------------------------------------------------
        reminders = [
            ("Szczepienie Barneya",         today + timedelta(days=1), "Przygotować szczepionkę i kartę zwierzęcia."),
            ("Badanie weterynaryjne Klary", today,                     "Potwierdzić wizytę weterynarza."),
        ]
        rem_count = 0
        for title, date, message in reminders:
            _, created = Reminder.objects.get_or_create(
                task=tasks[title],
                message=message,
                defaults={"date": date},
            )
            rem_count += int(created)
        self.stdout.write(self.style.SUCCESS(f"Przypomnienia: {rem_count}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Gotowe. Dane demonstracyjne wczytane."))
        self.stdout.write(f"Logowanie — login/hasło: admin / {PASSWORD} (oraz wlasciciel, pracownik).")