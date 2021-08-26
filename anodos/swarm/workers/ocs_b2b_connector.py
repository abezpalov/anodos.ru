import requests as r
import json
import urllib.parse

from swarm.models import *
from distributors.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    source_name = 'ocs.ru/b2b'
    name = 'OCS'
    login = None
    password = None
    company = 'OCS'
    url = 'https://connector.b2b.ocs.ru/api/v2/'

    def __init__(self):
        self.source = Source.objects.take(
            name=self.source_name,
            login=self.login,
            password=self.password)
        self.distributor = Distributor.objects.take(
            name=self.name
        )
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

    def get(self, command='', params=''):
        if self.token:

            if params:
                url = f'{self.url}{command}?{params}'
            else:
                url = f'{self.url}{command}'
            headers = {'X-API-Key': self.token,
                       'accept': 'application/json'}
            result = r.get(url, headers=headers, verify=None)

            if result.status_code == 200:
                return result.json()
            else:
                return None
        else:
            url = f'{command}.json'
            data = SourceData.objects.take(source=self.source, url=url)
            data = data.load_file()
            data = json.loads(data)
        return data

    def save_data(self, url, content):
        url = f'{url}.json'
        content = json.dumps(content)
        data = SourceData.objects.take(source=self.source, url=url)
        data.save_file(content)

    def update_currencies_exchanges(self):
        command = 'account/currencies/exchanges'
        print(command)
        data = self.get(command)

        if self.token:
            self.save_data(url=command, content=data)
        # TODO
        pass

    def update_contactpersons(self):
        command = 'account/contactpersons'
        print(command)
        data = self.get(command)

        if self.token:
            self.save_data(url=command, content=data)
        # TODO
        pass

    def update_payers(self):
        command = 'account/payers'
        print(command)
        data = self.get(command)

        if self.token:
            self.save_data(url=command, content=data)
        # TODO
        pass

    def update_consignees(self):
        command = 'account/consignees'
        print(command)
        data = self.get(command)

        if self.token:
            self.save_data(url=command, content=data)
        # TODO
        pass

    def update_finances(self):
        command = 'account/finances'
        print(command)
        data = self.get(command)

        if self.token:
            self.save_data(url=command, content=data)

        # TODO
        pass

    def update_shipment_cities(self):
        command = 'logistic/shipment/cities'
        print(command)
        data = self.get(command)

        self.cities = data

        if self.token:
            self.save_data(url=command, content=data)

        # TODO
        pass

    def update_shipment_points(self):
        command = 'logistic/shipment/pickup-points'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get(command, f'shipmentCity={city}')

        if self.token:
            self.save_data(url=command, content=data)

        # TODO
        pass

    def update_shipment_delivery_addresses(self):
        command = 'logistic/shipment/delivery-addresses'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get(command, f'shipmentCity={city}')

        if self.token:
            self.save_data(url=command, content=data)

        # TODO
        pass

    def update_stocks(self):
        command = 'logistic/stocks/locations'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get(command, f'shipmentCity={city}')

            self.stocks = self.stocks + data

        if self.token:
            self.save_data(url=command, content=data)

        # TODO
        pass

    def update_reserveplaces(self):
        command = 'logistic/stocks/reserveplaces'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get(command, f'shipmentCity={city}')

            self.reserveplaces = self.reserveplaces + data

        if self.token:
            self.save_data(url=command, content=data)

        # TODO
        pass

    def update_catalog_categories(self):

        # Получить данные через API или из файла обмена
        command = 'catalog/categories'
        print(command)
        data = self.get(command)

        # Если загрузка была через API, выгрузить данные в файл обмена
        if self.token:
            self.save_data(url=command, content=data)

        # Спарсить полученные данные
        self.parse_categories(data)

    def parse_categories(self, data, parent=None):
        for item in data:
            name = f"{item['name']} [{item['category']}]"
            category = Category.objects.take(
                distributor=self.distributor,
                name=name,
                parent=parent
            )
            print(category)
            if item['children']:
                self.parse_categories(item['children'], category)

    def update_catalog_products(self):

        # Получить данные через API или из файла обмена
        command = 'catalog/categories/all/products'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get(command, f'shipmentCity={city}&includesale=true&includeuncondition=true')

        # Если загрузка была через API, выгрузить данные в файл обмена
        if self.token:
            self.save_data(url=command, content=data)

        # TODO
        for n, item in enumerate(data['result']):
            vendor = Vendor.objects.take(distributor=self.distributor,
                                         name=item['product']['producer'])
            category = Category.objects.get_by_article(distributor=self.distributor,
                                                       article=item['product']['category'])
            condition = Condition.objects.take(distributor=self.distributor,
                                               name=item['product']['condition'])

            product_key = item['product'].get('itemId', None)
            party_key = item['product'].get('productKey', None)
            article = item['product'].get('partNumber', None)
            name = item['product'].get('productName', None)
            name_rus = item['product'].get('itemNameRus', None)
            name_other = item['product'].get('itemName', None)
            description = item['product'].get('productDescription', None)

            eaN128 = item['product'].get('eaN128', None)
            upc = item['product'].get('upc', None)
            pnc = item['product'].get('pnc', None)
            hsCode = item['product'].get('hsCode', None)

            traceable = item['product'].get('traceable', None)
            condition_description = item['product'].get('conditionDescription', None)

            product = Product.objects.take_by_party_key(distributor=self.distributor,
                                                        party_key=party_key,
                                                        name=name,
                                                        vendor=vendor,
                                                        category=category,
                                                        condition=condition,
                                                        product_key=product_key,
                                                        article=article,
                                                        name_rus=name_rus,
                                                        name_other=name_other,
                                                        description=description,
                                                        eaN128=eaN128,
                                                        upc=upc,
                                                        pnc=pnc,
                                                        hsCode=hsCode,
                                                        traceable=traceable,
                                                        condition_description=condition_description)

            print(f"{n+1} of {len(data['result'])} {product}")
