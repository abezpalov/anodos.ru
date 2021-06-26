import requests as r
import json

from multiprocessing.dummy import Pool as ThreadPool

from django.utils import timezone
from datetime import datetime, date, time, timedelta

from swarm.models import *
from trader.models import *
from swarm.workers.worker import Worker as W


class Worker(W):

    name = 'tinkoff.ru/invest/collector'
    login = None
    password = None
    company = 'Tinkoff'
    url = 'https://api-invest.tinkoff.ru/openapi/'

    intervals = ['month', 'week', 'day', 'hour', '5min', '1min']
    interval_limits = {'1min': {'min': timedelta(minutes=1), 'max': timedelta(days=1)},
                       '2min': {'min': timedelta(minutes=2), 'max': timedelta(days=1)},
                       '3min': {'min': timedelta(minutes=3), 'max': timedelta(days=1)},
                       '5min': {'min': timedelta(minutes=5), 'max': timedelta(days=1)},
                       '10min': {'min': timedelta(minutes=10), 'max': timedelta(days=1)},
                       '15min': {'min': timedelta(minutes=15), 'max': timedelta(days=1)},
                       '30min': {'min': timedelta(minutes=30), 'max': timedelta(days=1)},
                       'hour': {'min': timedelta(hours=1), 'max': timedelta(days=7)},
                       'day': {'min': timedelta(days=1), 'max': timedelta(days=365)},
                       'week': {'min': timedelta(days=7), 'max': timedelta(days=365)},
                       'month': {'min': timedelta(days=31), 'max': timedelta(days=365)}}
    start_datetime = datetime.combine(date(2000, 1, 1), time(0, 0, 0, 0))

    def __init__(self):
        self.source = Source.objects.take(
            name=self.name,
            login=self.login,
            password=self.password)
        self.token = settings.TINKOFF_TOKEN

        super().__init__()

    def run(self, command=None):
        self.send(f'TI run {command}')

        if command is None:
            # Обновляем список инструментов
            self.update_stocks()
            self.update_bonds()
            self.update_etfs()
            self.update_currencies()

            # Обновляем историю торгов
            self.update_instruments_history()

        elif command == 'shoot':
            # Получаем информацию о текущих торгах
            while True:
                self.shoot_instruments()

        self.send(f'TI end {command}')

    def get(self, command='', parameters=''):
        url = f'{self.url}{command}{parameters}'
        headers = {'Authorization': f'Bearer {self.token}',
                   'accept': 'application/json'}
        result = r.get(url, headers=headers, verify=None, timeout=180)
        try:
            result = result.json()
            # TODO проверить код ответа и отправить ошибку в случае ошибки
        except json.decoder.JSONDecodeError:
            result = None
        except r.exceptions.ConnectionError:
            result = None
        return result

    def update_stocks(self):
        stocks = self.get(command='market/stocks')
        for n, stock in enumerate(stocks['payload']['instruments']):
            instrument = Instrument.objects.take_by_figi(
                figi=stock.get('figi', None),
                ticker=stock.get('ticker', None),
                isin=stock.get('isin', None),
                minPriceIncrement=stock.get('minPriceIncrement', None),
                lot=stock.get('lot', None),
                currency=stock.get('currency', None),
                name=stock.get('name', None),
                type=stock.get('type', None),
            )
            print('{}/{} {}'.format(
                n + 1,
                len(stocks['payload']['instruments']),
                instrument))

    def update_bonds(self):
        bonds = self.get(command='market/bonds')
        for n, bond in enumerate(bonds['payload']['instruments']):
            instrument = Instrument.objects.take_by_figi(
                figi=bond.get('figi', None),
                ticker=bond.get('ticker', None),
                isin=bond.get('isin', None),
                minPriceIncrement=bond.get('minPriceIncrement', None),
                lot=bond.get('lot', None),
                currency=bond.get('currency', None),
                name=bond.get('name', None),
                type=bond.get('type', None),
            )
            print('{}/{} {}'.format(
                n + 1,
                len(bonds['payload']['instruments']),
                instrument))

    def update_etfs(self):
        etfs = self.get(command='market/etfs')
        for n, etf in enumerate(etfs['payload']['instruments']):
            instrument = Instrument.objects.take_by_figi(
                figi=etf.get('figi', None),
                ticker=etf.get('ticker', None),
                isin=etf.get('isin', None),
                minPriceIncrement=etf.get('minPriceIncrement', None),
                lot=etf.get('lot', None),
                currency=etf.get('currency', None),
                name=etf.get('name', None),
                type=etf.get('type', None),
            )
            print('{}/{} {}'.format(
                n + 1,
                len(etfs['payload']['instruments']),
                instrument))

    def update_currencies(self):
        command = 'market/currencies'
        currencies = self.get(command=command)
        for n, currency in enumerate(currencies['payload']['instruments']):
            instrument = Instrument.objects.take_by_figi(
                figi=currency.get('figi', None),
                ticker=currency.get('ticker', None),
                isin=currency.get('isin', None),
                minPriceIncrement=currency.get('minPriceIncrement', None),
                lot=currency.get('lot', None),
                currency=currency.get('currency', None),
                name=currency.get('name', None),
                type=currency.get('type', None),
            )
            print('{}/{} {}'.format(
                n + 1,
                len(currencies['payload']['instruments']),
                instrument))

    def update_instruments_history(self, instrument_type=None):

        content = 'Start update history {}'.format(Candle.objects.all().count())
        print(f'\n\n{content}')

        if instrument_type is None:
            instruments = Instrument.objects.all()
        else:
            instruments = Instrument.objects.filter(type=instrument_type)

        pool = ThreadPool(4)
        pool.map(self.update_instrument_history, instruments)

    def update_instrument_history(self, instrument):

        command = '/market/candles'

        # Проверяем, есть ли торги за последний месяц
        if not self.is_actual(instrument):
            return None

        # Проходим по всем интересуемым интервалам
        for i, interval in enumerate(self.intervals):

            # Определяем общие интервалы загрузки данных
            if i == 0:
                global_start = instrument.get_last_candles_datetime(interval=interval,
                                                                    default=self.start_datetime)
            else:
                global_start = instrument.get_last_candles_datetime(interval=interval,
                                                                    default=self.start_datetime,
                                                                    previous_interval=self.intervals[i-1])
            global_end = datetime.utcnow()

            # Если нет стартового интервала, пропускаем
            if global_start is None:
                continue

            # Готовим первый период
            start, end = self.first_interval(interval, global_start, global_end)

            # Получаем данные итерационно в пределах лимитов диапазонов
            while True:

                # Готовим запрос
                start_ = self.datetime_to_str(start)
                end_ = self.datetime_to_str(end)
                parameters = f'?figi={instrument.figi}&from={start_}&to={end_}&interval={interval}'

                # Получаем партию свечей
                candles = self.get(command=command, parameters=parameters)

                # Заносим информацию в базу
                if candles is None:
                    pass
                elif candles['status'] == 'Ok':
                    l = len(candles['payload']['candles'])
                    print(f'Update {l} candles: {instrument.ticker} {interval} {start} {end}')
                    for candle in candles['payload']['candles']:
                        candle = Candle.objects.write(instrument=instrument,
                                                      datetime=candle['time'],
                                                      interval=candle['interval'],
                                                      o=candle['o'],
                                                      c=candle['c'],
                                                      h=candle['h'],
                                                      l=candle['l'],
                                                      v=candle['v'])
                else:
                    print(parameters)
                    print(candles['status'], candles['payload']['code'])
                    print(candles['payload']['message'])

                # Готовим следующий интервал
                if not self.need_next_interval(interval, end, global_end):
                    break
                start, end = self.next_interval(interval, start, end, global_end)

    def shoot_instruments(self):

        instruments = Instrument.objects.all()

        l = len(instruments)
        for n, instrument in enumerate(instruments):
            if self.is_actual(instrument):
                print(f'{n+1}/{l} {instrument}')
                self.shoot_instrument(instrument)

    def shoot_instrument(self, instrument):

        # Получаем состояние стакана
        command = 'market/orderbook'
        parameters = f'?figi={instrument.figi}&depth=20'
        orderbook = self.get(command=command, parameters=parameters)
        if orderbook is None:
            return None
        elif settings.DEBUG:
            print(orderbook)

        # Получаем минутные свечи
        command = '/market/candles'
        end = datetime.utcnow()
        candles = {}
        for interval in self.intervals:
            start = end - self.interval_limits[interval]['max']
            start_ = self.datetime_to_str(start)
            end_ = self.datetime_to_str(end)
            parameters = f'?figi={instrument.figi}&from={start_}&to={end_}&interval={interval}'
            candles_ = self.get(command=command, parameters=parameters)
            if candles_ is None:
                return None
            candles[interval] = candles_

        snapshot = Snapshot.objects.add(instrument=instrument,
                                        orderbook=orderbook,
                                        candles=candles)
        print(snapshot)

    def is_actual(self, instrument):
        command = '/market/candles'
        start = self.datetime_to_str(datetime.utcnow() - self.interval_limits['month']['min'])
        end = self.datetime_to_str(datetime.utcnow())
        parameters = f'?figi={instrument.figi}&from={start}&to={end}&interval=month'
        candles = self.get(command=command, parameters=parameters)
        try:
            if candles['payload']['candles']:
                return True
            else:
                return False
        except TypeError:
            return False
        except KeyError:
            return False

    def datetime_to_str(self, x):
        x = str(x)
        x = x.split('.')[0]
        x = x.replace(' ', 'T')
        x = f'{x}.000000%2B00%3A00'
        return x

    def first_interval(self, interval, start, end):

        # Исправляем возможные пустые значения
        if start is None and interval == self.intervals[0]:
            start = self.start_datetime
        elif start is None and not interval == self.intervals[0]:
            start = end - self.interval_limits[interval]['max']
        if end is None:
            end = self.start_datetime + self.interval_limits[interval]['min']

        # Убираем данные о часовом поясе
        start = start.replace(tzinfo=None)

        # Корректируем диапазоны
        if end - start > self.interval_limits[interval]['max']:
            end = start + self.interval_limits[interval]['max']
        elif end - start < self.interval_limits[interval]['min']:
            start = end - self.interval_limits[interval]['min']
        return start, end

    def need_next_interval(self, interval, end, global_end):
        if global_end - end < self.interval_limits[interval]['min']:
            return False
        else:
            return True

    def next_interval(self, interval, start, end, global_end):
        start = start + self.interval_limits[interval]['max']
        end = end + self.interval_limits[interval]['max']
        if end > global_end:
            end = global_end
        return start, end

    def export_instruments_candles(self, instrument_type=None):

        if instrument_type is None:
            instruments = Instrument.objects.all()
        else:
            instruments = Instrument.objects.filter(type=instrument_type)

        for instrument in instruments:
            pass #TODO
