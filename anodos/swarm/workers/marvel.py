from datetime import datetime, timedelta

from django.utils import timezone
from django.conf import settings

import anodos.tools
import swarm.models
import distributors.models
import swarm.workers.worker


class Worker(swarm.workers.worker.Worker):

    name = 'Marvel'
    url = {'api': '',
           'base': ''}

    def __init__(self):
        self.source = swarm.models.Source.objects.take(name=self.name)
        self.distributor = distributors.models.Distributor.objects.take(name=self.name)
        self.stock_on_msk = distributors.models.Location.objects.take(distributor=self.distributor,
                                                                      key='Склад в Москве')
        self.stock_on_spb = distributors.models.Location.objects.take(distributor=self.distributor,
                                                                      key='Склад в Санк-Петербурге')
        self.near_transit = distributors.models.Location.objects.take(distributor=self.distributor,
                                                                      key='Ближний транзит')
        self.far_transit = distributors.models.Location.objects.take(distributor=self.distributor,
                                                                     key='Дальний транзит')

        self.count_of_news = 0
        self.count_of_products = 0
        self.count_of_parties = 0
        self.count_of_parameters = 0
        self.count_of_images = 0
        self.message = None

        super().__init__()

    def run(self):

        if self.command == 'update_news':
            pass

        elif self.command == 'update_stocks':
            self.update_catalog_categories()
            self.update_products()

            # Отправляем оповещение об успешном завершении
            self.message = f'- продуктов: {self.count_of_products};\n' \
                           f'- партий: {self.count_of_parties}.'

        elif self.command == 'update_content_all':
            keys = self.get_keys_for_update_content(mode='all')
            self.update_content(keys=keys, mode='all')
            self.message = f'- характеристик: {self.count_of_parameters};\n' \
                           f'- фотографий: {self.count_of_images}.'

        elif self.command == 'update_content_clear':
            keys = self.get_keys_for_update_content(mode='clear')
            self.update_content(keys=keys, mode='clear')
            self.message = f'- характеристик: {self.count_of_parameters};\n' \
                           f'- фотографий: {self.count_of_images}.'

        elif self.command == 'update_content_day':
            keys = self.get_keys_for_update_content(mode='day')
            self.update_content(keys=keys, mode='day')
            self.message = f'- характеристик: {self.count_of_parameters};\n' \
                           f'- фотографий: {self.count_of_images}.'

        elif self.command == 'update_content_week':
            keys = self.get_keys_for_update_content(mode='week')
            self.update_content(keys=keys, mode='week')
            self.message = f'- характеристик: {self.count_of_parameters};\n' \
                           f'- фотографий: {self.count_of_images}.'

        elif self.command == 'update_content_month':
            keys = self.get_keys_for_update_content(mode='month')
            self.update_content(keys=keys, mode='month')
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

    def save_data(self, url, content):
        url = f'{url}.json'
        content = str(content)
        data = swarm.models.SourceData.objects.take(source=self.source, url=url)
        data.save_file(content)

    def update_news(self):
        pass

    def update_catalog_categories(self):
        url = f'https://b2b.marvel.ru/Api/GetCatalogCategories' \
              f'?user={settings.MARVEL_LOGIN}' \
              f'&password={settings.MARVEL_PASSWORD}' \
              f'&responseFormat=1' \
              f'&instock=1'

        # Получаем данные через API
        data = self.load(url=url, result_type='json', request_type='POST')
        # data = self.load(url=url, result_type='text', request_type='POST')
        # self.save_data(url='b2b.marvel.ru/Api/GetCatalogCategories', content=data)

        # Парсим корневую категорию
        if data['Header']['Code'] == 0:
            self.parse_categories(data=data['Body']['Categories'])
        else:
            print('Ошибка!', data['Header']['Message'])

    def parse_categories(self, data, parent=None):
        for item in data:
            key = item.get('CategoryID', None)
            name = item.get('CategoryName', None)
            category = distributors.models.Category.objects.take(distributor=self.distributor,
                                                                 key=key,
                                                                 name=name,
                                                                 parent=parent)
            print(category)
            if item.get('SubCategories', None):
                self.parse_categories(item['SubCategories'], category)

    def update_products(self):
        url = f'https://b2b.marvel.ru/Api/GetFullStock' \
              f'?user={settings.MARVEL_LOGIN}' \
              f'&password={settings.MARVEL_PASSWORD}' \
              f'&packStatus=0' \
              f'&responseFormat=1' \
              f'&instock=2' \
              f'&updatedSince='

        # Получаем данные через API
        data = self.load(url=url, result_type='json', request_type='POST')

        # Парсим продукты
        if data['Header']['Code'] == 0:
            self.parse_products(data=data['Body']['CategoryItem'])
        else:
            print('Ошибка!', data['Header']['Message'])

    def parse_products(self, data):

        ware_pack_statuses = set()
        dimensions = set()

        for n, item in enumerate(data):

            # TODO Product

            # Производитель
            vendor = item.get('WareVendor', None)
            vendor = distributors.models.Vendor.objects.take(distributor=self.distributor,
                                                             name=vendor)

            # Категория
            category = item['Categories']['Category'][0]['CategoryId']
            category = distributors.models.Category.objects.take(distributor=self.distributor,
                                                                 key=category)

            # Ключи
            product_key = None
            party_key = None
            part_number = item.get('WareArticle', None)

            # Наименование
            name = item.get('WareFullName', None)
            name = anodos.tools.fix_text(name)

            short_name = None
            name_rus = None
            name_other = None

            # Описание
            description = None
            warranty = None

            # Масса нетто
            weight_net = item.get('NetWeight', None)
            weight_net = anodos.tools.fix_float(weight_net)

            # Масса брутто
            weight = item.get('Weight', None)
            weight = anodos.tools.fix_float(weight)

            # Объём
            # "UnitVolume": "0.000510000000",
            volume = item.get('UnitVolume', None)
            volume = anodos.tools.fix_float(volume)
            if volume:
                volume = volume / 100.0

            # Ширина
            # "Width": "8.500000000000",
            width = item.get('Width', None)
            width = anodos.tools.fix_float(width)
            if width:
                width = width / 100.0

            # Высота
            # "Height": "12.000000000000",
            height = item.get('Height', None)
            height = anodos.tools.fix_float(height)
            if height:
                height = height / 100.0

            # Глубина
            # "Depth": "5.000000000000",
            depth = item.get('Depth', None)
            depth = anodos.tools.fix_float(depth)
            if depth:
                depth = depth / 100.0

            product = distributors.models.Product.objects.take_by_part_number(distributor=self.distributor,
                                                                              product_key=product_key,
                                                                              party_key=party_key,
                                                                              part_number=part_number,
                                                                              vendor=vendor,
                                                                              category=category,
                                                                              name=name,
                                                                              description=description,
                                                                              warranty=warranty,
                                                                              gtin=None,
                                                                              tnved=None,
                                                                              traceable=None,
                                                                              weight=weight,
                                                                              width=width,
                                                                              height=height,
                                                                              depth=depth,
                                                                              volume=volume)
            print(f'{n+1} of {len(data)} {product}')

            if product is not None:
                self.count_of_products += 1

                # TODO Party

                # Цена
                price_in = item.get('WarePrice', None)
                price_in = anodos.tools.fix_float(price_in)

                # Валюта
                currency_in = item.get('WarePriceCurrency', None)
                currency_in = distributors.models.Currency.objects.take(key=currency_in)

                # Цена в рублях по внутреннему курсу
                price_in_rub = item.get('WarePriceRUB', None)
                price_in_rub = anodos.tools.fix_float(price_in_rub)

                # Рекомендованная розничная цена
                price_out = item.get('RRPrice', None)

                # Состояние упаковки
                ware_pack_status = item.get('WarePackStatus', None)
                ware_pack_statuses.add(ware_pack_status)
                if ware_pack_status == 'OK':
                    unconditional = False
                else:
                    unconditional = True

                # Информация о промо-программах
                promo_description = item.get('PromoDescription', None)
                promo_url = item.get('PromoDescription', None)
                if promo_description:
                    promo = True
                else:
                    promo = False

                # Локация склада
                dimension = item.get('Dimension', None)
                dimensions.add(dimension)

                if dimension == 'осн':

                    # Количество на складе в Москве
                    quantity_on_msk = item.get('AvailableForB2BOrderQtyInMSK', None)
                    quantity_on_msk, great_than_on_msk = self.fix_quantity(quantity_on_msk)

                    # Количество на складе в Питере
                    quantity_on_spb = item.get('AvailableForB2BOrderQtyInSPB', None)
                    quantity_on_spb, great_than_on_spb = self.fix_quantity(quantity_on_spb)

                    # Свободное количество, доступное для отгрузки через b2b
                    quantity_for_order = item.get('AvailableForB2BOrderQty', None)
                    quantity_for_order, great_than_for_order = self.fix_quantity(quantity_for_order)

                    # Ближний транзит (поступление на склад в течение 1-7 дней)
                    quantity_on_near_transit = item.get('InNearTransitCount', None)
                    quantity_on_near_transit, great_than_on_near_transit = self.fix_quantity(quantity_on_near_transit)

                    # Дальний транзит (поступление на склад в течение 8-30 дней)
                    quantity_on_far_transit = item.get('InFarTransitCount', None)
                    quantity_on_far_transit, great_than_on_far_transit = self.fix_quantity(quantity_on_far_transit)

                    if quantity_on_msk:
                        can_reserve, is_available_for_order = True, True
                        party = distributors.models.Party.objects.create(distributor=self.distributor,
                                                                         product=product,
                                                                         price_in=price_in,
                                                                         currency_in=currency_in,
                                                                         location=self.stock_on_msk,
                                                                         quantity=quantity_on_msk,
                                                                         quantity_great_than=great_than_on_msk,
                                                                         can_reserve=can_reserve,
                                                                         is_available_for_order=is_available_for_order,
                                                                         unconditional=unconditional,
                                                                         promo=promo)
                        self.count_of_parties += 1

                    if quantity_on_spb:
                        can_reserve, is_available_for_order = True, True
                        party = distributors.models.Party.objects.create(distributor=self.distributor,
                                                                         product=product,
                                                                         price_in=price_in,
                                                                         currency_in=currency_in,
                                                                         location=self.stock_on_spb,
                                                                         quantity=quantity_on_spb,
                                                                         quantity_great_than=great_than_on_spb,
                                                                         can_reserve=can_reserve,
                                                                         is_available_for_order=is_available_for_order,
                                                                         unconditional=unconditional,
                                                                         promo=promo)
                        self.count_of_parties += 1

                    if quantity_on_near_transit:
                        can_reserve, is_available_for_order = True, False
                        party = distributors.models.Party.objects.create(distributor=self.distributor,
                                                                         product=product,
                                                                         price_in=price_in,
                                                                         currency_in=currency_in,
                                                                         location=self.near_transit,
                                                                         quantity=quantity_on_near_transit,
                                                                         quantity_great_than=great_than_on_near_transit,
                                                                         can_reserve=can_reserve,
                                                                         is_available_for_order=is_available_for_order,
                                                                         unconditional=unconditional,
                                                                         promo=promo)
                        self.count_of_parties += 1

                    if quantity_on_far_transit:
                        can_reserve, is_available_for_order = True, False
                        party = distributors.models.Party.objects.create(distributor=self.distributor,
                                                                         product=product,
                                                                         price_in=price_in,
                                                                         currency_in=currency_in,
                                                                         location=self.far_transit,
                                                                         quantity=quantity_on_far_transit,
                                                                         quantity_great_than=great_than_on_far_transit,
                                                                         can_reserve=can_reserve,
                                                                         is_available_for_order=is_available_for_order,
                                                                         unconditional=unconditional,
                                                                         promo=promo)
                        self.count_of_parties += 1

    def get_keys_for_update_content(self, mode='all'):

        keys = []

        # Получаем ключи из базы
        if mode == 'clear':
            keys_ = distributors.models.Product.objects.filter(distributor=self.distributor,
                                                               content__isnull=True).values('part_number')
        else:
            keys_ = distributors.models.Product.objects.filter(distributor=self.distributor).values('part_number')

        # Чистим ключи
        for key_ in keys_:
            keys.append(self.fix_part_number(key_['part_number']))

        return keys

    def update_content(self, keys, mode='all'):

        # Количество продуктов в одном запросе
        if mode in ['all', 'clear']:
            quantity_in_request = 100
        else:
            quantity_in_request = 500

        # Оформляем дату старта
        start = ''
        if mode == 'day':
            start = datetime.utcnow() - timedelta(days=1)
            start = self.datetime_to_str(x=start)

        elif mode == 'week':
            start = datetime.utcnow() - timedelta(days=7)
            start = self.datetime_to_str(x=start)

        elif mode == 'month':
            start = datetime.utcnow() - timedelta(days=31)
            start = self.datetime_to_str(x=start)

        # Готовим обрамление урлов
        url_params_start = f'https://b2b.marvel.ru/Api/GetItems' \
                           f'?user={settings.MARVEL_LOGIN}' \
                           f'&password={settings.MARVEL_PASSWORD}' \
                           f'&packStatus=0' \
                           f'&responseFormat=1' \
                           f'&getExtendedItemInfo=1' \
                           f'{start}' \
                           f'&items=<Root><WareItem>'

        url_images_start = f'https://b2b.marvel.ru/Api/GetItemPhotos' \
                           f'?user={settings.MARVEL_LOGIN}' \
                           f'&password={settings.MARVEL_PASSWORD}' \
                           f'&packStatus=0' \
                           f'&responseFormat=1' \
                           f'{start}' \
                           f'&items=<Root><WareItem>'

        url_end = '</WareItem></Root>'

        # Готовим запросы и выполняем их
        url_ = ''
        for n, key in enumerate(keys):

            print(f'{n+1} of {len(keys)} {key}')
            url_ = f'{url_}<ItemId>{key}</ItemId>'

            # Если счётчик кратен партии или последний
            if n + 1 == len(keys) or (n + 1) % quantity_in_request == 0:

                # Загружаем параметры
                url = f'{url_params_start}{url_}{url_end}'
                data = self.load(url=url, result_type='json', request_type='POST')
                if data['Header']['Code'] == 0:
                    try:
                        self.parse_content(data['Body']['CategoryItem'])
                    except TypeError:
                        pass
                else:
                    print('Ошибка!', data['Header']['Message'])

                # Загружаем изображения
                url = f'{url_images_start}{url_}{url_end}'
                data = self.load(url=url, result_type='json', request_type='POST')
                if data['Header']['Code'] == 0:
                    self.parse_images(data['Body']['Photo'])
                else:
                    print('Ошибка!', data['Header']['Message'])

                # Обнуляем url
                url_ = ''

    def parse_content(self, data):

        for content in data:
            try:
                product = distributors.models.Product.objects.get(distributor=self.distributor,
                                                                  part_number__iexact=content['WareArticle'])
            except distributors.models.Product.DoesNotExist:
                continue

            try:
                parameters = content['ExtendedInfo']['Parameter']
            except KeyError:
                continue

            for parameter in parameters:
                name = parameter.get('ParameterName', None)
                value = parameter.get('ParameterValue', None)

                if name:
                    parameter = distributors.models.Parameter.objects.take(distributor=self.distributor,
                                                                           name=name)
                else:
                    continue

                parameter_value = distributors.models.ParameterValue.objects.take(distributor=self.distributor,
                                                                                  product=product,
                                                                                  parameter=parameter,
                                                                                  value=value,
                                                                                  unit=None)
                print(parameter_value)
                self.count_of_parameters += 1

            product.content_loaded = timezone.now()
            product.content = content
            product.save()

    def parse_images(self, images):

        for image in images:
            product = distributors.models.Product.objects.get(distributor=self.distributor,
                                                              part_number__iexact=image['BigImage']['WareArticle'])

            url = image['BigImage']['URL']
            image = distributors.models.ProductImage.objects.take(product=product, source_url=url)
            print(image)
            self.count_of_images += 1

    @staticmethod
    def fix_quantity(quantity):

        # Насильно превращаем в строку
        quantity = str(quantity)

        if '+' in quantity or '>' in quantity:
            quantity_great_than = True
        else:
            quantity_great_than = False

        if 'много' in quantity:
            quantity = '10'
            quantity_great_than = True

        if '<' in quantity:
            quantity = str(int(quantity) // 2)

        dictionary = {'+': '', '>': '', '*': '', '<': ''}
        for key in dictionary:
            quantity = quantity.replace(key, dictionary[key])

        return int(quantity), quantity_great_than

    @staticmethod
    def fix_part_number(part_number):

        # Насильно превращаем в строку
        part_number = str(part_number)

        dictionary = {'#': '', '@': '', ':': '', '&': '', '?': ''}
        for key in dictionary:
            part_number = part_number.replace(key, dictionary[key])

        return part_number

    @staticmethod
    def datetime_to_str(x):
        x = x.strftime('%d%m%Y')
        x = f'&updatedSince={x}'
        return x
