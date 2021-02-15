import requests as r
import json

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
        self.get_bonds()
        self.get_etfs()
        self.get_currencies()

        # Получаем информацию о текущих торгах
        self.get_stocks_orderbooks()


    def post(self, command=''):
        url = f'{self.url}{command}'
        print(url)
        headers = {'Authorization': f'Bearer {self.token}',
                   'accept': 'application/json'}
        result = r.get(url, headers=headers, verify=None)
        return result.json()

    def get_stocks(self):
        stocks = self.post(command='market/stocks')
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
        bonds = self.post(command='market/bonds')
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
        etfs = self.post(command='market/etfs')
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
        currencies = self.post(command='market/currencies')
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

    def get_stocks_orderbooks(self):

        stocks = Instruments.objects.filter(type='Stock')
        for stock in stocks:


