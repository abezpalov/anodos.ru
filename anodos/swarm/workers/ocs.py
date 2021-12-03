import time
import requests as r
import json
import urllib.parse
from datetime import datetime, timedelta

from django.utils import timezone
from django.conf import settings

import anodos.tools
import swarm.models
import distributors.models
import swarm.workers.worker


class Worker(swarm.workers.worker.Worker):

    name = 'OCS'
    url = {'api': 'https://connector.b2b.ocs.ru/api/v2/',
           'events': 'https://zubrit.ocs.ru',
           'base': 'https://www.ocs.ru',
           'news': 'https://www.ocs.ru',
           'promo': 'https://www.ocs.ru/Promo'}

    def __init__(self):
        self.source = swarm.models.Source.objects.take(name=self.name)
        self.distributor = distributors.models.Distributor.objects.take(name=self.name)

        self.cities = []
        self.stocks = []
        self.reserveplaces = []

        self.count_of_products = 0
        self.count_of_parties = 0
        self.count_of_news = 0
        self.count_of_prs = 0
        self.count_of_promo = 0
        self.count_of_events = 0
        self.count_of_parameters = 0
        self.count_of_images = 0
        self.message = None

        super().__init__()

    def run(self):

        if self.command == 'update_news':
            self.update_news()
            self.update_promo()
            self.update_events()
            self.message = f'- новостей: {self.count_of_news};\n' \
                           f'- пресс-релизов: {self.count_of_prs};\n' \
                           f'- промо: {self.count_of_promo};\n' \
                           f'- событий: {self.count_of_events}.'

        elif self.command == 'update_stocks':

            # Обновляем информации о логистике
            self.update_shipment_cities()
            self.update_stocks()
            self.update_reserveplaces()

            # Обновляем каталог
            self.update_catalog_categories()
            self.update_catalog_products()

            # Удаляем устаревшие партии
            distributors.models.Party.objects.filter(distributor=self.distributor,
                                                     created__lte=self.start_time).delete()

            # Отправляем оповещение об успешном завершении
            self.message = f'- продуктов: {self.count_of_products};\n' \
                           f'- партий: {self.count_of_parties}.'

        elif self.command == 'update_content_all':
            keys = self.get_keys_for_update_content('all')
            self.update_content(keys)
            self.message = f'- характеристик: {self.count_of_parameters};\n' \
                           f'- фотографий: {self.count_of_images}.'

        elif self.command == 'update_content_clear':
            keys = self.get_keys_for_update_content('clear')
            self.update_content(keys)
            self.message = f'- характеристик: {self.count_of_parameters};\n' \
                           f'- фотографий: {self.count_of_images}.'

        elif self.command == 'update_content_changes_day':
            keys = self.get_keys_for_update_content('day')
            self.update_content(keys)
            self.message = f'- характеристик: {self.count_of_parameters};\n' \
                           f'- фотографий: {self.count_of_images}.'

        elif self.command == 'update_content_changes_week':
            keys = self.get_keys_for_update_content('week')
            self.update_content(keys)
            self.message = f'- характеристик: {self.count_of_parameters};\n' \
                           f'- фотографий: {self.count_of_images}.'

        elif self.command == 'update_content_changes_month':
            keys = self.get_keys_for_update_content('month')
            self.update_content(keys)
            self.message = f'- характеристик: {self.count_of_parameters};\n' \
                           f'- фотографий: {self.count_of_images}.'

        elif self.command == 'drop_parameters':
            distributors.models.Parameter.objects.filter(distributor=self.distributor).delete()
            distributors.models.Parameter.objects.filter(distributor__isnull=True).delete()
            distributors.models.Product.objects.filter(distributor=self.distributor).update(content_loaded=None,
                                                                                            content=None)

        elif self.command == 'all_delete':
            self.distributor.delete()

        else:
            print('Неизвестная команда!')

        if self.message:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}:\n'
                                      f'{self.message}')
        else:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}.\n')

    def get_by_api(self, command='', params=''):

        if params:
            url = f"{self.url['api']}{command}?{params}"
        else:
            url = f"{self.url['api']}{command}"
        headers = {'X-API-Key': settings.OCS_TOKEN,
                   'accept': 'application/json'}
        result = r.get(url, headers=headers, verify=None)

        if result.status_code == 200:
            return result.json()
        else:
            print(f'Error: {result.status_code} in URL {url}')
            return None

    def post_by_api(self, command='', params=''):
        url = f"{self.url['api']}{command}"
        headers = {'X-API-Key': settings.OCS_TOKEN,
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
        data = swarm.models.SourceData.objects.take(source=self.source, url=url)
        data.save_file(content)

    def update_events(self):

        # Заходим на первую страницу
        tree = self.load(url=self.url['events'], result_type='html')

        # Получаем все ссылки
        items = tree.xpath('//div[@class="event-item"]')

        for item in items:
            try:
                event = item.xpath('.//div[@class="event-item-label"]/text()')[0]
                vendor = item.xpath('.//div[@class="event-item-vendors"]/span/text()')[0]
                name = item.xpath('.//a[@class="event-item-title"]/text()')[0]
                url = item.xpath('.//a[@class="event-item-title"]/@href')[0]
                location = item.xpath('.//div[@class="event-item-location"]/text()')[0]
                date = item.xpath('.//div[@class="event-item-date"]/text()')[0]
            except IndexError:
                continue

            if not url.startswith(self.url['events']):
                if url[0] == '/':
                    url = '{}{}'.format(self.url['events'], url)
                else:
                    url = '{}/{}'.format(self.url['events'], url)

            event = anodos.tools.fix_text(event)
            vendor = anodos.tools.fix_text(vendor)
            name = anodos.tools.fix_text(name)
            location = anodos.tools.fix_text(location)
            date = anodos.tools.fix_text(date)

            try:
                data = swarm.models.SourceData.objects.get(source=self.source, url=url)
            except swarm.models.SourceData.DoesNotExist:
                content = f'<b><a href="{url}">{name}</a></b>\n' \
                          f'<i>{date} {location}</i>\n\n' \
                          f'#{self.name} #{event} #{vendor}'
                anodos.tools.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)

                data = swarm.models.SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
            print(data)
            self.count_of_events += 1

    def update_news(self):

        # Заходим на первую страницу
        tree = self.load(url=self.url['news'], result_type='html')

        # Получаем все ссылки
        items = tree.xpath('//div[@class="item item-news"]')

        for item in items:
            try:
                news_type = item.xpath('.//*[@class="header"]//a/text()')[0]
                title = item.xpath('.//*[@class="topic"]//a/text()')[0]
                url = item.xpath('.//*[@class="topic"]//a/@href')[0]
                term = item.xpath('.//*[@class="header"]//em/text()')[0]
                text = item.xpath('.//*[@class="body"]//text()')[0]
            except IndexError:
                continue

            if not url.startswith(self.url['news']):
                if url[0] == '/':
                    url = '{}{}'.format(self.url['base'], url)
                else:
                    url = '{}/{}'.format(self.url['base'], url)

            news_type = anodos.tools.fix_text(news_type)
            title = anodos.tools.fix_text(title)
            term = anodos.tools.fix_text(term)
            text = anodos.tools.fix_text(text)

            try:
                data = swarm.models.SourceData.objects.get(source=self.source, url=url)
            except swarm.models.SourceData.DoesNotExist:
                content = f'<b><a href="{url}">{title}</a></b>\n' \
                          f'<i>{term}</i>\n\n' \
                          f'{text}\n' \
                          f'#{self.name} #{news_type}'
                anodos.tools.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)
                data = swarm.models.SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
            print(data)

            self.count_of_news += 1

        items = tree.xpath('//div[@class="item item-pr"]')
        for item in items:
            try:
                news_type = item.xpath('.//*[@class="header"]//a/text()')[0]
                title = item.xpath('.//*[@class="topic"]//a/text()')[0]
                url = item.xpath('.//*[@class="topic"]//a/@href')[0]
                term = item.xpath('.//*[@class="header"]//em/text()')[0]
                text = item.xpath('.//*[@class="body"]//text()')[0]
            except IndexError:
                continue

            if not url.startswith(self.url['base']):
                if url[0] == '/':
                    url = '{}{}'.format(self.url['base'], url)
                else:
                    url = '{}/{}'.format(self.url['base'], url)

            news_type = anodos.tools.fix_text(news_type)
            title = anodos.tools.fix_text(title)
            term = anodos.tools.fix_text(term)
            text = anodos.tools.fix_text(text)

            try:
                data = swarm.models.SourceData.objects.get(source=self.source, url=url)
            except swarm.models.SourceData.DoesNotExist:
                content = f'<b><a href="{url}">{title}</a></b>\n' \
                          f'<i>{term}</i>\n\n' \
                          f'{text}\n' \
                          f'#{self.name} #{news_type}'
                anodos.tools.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)
                data = swarm.models.SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
            print(data)

            self.count_of_prs += 1

    def update_promo(self):

        # Заходим на первую страницу
        tree = self.load(url=self.url['promo'], result_type='html')

        # Получаем все ссылки
        items = tree.xpath('//div[@class="item"]')
        for item in items:
            try:
                vendor = item.xpath('.//*[@class="vendor"]//text()')[0]
                term = item.xpath('.//*[@class="term"]//text()')[0]
                title = item.xpath('.//h2//text()')[0]
                text = item.xpath('.//div[@class="info"]/p//text()')[0]
                url = item.xpath('.//h2/a/@href')[0]
            except IndexError:
                continue

            if not url.startswith(self.url['base']):
                if url[0] == '/':
                    url = '{}{}'.format(self.url['base'], url)
                else:
                    url = '{}/{}'.format(self.url['base'], url)

            vendor = anodos.tools.fix_text(vendor)
            term = anodos.tools.fix_text(term)
            title = anodos.tools.fix_text(title)
            text = anodos.tools.fix_text(text)

            try:
                data = swarm.models.SourceData.objects.get(source=self.source, url=url)
            except swarm.models.SourceData.DoesNotExist:
                content = f'<b><a href="{url}">{title}</a></b>\n' \
                          f'<i>{term}</i>\n\n' \
                          f'{text}\n' \
                          f'#{self.name} #промо #{vendor}'
                anodos.tools.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)
                data = swarm.models.SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
            print(data)

            self.count_of_promo += 1

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

    def update_shipment_points(self):
        command = 'logistic/shipment/pickup-points'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get_by_api(command, f'shipmentCity={city}')

    def update_shipment_delivery_addresses(self):
        command = 'logistic/shipment/delivery-addresses'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get_by_api(command, f'shipmentCity={city}')

    def update_stocks(self):
        command = 'logistic/stocks/locations'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get_by_api(command, f'shipmentCity={city}')
            self.stocks = self.stocks + data

    def update_reserveplaces(self):
        command = 'logistic/stocks/reserveplaces'
        print(command)
        for city in self.cities:
            city = urllib.parse.quote_plus(city)
            data = self.get_by_api(command, f'shipmentCity={city}')
            self.reserveplaces = self.reserveplaces + data

    def update_catalog_categories(self):
        command = 'catalog/categories'
        print(command)
        data = self.get_by_api(command)

        # Спарсить полученные данные
        self.parse_categories(data)

    def parse_categories(self, data, parent=None):
        for item in data:
            key = item['category']
            name = item['name']
            category = distributors.models.Category.objects.take(distributor=self.distributor,
                                                                 key=key,
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
                data = swarm.models.SourceData.objects.take(source=self.source, url=f'{command}.json')
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
                self.count_of_products += 1

    def parse_product(self, item):
        vendor = distributors.models.Vendor.objects.take(distributor=self.distributor,
                                                         name=item['product']['producer'])
        category = distributors.models.Category.objects.take(distributor=self.distributor,
                                                             key=item['product']['category'])

        product_key = item['product'].get('itemId', None)
        party_key = item['product'].get('productKey', None)
        part_number = item['product'].get('partNumber', None)
        short_name = item['product'].get('productName', None)
        name_rus = item['product'].get('itemNameRus', None)
        name_other = item['product'].get('itemName', None)
        name = f"{name_rus} {name_other}"
        description = item['product'].get('productDescription', None)
        warranty = item['product'].get('warranty', None)

        ean_128 = item['product'].get('eaN128', None)
        upc = item['product'].get('upc', None)
        pnc = item['product'].get('pnc', None)
        hs_code = item['product'].get('hsCode', None)

        traceable = item['product'].get('traceable', None)

        if item['product']['condition'] == 'Regular':
            unconditional = False
            sale = False
        elif item['product']['condition'] == 'Sale':
            unconditional = False
            sale = True
        elif item['product']['condition'] == 'Unconditional':
            unconditional = True
            sale = False

        condition_description = item['product'].get('conditionDescription', None)

        weight = item['packageInformation'].get('weight', None)
        width = item['packageInformation'].get('width', None)
        height = item['packageInformation'].get('height', None)
        depth = item['packageInformation'].get('depth', None)
        volume = item['packageInformation'].get('volume', None)
        multiplicity = item['packageInformation'].get('multiplicity', None)
        unit = distributors.models.Unit.objects.take(key=item['packageInformation'].get('units', None))

        product = distributors.models.Product.objects.take_by_party_key(distributor=self.distributor,
                                                                        party_key=party_key,
                                                                        name=name,
                                                                        vendor=vendor,
                                                                        category=category,
                                                                        product_key=product_key,
                                                                        part_number=part_number,
                                                                        short_name=short_name,
                                                                        name_rus=name_rus,
                                                                        name_other=name_other,
                                                                        description=description,
                                                                        ean_128=ean_128,
                                                                        upc=upc,
                                                                        pnc=pnc,
                                                                        hs_code=hs_code,
                                                                        traceable=traceable,
                                                                        weight=weight,
                                                                        width=width,
                                                                        height=height,
                                                                        depth=depth,
                                                                        volume=volume,
                                                                        multiplicity=multiplicity,
                                                                        unit=unit,
                                                                        warranty=warranty)
        # Удаляем имеющиеся партии товара
        distributors.models.Party.objects.filter(product=product).delete()

        # Получаем актуальную информацию по партиям товара
        is_available_for_order = item.get('isAvailableForOrder', None)

        try:
            price_in = item['price']['order']['value']
            currency_in = item['price']['order']['currency']
            currency_in = currency_in.replace('RUR', 'RUB')
            currency_in = distributors.models.Currency.objects.take(key=currency_in)
        except KeyError:
            price_in = None
            currency_in = None

        try:
            price_out = item['price']['endUser']['value']
            currency_out = item['price']['endUser']['currency']
            currency_out = currency_out.replace('RUR', 'RUB')
            currency_out = distributors.models.Currency.objects.take(key=currency_out)
        except KeyError:
            price_out = None
            currency_out = None

        try:
            price_out_open = item['price']['endUserWeb']['value']
            currency_out_open = item['price']['endUserWeb']['currency']
            currency_out_open = currency_out_open.replace('RUR', 'RUB')
            currency_out_open = distributors.models.Currency.objects.take(key=currency_out_open)
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

            location = distributors.models.Location.objects.take(distributor=self.distributor,
                                                                 key=key,
                                                                 description=description)

            distributors.models.Party.objects.create(distributor=self.distributor,
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
                                                     unit=unit,
                                                     can_reserve=can_reserve,
                                                     is_available_for_order=is_available_for_order,
                                                     unconditional=unconditional,
                                                     sale=sale,
                                                     condition_description=condition_description)
        if len(item['locations']) == 0:
            location = None
            quantity = None
            quantity_great_than = None
            can_reserve = None

            distributors.models.Party.objects.create(distributor=self.distributor,
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
                                                     is_available_for_order=is_available_for_order,
                                                     unconditional=unconditional,
                                                     sale=sale,
                                                     condition_description=condition_description)
            self.count_of_parties += 1
        return product

    def get_keys_for_update_content(self, mode=None):

        keys = []

        if mode == 'all':
            keys_ = distributors.models.Product.objects.filter(distributor=self.distributor).values('product_key')
            for key_ in keys_:
                keys.append(key_['product_key'])

        elif mode == 'clear':
            keys_ = distributors.models.Product.objects.filter(distributor=self.distributor,
                                                               content__isnull=True).values('product_key')
            for key_ in keys_:
                keys.append(key_['product_key'])

        elif mode == 'day':
            command = 'content/changes'
            start = datetime.utcnow() - timedelta(days=1)
            start = self.datetime_to_str(x=start)

            keys_ = self.get_by_api(command=command, params=f'from={start}')
            for key_ in keys_:
                keys.append(key_['itemId'])

        elif mode == 'week':
            command = 'content/changes'
            start = datetime.utcnow() - timedelta(days=7)
            start = self.datetime_to_str(x=start)

            keys_ = self.get_by_api(command=command, params=f'from={start}')
            for key_ in keys_:
                keys.append(key_['itemId'])
            return keys

        elif mode == 'month':
            command = 'content/changes'
            start = datetime.utcnow() - timedelta(days=31)
            start = self.datetime_to_str(x=start)

            keys_ = self.get_by_api(command=command, params=f'from={start}')
            for key_ in keys_:
                keys.append(key_['itemId'])

        return keys

    def update_content(self, keys):
        command = 'content/batch'
        print(command)

        batch_size = settings.OCS_BATCH_SIZE

        # Расчитываем количество партий
        batches_count = len(keys) // batch_size
        if len(keys) % batch_size:
            batches_count += 1

        for n in range(batches_count):
            print(f"{n+1} of {batches_count}")
            batch = json.dumps(keys[n*batch_size:(n+1)*batch_size])

            data = self.post_by_api(command=command, params=batch)

            if data is not None:
                for content in data['result']:
                    self.parse_content(content)

            print('wait')
            time.sleep(18)

    def parse_content(self, content):

        products = distributors.models.Product.objects.filter(distributor=self.distributor,
                                                              product_key=content['itemId'])
        for product in products:

            # description
            description = content.get('description', None)

            # properties
            for parameter in content['properties']:
                name = parameter.get('name', None)
                description = parameter.get('description', None)
                value = parameter.get('value', None)
                unit = parameter.get('unit', None)

                if name:
                    parameter = distributors.models.Parameter.objects.take(distributor=self.distributor,
                                                                           name=name,
                                                                           description=description)
                else:
                    continue

                if unit:
                    unit = distributors.models.ParameterUnit.objects.take(key=unit)

                parameter_value = distributors.models.ParameterValue.objects.take(distributor=self.distributor,
                                                                                  product=product,
                                                                                  parameter=parameter,
                                                                                  value=value,
                                                                                  unit=unit)
                print(parameter_value)
                self.count_of_parameters += 1

            # images
            for image in content['images']:
                url = image.get('url', None)
                image = distributors.models.ProductImage.objects.take(product=product, source_url=url)
                print(image)
                self.count_of_images += 1

            product.content_loaded = timezone.now()
            product.content = content
            product.save()

            url = f'{settings.HOST}/distributors/product/{product.id}/'

    @staticmethod
    def datetime_to_str(x):
        x = str(x)
        x = x.split('.')[0]
        x = x.replace(' ', 'T')
        x = f'{x}.000000%2B00%3A00'
        return x
