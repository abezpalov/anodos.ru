import requests as r
import json

from django.utils import timezone
from datetime import timedelta

from swarm.models import *
from trader.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'tinkoff.ru/invest/collector'
    login = None
    password = None
    company = 'Tinkoff'
    url = 'https://api-invest.tinkoff.ru/openapi/'

    def __init__(self):
        self.source = Source.objects.take(
            name=self.name,
            login=self.login,
            password=self.password)
        self.token = settings.TINKOFF_TOKEN

        super().__init__()

    def run(self):

        # Обновляем список инструментов
        self.get_stocks()
        # self.get_bonds()
        # self.get_etfs()
        # self.get_currencies()

        # Получаем информацию о текущих торгах
        while True:
            self.get_stocks_now()

    def get(self, command='', parameters=''):
        url = f'{self.url}{command}{parameters}'
        headers = {'Authorization': f'Bearer {self.token}',
                   'accept': 'application/json'}
        result = r.get(url, headers=headers, verify=None)
        return result.json()

    def get_stocks(self):
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

    def get_bonds(self):
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

    def get_etfs(self):
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

    def get_currencies(self):
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

    def get_stocks_now(self):
        stocks = Instrument.objects.filter(type='Stock')
        l = len(stocks)
        for n, stock in enumerate(stocks):
            print(f'{n+1}/{l} {stock}')

            # Получаем состояние стакана
            command = 'market/orderbook'
            parameters = f'?figi={stock.figi}&depth=20'
            orderbook = self.get(command=command, parameters=parameters)

            # Получаем минутные свечи за 3 часа
            command = '/market/candles'
            now = timezone.now()
            start = self.datetime_to_str(now - timedelta(hours=3))
            end = self.datetime_to_str(now)
            parameters = f'?figi={stock.figi}&from={start}&to={end}&interval=1min'
            candles = self.get(command=command, parameters=parameters)

            snapshot = Snapshot.objects.add(instrument=stock,
                                            orderbook=orderbook,
                                            candles=candles)
            print(snapshot)

    def datetime_to_str(self, x):
        x = str(x)
        x = x.replace(' ', 'T')
        x = x.replace(':', '%3A')
        x = x.replace('+', '%2B')
        return x
