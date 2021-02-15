from django.contrib import admin
from trader.models import Instrument


@admin.register(Instrument)
class AdminSource(admin.ModelAdmin):
    pass