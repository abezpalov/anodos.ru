from django.contrib import admin
from pflops.models import Article, Vendor


@admin.register(Article)
class AdminArticle(admin.ModelAdmin):
    pass


@admin.register(Vendor)
class AdminVendor(admin.ModelAdmin):
    pass
