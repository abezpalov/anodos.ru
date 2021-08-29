from django.contrib import admin
from distributors.models import Distributor, Category, Vendor, Condition, Product, Currency, Location, Party


@admin.register(Distributor)
class AdminSource(admin.ModelAdmin):
    pass


@admin.register(Category)
class AdminSource(admin.ModelAdmin):
    pass


@admin.register(Vendor)
class AdminSource(admin.ModelAdmin):
    pass


@admin.register(Condition)
class AdminSource(admin.ModelAdmin):
    pass


@admin.register(Product)
class AdminSource(admin.ModelAdmin):
    pass


@admin.register(Currency)
class AdminSource(admin.ModelAdmin):
    pass


@admin.register(Location)
class AdminSource(admin.ModelAdmin):
    pass


@admin.register(Party)
class AdminSource(admin.ModelAdmin):
    pass

