import requests as r
import json
import urllib.parse

from swarm.models import *
from trader.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'ocs.ru/b2b'
    login = None
    password = None
    company = 'OCS'
    url = 'https://connector.b2b.ocs.ru/api/v2/'

    def __init__(self):
        self.source = Source.objects.take(
            name=self.name,
            login=self.login,
            password=self.password)
        self.token = settings.OCS_TOKEN

        self.cities = []
        self.stocks = []
        self.reserveplaces = []

        super().__init__()

    def run(self, command='update'):

        if command is 'update':

            # Обновление информации об аккаунте
            # self.update_currencies_exchanges()
            # self.update_contactpersons()
            # self.update_payers()
            # self.update_consignees()
            # self.update_finances()

            # Обновление информации о логистики
            self.update_shipment_cities()
            self.update_shipment_points()
            self.update_shipment_delivery_addresses()
            self.update_stocks()
            self.update_reserveplaces()

            # Обновление каталога
            self.update_catalog_categories()
            self.update_catalog_products()

    def get(self, command=''):
        url = f'{self.url}{command}'
        headers = {'X-API-Key': self.token,
                   'accept': 'application/json'}
        result = r.get(url, headers=headers, verify=None)

        if result.status_code == 200:
            return result.json()
        else:
            return None

    def save_data(self, url, content):
        url = f'{url}.json'
        content = json.dumps(content)
        data = SourceData.objects.take(source=self.source, url=url)
        data.save_file(content)

    def update_currencies_exchanges(self):
        command = 'account/currencies/exchanges'
        print(command)
        data = self.get(command)

        self.save_data(url=command, content=data)

        # TODO
        pass

    def update_contactpersons(self):
        command = 'account/contactpersons'
        print(command)
        data = self.get(command)

        self.save_data(url=command, content=data)

        # TODO
        pass

    def update_payers(self):
        command = 'account/payers'
        print(command)
        data = self.get(command)

        self.save_data(url=command, content=data)

        # TODO
        pass

    def update_consignees(self):
        command = 'account/consignees'
        print(command)
        data = self.get(command)

        self.save_data(url=command, content=data)

        # TODO
        pass

    def update_finances(self):
        command = 'account/finances'
        print(command)
        data = self.get(command)

        self.save_data(url=command, content=data)

        # TODO
        pass

    def update_shipment_cities(self):
        command = 'logistic/shipment/cities'
        print(command)
        data = self.get(command)

        self.cities = data

        self.save_data(url=command, content=data)

        # TODO
        pass


    def update_shipment_points(self):
        command = 'logistic/shipment/pickup-points'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get(f'{command}?shipmentCity={city}')

        self.save_data(url=command, content=data)

        # TODO
        pass

    def update_shipment_delivery_addresses(self):
        command = 'logistic/shipment/delivery-addresses'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get(f'{command}?shipmentCity={city}')

        self.save_data(url=command, content=data)

        # TODO
        pass

    def update_stocks(self):
        command = 'logistic/stocks/locations'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get(f'{command}?shipmentCity={city}')

            self.stocks = self.stocks + data

        self.save_data(url=command, content=data)

        # TODO
        pass

    def update_reserveplaces(self):
        command = 'logistic/stocks/reserveplaces'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get(f'{command}?shipmentCity={city}')

            self.reserveplaces = self.reserveplaces + data

        self.save_data(url=command, content=data)

        # TODO
        pass

    def update_catalog_categories(self):
        command = 'catalog/categories'
        print(command)
        data = self.get(command)

        self.save_data(url=command, content=data)

        # TODO
        pass

    def update_catalog_products(self):
        command = 'catalog/categories/all/products'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get(f'{command}?shipmentCity={city}')

        self.save_data(url=command, content=data)

        # TODO
        pass
