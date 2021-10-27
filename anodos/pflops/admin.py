from django.contrib import admin
from pflops.models import CatalogElement, Vendor, Category, Product, Currency, Image


@admin.register(CatalogElement)
class AdminArticle(admin.ModelAdmin):
    pass


@admin.register(Vendor)
class AdminVendor(admin.ModelAdmin):
    pass


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    pass


@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    pass


@admin.register(Currency)
class AdminProduct(admin.ModelAdmin):
    pass


@admin.register(Image)
class AdminProduct(admin.ModelAdmin):
    pass
