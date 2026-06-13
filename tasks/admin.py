from django.contrib import admin
from .models import Task, TaskType, Reminder

admin.site.register(Task)
admin.site.register(TaskType)
admin.site.register(Reminder)
