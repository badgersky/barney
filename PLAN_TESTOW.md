# Plan testów — system Barney

## 1. Cel i zakres

Celem testów jest weryfikacja, że aplikacja Barney (zarządzanie opieką nad zwierzętami) realizuje wymagania funkcjonalne i niefunkcjonalne ze specyfikacji oraz że kluczowe reguły biznesowe działają poprawnie i nie ulegają regresji przy kolejnych zmianach.

Zakresem testów objęte są: modele danych i ich logika, formularze i walidacja, widoki wraz z routingiem i szablonami, kontrola dostępu oparta na rolach oraz reguły integralności danych. Poza zakresem automatycznych testów pozostają: wygląd graficzny i responsywność (oceniane manualnie), wydajność oraz integracja z zewnętrznym systemem powiadomień (niezaimplementowana).

## 2. Poziomy testów

Testy podzielono na trzy poziomy, zgodnie z wymaganiami zadania. Każdy poziom ma odrębne, opisane klasy testowe w katalogu `tests.py` poszczególnych aplikacji.

**Testy jednostkowe** sprawdzają pojedyncze fragmenty logiki w izolacji od bazy danych i warstwy HTTP — przede wszystkim metody modeli. Przykłady: wyliczanie stanu zadania z terminu (`Task.display_status` → „Zaległe"/„Nadchodzące"/„Zaplanowane"), metody ról użytkownika (`User.is_admin/is_manager/is_worker`), reprezentacje tekstowe encji. Klasy: `UserModelUnitTest`, `AnimalModelUnitTest`, `BuildingModelUnitTest`, `TaskUnitTest`.

**Testy modułowe** sprawdzają współpracę kilku elementów jednej aplikacji z udziałem bazy danych: model + formularz + relacje. Obejmują walidację formularzy (np. wymóg, by zadanie dotyczyło zwierzęcia albo lokalizacji), reguły kasowania (NFR-05 — usunięcie lokalizacji nie kasuje zwierząt ani zadań; ochrona gatunku używanego przez zwierzę), kolejność historii notatek oraz obecność danych referencyjnych zasianych migracjami. Klasy: `AnimalModuleTest`, `BuildingModuleTest`, `TaskModuleTest`.

**Testy funkcjonalne** sprawdzają działanie aplikacji od strony użytkownika — pełną ścieżkę żądanie → widok → szablon → odpowiedź, z wykorzystaniem klienta testowego Django. Obejmują logowanie i rejestrację, wymóg uwierzytelnienia (NFR-02), kontrolę dostępu wg roli (pracownik nie może tworzyć danych, widzi tylko swoje zadania), przepływ dodawania i podglądu zadania, dodawanie przypomnień oraz notatek widocznych w historii. Klasy: `AuthFunctionalTest`, `AnimalFunctionalTest`, `BuildingFunctionalTest`, `TaskFunctionalTest`.

## 3. Środowisko i narzędzia

Testy korzystają z wbudowanego frameworka `django.test` (oparty na `unittest`), uruchamianego przez `manage.py test`. Pomiar pokrycia kodu realizuje narzędzie `coverage` (konfiguracja w `.coveragerc`). Testy nie wymagają działającego serwera ani osobnej bazy — Django tworzy izolowaną bazę testową, którą usuwa po zakończeniu, a każdy test działa w transakcji wycofywanej po jego wykonaniu.

Przewidziano dwa środowiska uruchomieniowe: PostgreSQL (zgodne z produkcją — używane w Dockerze i w CI, ustawienia `config.settings`) oraz SQLite w pamięci dla szybkich uruchomień lokalnych bez bazy (`config.settings_test`).

## 4. Uruchamianie testów

W kontenerze aplikacji (PostgreSQL):

```
docker compose exec web python manage.py test
```

Lokalnie, szybko, bez PostgreSQL (SQLite w pamięci):

```
DJANGO_SETTINGS_MODULE=config.settings_test python manage.py test
```

Z pomiarem pokrycia:

```
coverage run manage.py test
coverage report          # podsumowanie w konsoli
coverage html            # szczegółowy raport HTML w katalogu htmlcov/
```

## 5. Automatyzacja

Proces testowania jest zautomatyzowany w GitHub Actions (`.github/workflows/tests.yml`). Po każdym `push` i `pull request` workflow: uruchamia usługę PostgreSQL, instaluje zależności z `requirements.txt` i `requirements-dev.txt`, wykonuje pełny zestaw testów z pomiarem pokrycia i publikuje raport pokrycia jako artefakt. Niepowodzenie któregokolwiek testu kończy build błędem, co blokuje scalanie zmian z regresją.

## 6. Macierz pokrycia wymagań

| Wymaganie | Poziom | Klasa.metoda testowa |
|---|---|---|
| FR-01 Logowanie / FR-02 role | jednostkowy, funkcjonalny | `UserModelUnitTest`, `AuthFunctionalTest`, `*Functional.test_worker_cannot_create` |
| FR-03–05 CRUD zwierząt | modułowy, funkcjonalny | `AnimalModuleTest`, `AnimalFunctionalTest.test_manager_can_create` |
| FR-06 Lista i szczegóły zwierzęcia | funkcjonalny | `AnimalFunctionalTest.test_list_renders_animals`, `test_add_note_appears_in_history_with_author` |
| FR-07 Zarządzanie lokalizacjami | funkcjonalny | `BuildingFunctionalTest` |
| FR-08 Zarządzanie zadaniami (cel: zwierzę/lokalizacja) | modułowy, funkcjonalny | `TaskModuleTest.test_form_*`, `TaskFunctionalTest.test_create_*` |
| FR-09 Przypomnienia | modułowy, funkcjonalny | `TaskModuleTest.test_reminder_related_to_task`, `TaskFunctionalTest.test_reminder_added_and_visible_in_detail` |
| FR-10 Oznaczanie statusu | funkcjonalny | `TaskFunctionalTest.test_worker_can_update_own_task_status` |
| FR-11 Zadania zaległe/nadchodzące | jednostkowy | `TaskUnitTest.test_overdue_*`, `test_upcoming_*` |
| Historia notatek (zwierzę/lokalizacja) | modułowy, funkcjonalny | `AnimalModuleTest.test_note_history_order_and_latest`, `BuildingModuleTest`, testy funkcjonalne dodawania notatek |
| NFR-02 Dostęp tylko po zalogowaniu | funkcjonalny | `*Functional.test_list_requires_login`, `AuthFunctionalTest` |
| NFR-05 Usunięcie lokalizacji nie kasuje zwierząt/zadań | modułowy | `AnimalModuleTest.test_deleting_location_keeps_animal_nfr05`, `BuildingModuleTest.test_delete_location_does_not_delete_animals` |
| Dane referencyjne (gatunki, typy zadań) | modułowy | `TaskModuleTest.test_seed_reference_data_present` |

## 7. Kryteria zaliczenia

Zestaw uznaje się za zaliczony, gdy wszystkie testy przechodzą (status `OK`), a pokrycie kodu aplikacji utrzymuje się na poziomie co najmniej 90%. Każda nowa funkcjonalność powinna być dostarczana wraz z testami; każdy naprawiony błąd — wraz z testem zabezpieczającym przed jego powrotem.

## 8. Aktualny stan

Zestaw liczy 45 testów (jednostkowe, modułowe i funkcjonalne dla aplikacji `users`, `animals`, `buildings`, `tasks`). Wszystkie przechodzą, a pokrycie kodu aplikacji wynosi ok. 97%. Najniżej pokryte pozostają fragmenty marginalne (przekierowanie strony głównej, gałąź rejestracji wyświetlająca pusty formularz).

## 9. Dalsze kroki

Po dodaniu kolejnych funkcjonalności (dashboard, integracja powiadomień) zestaw należy rozszerzyć o odpowiednie testy funkcjonalne i modułowe. Warto też dołożyć testy negatywne dla edycji i usuwania (próby modyfikacji cudzych zadań przez pracownika) oraz — przy ocenie wyglądu — listę scenariuszy testów manualnych dla responsywności (NFR-04).
