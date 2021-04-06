import os
import uuid
from django.db import models
from django.conf import settings


class InstrumentManager(models.Manager):

    def take_by_figi(self, figi='', **kwargs):

        if not figi:
            return None

        try:
            o = self.get(figi=figi)

        except Instrument.DoesNotExist:
            o = Instrument()
            o.figi = figi

        if kwargs.get('ticker', None):
            o.ticker = kwargs.get('ticker', None)
        if kwargs.get('isin', None):
            o.isin = kwargs.get('isin', None)
        if kwargs.get('name', None):
            o.name = kwargs.get('name', None)
        if kwargs.get('type', None):
            o.type = kwargs.get('type', None)
        if kwargs.get('lot', None):
            o.lot = kwargs.get('lot', None)
        if kwargs.get('minPriceIncrement', None):
            o.minPriceIncrement = kwargs.get('minPriceIncrement', None)
        if kwargs.get('currency', None):
            o.currency = kwargs.get('currency', None)

        o.save()
        return o

    def get_by_ticker(self, ticker):
        try:
            o = self.get(ticker=ticker)
            return o
        except Instrument.DoesNotExist:
            return None


class Instrument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    figi = models.CharField(max_length=128, unique=True)
    ticker = models.CharField(max_length=128, null=True, default=None, db_index=True)
    isin = models.CharField(max_length=128, null=True, default=None)
    name = models.TextField(null=True, default=None, db_index=True)
    type = models.CharField(max_length=128, null=True, default=None, db_index=True)
    lot = models.BigIntegerField(null=True, default=None)
    minPriceIncrement = models.DecimalField(null=True, default=None,
                                            max_digits=19, decimal_places=10)

    objects = InstrumentManager()

    def __str__(self):
        return "Instrument: {} ({})".format(self.ticker, self.name)

    def get_last_candles_datetime(self, interval, default, force_default=False):
        try:
            result = Candle.objects.filter(instrument=self,
                                           interval=interval).order_by('-datetime')[0].datetime
        except IndexError:
            if force_default:
                print('Use Force default')
                result = default
            else:
                print('Use NOT Force default')
                result = self.get_first_candles_datetime(interval='month')
        return result

    def get_first_candles_datetime(self, interval):
        try:
            return Candle.objects.filter(instrument=self, interval=interval).order_by('datetime')[0].datetime
        except IndexError:
            return None

    class Meta:
        ordering = ['ticker']


class SnapshotManager(models.Manager):

    def add(self, instrument, orderbook, candles):
        o = Snapshot()
        o.instrument = instrument
        o.orderbook = orderbook
        o.candles = candles
        o.save()
        return o


class Snapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    instrument = models.ForeignKey('Instrument', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    orderbook = models.TextField()
    candles = models.TextField()

    objects = SnapshotManager()

    def __str__(self):
        return "Snapshot: {} {}".format(self.instrument.ticker, self.created)

    class Meta:
        ordering = ['created']


class CandleManager(models.Manager):

    def write(self, instrument, datetime, interval, o, c, h, l, v):
        try:
            candle = self.get(instrument=instrument, datetime=datetime, interval=interval)
        except Candle.DoesNotExist:
            candle = Candle()
            candle.instrument = instrument
            candle.datetime = datetime
            candle.interval = interval

        candle.o = o
        candle.c = c
        candle.h = h
        candle.l = l
        candle.v = v
        candle.save()
        return candle


class Candle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    instrument = models.ForeignKey('Instrument', on_delete=models.CASCADE)
    datetime = models.DateTimeField(db_index=True)

    interval = models.CharField(max_length=8, db_index=True)
    o = models.DecimalField(max_digits=20, decimal_places=10)
    c = models.DecimalField(max_digits=20, decimal_places=10)
    h = models.DecimalField(max_digits=20, decimal_places=10)
    l = models.DecimalField(max_digits=20, decimal_places=10)
    v = models.BigIntegerField()

    objects = CandleManager()

    def __str__(self):
        return "Candle: {} {} {}".format(self.instrument.ticker, self.interval, self.datetime)

    class Meta:
        ordering = ['-datetime']
