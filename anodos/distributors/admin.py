from django.contrib import admin
from distributors.models import Distributor, Category, Vendor


@admin.register(Distributor)
class AdminSource(admin.ModelAdmin):
    pass


@admin.register(Category)
class AdminSource(admin.ModelAdmin):
    pass


@admin.register(Vendor)
class AdminSource(admin.ModelAdmin):
    pass
