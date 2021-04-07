from django.contrib import admin
from pflops.models import Category


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    pass
