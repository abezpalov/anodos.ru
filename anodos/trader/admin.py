from django.contrib import admin
from trader.models import Instrument, Snapshot


@admin.register(Instrument)
class AdminInstrument(admin.ModelAdmin):
    pass


@admin.register(Snapshot)
class AdminSnapshot(admin.ModelAdmin):
    pass
