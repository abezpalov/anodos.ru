from django.contrib import admin
from swarm.models import Source, SourceData, Organisation, Product


@admin.register(Source)
class AdminSource(admin.ModelAdmin):
    pass


@admin.register(SourceData)
class AdminSourceData(admin.ModelAdmin):
    pass


@admin.register(Organisation)
class AdminSourceData(admin.ModelAdmin):
    pass


@admin.register(Product)
class AdminSourceData(admin.ModelAdmin):
    pass

