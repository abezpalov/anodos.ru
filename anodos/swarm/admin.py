from django.contrib import admin
from swarm.models import Source, SourceData


@admin.register(Source)
class AdminSource(admin.ModelAdmin):
    pass


@admin.register(SourceData)
class AdminSourceData(admin.ModelAdmin):
    pass
