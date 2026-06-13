from django.contrib import admin
from .models import Animal, Species, AnimalNote

admin.site.register(Animal)
admin.site.register(Species)
admin.site.register(AnimalNote)
