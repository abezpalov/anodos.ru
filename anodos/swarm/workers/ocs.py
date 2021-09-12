import time
import requests as r
import json
import urllib.parse

from django.utils import timezone

from swarm.models import *
from distributors.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    source_name = 'ocs.ru'
    name = 'OCS'
    login = None
    password = None
    url = {'api': 'https://connector.b2b.ocs.ru/api/v2/',
           'events': 'https://zubrit.ocs.ru',
           'base': 'https://www.ocs.ru',
           'news': 'https://www.ocs.ru',
           'promo': 'https://www.ocs.ru/Promo'
           }

    def __init__(self):
        self.start_time = timezone.now()
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

    def run(self, command=None):

        self.send(f'OCS run {command}')

        if command is None:
            print('Без команды не работаю!')

        elif command == 'update_events':
            self.update_events()

        elif command == 'update_news':
            self.update_news()

        elif command == 'update_promo':
            self.update_promo()

        elif command == 'update_stocks':

            # Обновляем информации о логистике
            self.update_shipment_cities()
            self.update_stocks()
            self.update_reserveplaces()

            # Обновляем каталог
            self.update_catalog_categories()
            self.update_catalog_products()

            # Удаляем устаревшие партии
            Party.objects.filter(distributor=self.distributor,
                                 created__lte=self.start_time).delete()

        elif command == 'update_content':
            self.update_content()

        elif command == 'all_delete':
            self.distributor.delete()

    def get_by_api(self, command='', params=''):

        if params:
            url = f"{self.url['api']}{command}?{params}"
        else:
            url = f"{self.url['api']}{command}"
        headers = {'X-API-Key': self.token,
                   'accept': 'application/json'}
        result = r.get(url, headers=headers, verify=None)

        if result.status_code == 200:
            return result.json()
        else:
            print(f'Error: {result.status_code} in URL {url}')
            return None

    def post_by_api(self, command='', params=''):
        url = f"{self.url['api']}{command}"
        headers = {'X-API-Key': self.token,
                   'accept': 'application/json',
                   'Content-Type': 'application/json'}

        result = r.post(url, headers=headers, data=str(params), verify=None)
        if result.status_code == 200:
            return result.json()
        else:
            print(f'Error: {result.status_code} in URL {url}')
            return None

    def save_data(self, url, content):
        url = f'{url}.json'
        content = json.dumps(content)
        data = SourceData.objects.take(source=self.source, url=url)
        data.save_file(content)

    def update_events(self):

        # Заходим на первую страницу
        tree = self.load(url=self.url['events'], result_type='html')

        # Получаем все ссылки
        items = tree.xpath('//div[@class="event-item"]')

        for item in items:
            event = item.xpath('.//div[@class="event-item-label"]/text()')[0]
            event = self.fix_text(event)

            vendor = item.xpath('.//div[@class="event-item-vendors"]/span/text()')[0]
            vendor = self.fix_text(vendor)

            name = item.xpath('.//a[@class="event-item-title"]/text()')[0]
            name = self.fix_text(name)

            url = item.xpath('.//a[@class="event-item-title"]/@href')[0]
            if not url.startswith(self.url['events']):
                if url[0] == '/':
                    url = '{}{}'.format(self.url['events'], url)
                else:
                    url = '{}/{}'.format(self.url['events'], url)

            location = item.xpath('.//div[@class="event-item-location"]/text()')[0]
            location = self.fix_text(location)

            date = item.xpath('.//div[@class="event-item-date"]/text()')[0]
            date = self.fix_text(date)

            try:
                data = SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:
                content = f'<b>{event} {vendor}</b>\n' \
                          f'<i>{date} {location}</i>\n\n' \
                          f'<a href="{url}">{name}</a>'
                self.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)

                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
            print(data)

        # Отправляем отчёт
        self.send(f'Нашёл {len(items)} мероприятий у {self.name}')

    def update_news(self):

        # Заходим на первую страницу
        tree = self.load(url=self.url['news'], result_type='html')

        # Получаем все ссылки
        items = tree.xpath('//div[@class="item item-news"]')

        for item in items:
            news_type = item.xpath('.//*[@class="header"]//a/text()')[0]
            title = item.xpath('.//*[@class="topic"]//a/text()')[0]
            url = item.xpath('.//*[@class="topic"]//a/@href')[0]
            term = item.xpath('.//*[@class="header"]//em/text()')[0]
            text = item.xpath('.//*[@class="body"]//text()')[0]
            if not url.startswith(self.url['news']):
                if url[0] == '/':
                    url = '{}{}'.format(self.url['base'], url)
                else:
                    url = '{}/{}'.format(self.url['base'], url)

            try:
                data = SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:
                content = f'<b>{news_type} {self.name}</b>\n' \
                          f'<i>{term}</i>\n\n' \
                          f'<a href="{url}">{title}</a>\n' \
                          f'{text}\n'
                self.send(content)
                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
            print(data)

        # Отправляем отчёт
        self.send(f'Нашёл {len(items)} новостей у {self.name}')

        items = tree.xpath('//div[@class="item item-pr"]')
        for item in items:
            news_type = item.xpath('.//*[@class="header"]//a/text()')[0]
            title = item.xpath('.//*[@class="topic"]//a/text()')[0]
            url = item.xpath('.//*[@class="topic"]//a/@href')[0]
            term = item.xpath('.//*[@class="header"]//em/text()')[0]
            text = item.xpath('.//*[@class="body"]//text()')[0]
            if not url.startswith(self.url['base']):
                if url[0] == '/':
                    url = '{}{}'.format(self.url['base'], url)
                else:
                    url = '{}/{}'.format(self.url['base'], url)

            try:
                data = SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:
                content = f'<b>{news_type} {self.name}</b>\n' \
                          f'<i>{term}</i>\n\n' \
                          f'<a href="{url}">{title}</a>\n' \
                          f'{text}'
                self.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)
                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
            print(data)

        # Отправляем отчёт
        self.send(f'Нашёл {len(items)} пресс-релизов у {self.name}')

    def update_promo(self):

        # Заходим на первую страницу
        tree = self.load(url=self.url['promo'], result_type='html')

        # Получаем все ссылки
        items = tree.xpath('//div[@class="item"]')
        for item in items:
            vendor = item.xpath('.//*[@class="vendor"]//text()')[0]
            term = item.xpath('.//*[@class="term"]//text()')[0]
            title = item.xpath('.//h2//text()')[0]
            text = item.xpath('.//div[@class="info"]/p//text()')[0]
            url = item.xpath('.//h2/a/@href')[0]
            if not url.startswith(self.url['base']):
                if url[0] == '/':
                    url = '{}{}'.format(self.url['base'], url)
                else:
                    url = '{}/{}'.format(self.url['base'], url)

            try:
                data = SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:
                content = f'<b>Промо-акция {self.name} и {vendor}</b>\n' \
                          f'<i>{term}</i>\n\n' \
                          f'<a href="{url}">{title}</a>\n' \
                          f'{text}'
                self.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)
                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
            print(data)

        # Отправляем отчёт
        self.send(f'Нашёл {len(items)} промо у {self.name}')

    def send_info(self):
        count_products = Product.objects.filter(distributor=self.distributor).count()
        count_parties = Party.objects.filter(distributor=self.distributor).count()
        count_photos = ProductImage.objects.filter(product__distributor=self.distributor).count()
        count_parameter_values = ParameterValue.objects.filter(distributor=self.distributor).count()
        count_product_contents = Product.objects.filter(content__isnull=False).count()

        self.send(f'OCS end\n'
                  f'count_products = {count_products}\n'
                  f'count_parties = {count_parties}\n'
                  f'count_photos = {count_photos}\n'
                  f'count_parameter_values = {count_parameter_values}\n'
                  f'count_product_contents = {count_product_contents}\n')

    def update_currencies_exchanges(self):
        command = 'account/currencies/exchanges'
        print(command)
        data = self.get_by_api(command)

        # TODO
        pass

    def update_contactpersons(self):
        command = 'account/contactpersons'
        print(command)
        data = self.get_by_api(command)

        # TODO
        pass

    def update_payers(self):
        command = 'account/payers'
        print(command)
        data = self.get_by_api(command)

        # TODO
        pass

    def update_consignees(self):
        command = 'account/consignees'
        print(command)
        data = self.get_by_api(command)

        # TODO
        pass

    def update_finances(self):
        command = 'account/finances'
        print(command)
        data = self.get_by_api(command)

        # TODO
        pass

    def update_shipment_cities(self):
        command = 'logistic/shipment/cities'
        print(command)
        data = self.get_by_api(command)

        self.cities = data

        # TODO
        pass

    def update_shipment_points(self):
        command = 'logistic/shipment/pickup-points'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get_by_api(command, f'shipmentCity={city}')

        # TODO
        pass

    def update_shipment_delivery_addresses(self):
        command = 'logistic/shipment/delivery-addresses'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get_by_api(command, f'shipmentCity={city}')

        # TODO
        pass

    def update_stocks(self):
        command = 'logistic/stocks/locations'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get_by_api(command, f'shipmentCity={city}')

            self.stocks = self.stocks + data

        # TODO
        pass

    def update_reserveplaces(self):
        command = 'logistic/stocks/reserveplaces'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get_by_api(command, f'shipmentCity={city}')

            self.reserveplaces = self.reserveplaces + data

        # TODO
        pass

    def update_catalog_categories(self):
        command = 'catalog/categories'
        print(command)
        data = self.get_by_api(command)

        # Спарсить полученные данные
        self.parse_categories(data)

    def parse_categories(self, data, parent=None):
        for item in data:
            article = item['category']
            name = item['name']
            category = Category.objects.take(
                distributor=self.distributor,
                article=article,
                name=name,
                parent=parent)
            print(category)
            if item['children']:
                self.parse_categories(item['children'], category)

    def update_catalog_products(self):
        command = 'catalog/categories/all/products'
        print(command)

        for city in self.cities:
            if settings.OCS_TEST:
                data = SourceData.objects.take(source=self.source, url=f'{command}.json')
                data = data.load_file()
                data = json.loads(data)
            else:
                city = urllib.parse.quote_plus(city)
                data = self.get_by_api(command,
                                       f'shipmentCity={city}&&includesale=true'
                                       f'&includeuncondition=true&includemissing=true')

            for n, item in enumerate(data['result']):
                product = self.parse_product(item)
                print(f"{n + 1} of {len(data['result'])} {product}")

    def parse_product(self, item):
        vendor = Vendor.objects.take(distributor=self.distributor,
                                     name=item['product']['producer'])
        category = Category.objects.take(distributor=self.distributor,
                                         article=item['product']['category'])
        condition = Condition.objects.take(distributor=self.distributor,
                                           name=item['product']['condition'])

        product_key = item['product'].get('itemId', None)
        party_key = item['product'].get('productKey', None)
        article = item['product'].get('partNumber', None)
        short_name = item['product'].get('productName', None)
        name_rus = item['product'].get('itemNameRus', None)
        name_other = item['product'].get('itemName', None)
        name = f"{name_rus} {name_other}"
        description = item['product'].get('productDescription', None)

        ean_128 = item['product'].get('eaN128', None)
        upc = item['product'].get('upc', None)
        pnc = item['product'].get('pnc', None)
        hs_code = item['product'].get('hsCode', None)

        traceable = item['product'].get('traceable', None)
        condition_description = item['product'].get('conditionDescription', None)

        weight = item['packageInformation'].get('weight', None)
        width = item['packageInformation'].get('width', None)
        height = item['packageInformation'].get('height', None)
        depth = item['packageInformation'].get('depth', None)
        volume = item['packageInformation'].get('volume', None)
        multiplicity = item['packageInformation'].get('multiplicity', None)
        unit = Unit.objects.take(key=item['packageInformation'].get('units', None))

        product = Product.objects.take_by_party_key(distributor=self.distributor,
                                                    party_key=party_key,
                                                    name=name,
                                                    vendor=vendor,
                                                    category=category,
                                                    condition=condition,
                                                    product_key=product_key,
                                                    article=article,
                                                    short_name=short_name,
                                                    name_rus=name_rus,
                                                    name_other=name_other,
                                                    description=description,
                                                    ean_128=ean_128,
                                                    upc=upc,
                                                    pnc=pnc,
                                                    hs_code=hs_code,
                                                    traceable=traceable,
                                                    condition_description=condition_description,
                                                    weight=weight,
                                                    width=width,
                                                    height=height,
                                                    depth=depth,
                                                    volume=volume,
                                                    multiplicity=multiplicity,
                                                    unit=unit)

        # Удаляем имеющиеся партии товара
        Party.objects.filter(distributor=self.distributor, product=product).delete()

        # Получаем актуальную информацию по партиям товара
        is_available_for_order = item.get('isAvailableForOrder', None)

        try:
            price_in = item['price']['order']['value']
            currency_in = item['price']['order']['currency']
            currency_in = Currency.objects.take(key=currency_in)
        except KeyError:
            price_in = None
            currency_in = None

        try:
            price_out = item['price']['endUser']['value']
            currency_out = item['price']['endUser']['currency']
            currency_out = Currency.objects.take(key=currency_out)
        except KeyError:
            price_out = None
            currency_out = None

        try:
            price_out_open = item['price']['endUserWeb']['value']
            currency_out_open = item['price']['endUserWeb']['currency']
            currency_out_open = Currency.objects.take(key=currency_out_open)
        except KeyError:
            price_out_open = None
            currency_out_open = None

        try:
            must_keep_end_user_price = item['price']['must_keep_end_user_price']
        except KeyError:
            must_keep_end_user_price = None

        for location in item['locations']:
            key = location['location']
            description = location.get('description')

            quantity = location['quantity']['value']
            quantity_great_than = location['quantity'].get('isGreatThan', False)

            can_reserve = location.get('canReserve', None)

            location = Location.objects.take(key=key,
                                             description=description)

            party = Party.objects.create(distributor=self.distributor,
                                         product=product,
                                         price_in=price_in,
                                         currency_in=currency_in,
                                         price_out=price_out,
                                         currency_out=currency_out,
                                         price_out_open=price_out_open,
                                         currency_out_open=currency_out_open,
                                         must_keep_end_user_price=must_keep_end_user_price,
                                         location=location,
                                         quantity=quantity,
                                         quantity_great_than=quantity_great_than,
                                         can_reserve=can_reserve,
                                         is_available_for_order=is_available_for_order)

        if len(item['locations']) == 0:
            location = None
            quantity = None
            quantity_great_than = None
            can_reserve = None

            party = Party.objects.create(distributor=self.distributor,
                                         product=product,
                                         price_in=price_in,
                                         currency_in=currency_in,
                                         price_out=price_out,
                                         currency_out=currency_out,
                                         price_out_open=price_out_open,
                                         currency_out_open=currency_out_open,
                                         must_keep_end_user_price=must_keep_end_user_price,
                                         location=location,
                                         quantity=quantity,
                                         quantity_great_than=quantity_great_than,
                                         can_reserve=can_reserve,
                                         is_available_for_order=is_available_for_order)

        return product

    def update_content(self):
        command = 'content/batch'
        print(command)

        batch_size = settings.OCS_BATCH_SIZE

        # Получаем идентификаторы продуктов, которые нуждаются в обновлении контента
        ids_ = Product.objects.filter(distributor=self.distributor, content__isnull=True).values('product_key')

        ids = []
        for id_ in ids_:
            ids.append(id_['product_key'])

        # random.shuffle(ids)

        # Расчитываем количество партий
        batches_count = len(ids) // batch_size
        if len(ids) % batch_size:
            batches_count += 1

        for n in range(batches_count):
            print(f"{n+1} of {batches_count}")
            self.send(f"{n+1} of {batches_count} batch load")
            batch = json.dumps(ids[n*batch_size:(n+1)*batch_size])

            print(batch)

            data = self.post_by_api(command=command, params=batch)

            if data is not None:
                print(f"Получил контент по {len(data['result'])} продуктам")
                for content in data['result']:
                    self.parse_content(content)

            print('wait')
            time.sleep(18)

    def parse_content(self, content):

        products = Product.objects.filter(distributor=self.distributor,
                                          product_key=content['itemId'])
        for product in products:

            print(product)

            # description
            description = content.get('description', None)

            # properties
            for parameter in content['properties']:
                group = parameter.get('group', None)
                name = parameter.get('name', None)
                description = parameter.get('description', None)
                value = parameter.get('value', None)
                unit = parameter.get('unit', None)

                if group:
                    group = ParameterGroup.objects.take(distributor=self.distributor, name=group)

                if name:
                    parameter = Parameter.objects.take(distributor=self.distributor,
                                                       group=group,
                                                       name=name,
                                                       description=description)
                else:
                    continue

                if unit:
                    unit = ParameterUnit.objects.take(key=unit)

                parameter_value = ParameterValue.objects.take(distributor=self.distributor,
                                                              product=product,
                                                              parameter=parameter,
                                                              value=value,
                                                              unit=unit)
                print(parameter_value)

            # images
            for image in content['images']:
                url = image.get('url', None)
                image = ProductImage.objects.take(product=product, source_url=url)
                print(image)

            product.content_loaded = timezone.now()
            product.content = content
            product.save()

            self.send(f'Content loaded: {product}')
