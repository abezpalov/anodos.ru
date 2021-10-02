from django.contrib import admin
from pflops.models import Article


@admin.register(Article)
class AdminCategory(admin.ModelAdmin):
    pass
