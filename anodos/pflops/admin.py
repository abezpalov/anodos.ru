from django.contrib import admin
from pflops.models import Category, Article


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    pass


@admin.register(Article)
class AdminCategory(admin.ModelAdmin):
    pass
