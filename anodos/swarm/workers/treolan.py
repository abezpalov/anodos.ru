import time
import requests as r
import lxml
import urllib.parse
from datetime import datetime, timedelta
import zeep

from django.utils import timezone
from django.conf import settings
from swarm.models import *
from distributors.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    source_name = 'treolan.ru'
    name = 'Treolan'
    login = settings.TREOLAN_LOGIN
    password = settings.TREOLAN_PASSWORD
    url = {'wsdl': 'https://api.treolan.ru/ws/service.asmx?wsdl',
           'base': 'https://www.treolan.ru',
           }
    content_urls = {'Новость вендора': 'https://www.treolan.ru/vendor/news',
                    'Промо': 'https://www.treolan.ru/vendor/marketing',
                    'Новое поступление': 'https://www.treolan.ru/new_arrival',
                    'Новость': 'https://www.treolan.ru/company/news',
                    }

    def __init__(self):
        self.start_time = timezone.now()
        self.host = settings.HOST

        self.source = Source.objects.take(
            name=self.source_name,
            login=self.login,
            password=self.password)
        self.distributor = Distributor.objects.take(name=self.name)

        self.stock = Location.objects.take(distributor=self.distributor,
                                           key='Склад')
        self.transit = Location.objects.take(distributor=self.distributor,
                                             key='Транзит')

        self.count_products = 0
        self.count_parties = 0
        self.count_news = 0

        self.client = None

        self.test = set()

        super().__init__()

    def run(self, command=None):

        self.send(f'{self.distributor}: {command} start')

        if command == 'update_news':
            self.update_news()
            self.send(f'{self.distributor} {command} finish:'
                      f'- новостей: {self.count_news}.')

        elif command == 'update_stocks':

            # Инициализируем SOAP-клиента
            settings_ = zeep.Settings(strict=False, xml_huge_tree=True)
            self.client = zeep.Client(wsdl=self.url['wsdl'], settings=settings_)

            # self.update_categories()
            self.update_catalog()

            # Удаляем устаревшие партии
            Party.objects.filter(distributor=self.distributor,
                                 created__lte=self.start_time).delete()

            # Отправляем оповещение об успешном завершении
            self.send(f'{self.distributor} {command} finish:\n'
                      f'- продуктов: {self.count_products};\n'
                      f'- партий: {self.count_parties}.')

            print(self.test)

        elif command == 'update_content_all':

            # Инициализируем SOAP-клиента
            settings_ = zeep.Settings(strict=False, xml_huge_tree=True)
            self.client = zeep.Client(wsdl=self.url['wsdl'], settings=settings_)

            # Получаем ключи продуктов для запросов
            keys = self.get_keys_for_update_content('all')
            self.update_content(keys)

        elif command == 'update_content_clear':

            # Инициализируем SOAP-клиента
            settings_ = zeep.Settings(strict=False, xml_huge_tree=True)
            self.client = zeep.Client(wsdl=self.url['wsdl'], settings=settings_)

            # Получаем ключи продуктов для запросов
            keys = self.get_keys_for_update_content('clear')
            self.update_content(keys)

        elif command == 'test':
            pass

        elif command == 'all_delete':
            self.distributor.delete()

        else:
            print('Неизвестная команда!')

    def update_news(self):

        for idx in self.content_urls:
            content_type = idx
            url = self.content_urls[idx]
            tree = self.load(url=url, result_type='html')
            self.parse_news(tree=tree, content_type=content_type)

    def parse_news(self, tree, content_type):

        items = tree.xpath('.//div[@class="news-preview col-3"]')
        for item in items:
            # title
            title = item.xpath('.//*[@class="news-preview__title"]/a/text()')[0]
            title = self.fix_text(title)

            # url
            url = item.xpath('.//*[@class="news-preview__title"]/a/@href')[0]

            # date
            date = item.xpath('.//*[@class="news-preview__date"]/text()')[0]
            date = self.fix_text(date)

            # description
            try:
                description = item.xpath('.//*[@class="news-preview__description"]/a/text()')[0]
            except IndexError:
                description = ''
            description = self.fix_text(description)

            try:
                data = SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:
                content = f'<b>{self.distributor}: {content_type}</b>\n' \
                          f'<i>{date}</i>\n' \
                          f'<a href="{url}">{title}</a>\n' \
                        f'{description}'
                self.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)

                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
            print(data)
            self.count_news += 1

    def update_categories(self):
        result = self.client.service.GetCategories(login=self.login,
                                                   password=self.password)
        tree = lxml.etree.fromstring(result['Result'])
        self.parse_categories(tree)

    def parse_categories(self, tree):
        categories = tree.xpath('.//category')
        for element in categories:
            category = self.parse_category(element)
            print(category)

    def parse_category(self, element):
        key = element.xpath('.//@id')[0]
        parent_key = element.xpath('.//@parentid')[0]
        try:
            parent = Category.objects.get(distributor=self.distributor, key=parent_key)
        except Category.DoesNotExist:
            parent = None
        name = element.xpath('.//@name')[0]
        name = self.fix_text(name)
        category = Category.objects.take(distributor=self.distributor,
                                         key=key,
                                         name=name,
                                         parent=parent)
        return category

    def update_catalog(self):
        result = self.client.service.GenCatalogV2(login=self.login,
                                                  password=self.password,
                                                  category='',
                                                  vendorid=0,
                                                  keywords='',
                                                  criterion=0,
                                                  inArticul=0,
                                                  inName=0,
                                                  inMark=0,
                                                  showNc=0)
        tree = lxml.etree.fromstring(result['Result'])
        self.parse_catalog(tree)

    def parse_catalog(self, tree, parent=None):

        # Проходим по всем категориям
        categories = tree.xpath('./category')
        for category_ in categories:
            key = category_.xpath('./@id')[0]
            key = self.fix_text(key)
            name = category_.xpath('./@name')[0]
            name = self.fix_text(name)
            category = Category.objects.take(distributor=self.distributor,
                                             key=key,
                                             name=name,
                                             parent=parent)
            print(category)
            self.parse_catalog(tree=category_, parent=category)

            products = category_.xpath('./position')

            # Проходим по всем продуктам
            for item in products:

                # @id - Идентификатор позиции
                product_key = item.xpath('./@id')[0]

                # @prid - Внутренний идентификатор позиции.
                party_key = item.xpath('./@prid')[0]

                # @articul - Артикул.
                part_number = item.xpath('./@articul')[0]

                # @name - Наименование.
                name = item.xpath('./@name')[0]

                # @rusDescr - Русское описание.
                description = item.xpath('./@rusDescr')[0]

                # @vendor - Производитель.
                vendor = item.xpath('./@vendor')[0]
                vendor = self.fix_text(vendor)
                vendor = Vendor.objects.take(distributor=self.distributor, name=vendor)

                # @vendor-id - Идентификатор производителя.
                vendor_id = item.xpath('./@vendor-id')[0]

                # @gp - Срок гарантийного обслуживания.
                try:
                    warranty = item.xpath('./@gp')[0]
                except IndexError:
                    warranty = None

                # @price - Цена.
                price_out = item.xpath('./@price')[0]

                # @dprice - Цена c учетом скидки.
                price_in = item.xpath('./@dprice')[0]

                # @currency - Валюта, в которой указана стоимость товара.
                # Значением является международный код валюты из трёх латинских символов(RUB, USD и тд.).
                currency = item.xpath('./@currency')[0]
                currency = Currency.objects.take(key=currency)

                # @discount - Размер скидки.
                try:
                    discount = item.xpath('./@discount')[0]
                except IndexError:
                    discount = None

                # @outoftrade - Не закупается на склад (X - снимается).
                outoftrade = item.xpath('./@outoftrade')[0]
                if outoftrade == 'X':
                    outoftrade = True
                else:
                    outoftrade = False

                # @uchmark - Участие в маркетинговых программах(0 – не участвует, 2 – участвует).
                promo = item.xpath('./@uchmark')[0]
                if promo == '2':
                    promo = True
                else:
                    promo = False

                # @sale - Участие в распродажах некондиции(0 – не участвует, 1 – участвует).
                sale = item.xpath('./@sale')[0]

                # @freenom - Свободно на складе.
                quantity_on_stock = item.xpath('./@freenom')[0]
                self.test.add(quantity_on_stock)

                # @freeptrans - Свободнов транзите.
                quantity_on_transit = item.xpath('./@freeptrans')[0]
                self.test.add(quantity_on_transit)

                # @ntdate - Дата ближайшего транзита.
                incoming_date = item.xpath('./@ntdate')[0]

                # @ntstatus - Статус ближайшего транзита.
                ntstatus = item.xpath('./@ntstatus')[0]

                # @width - Ширина, см.
                depth = item.xpath('./@width')[0]
                depth = float(depth) / 100.0

                # @length - Длина, см.
                width = item.xpath('./@length')[0]
                width = float(width) / 100.0

                # @height - Высота, см.
                height = item.xpath('./@height')[0]
                height = float(height) / 100.0

                # @brutto - Вес в упаковке, кг.
                weight = item.xpath('./@brutto')[0]

                # @GTIN - Код GTIN (используется Dictionary.Ean).
                gtin = item.xpath('./@GTIN')[0]

                # @isTraceable - Признак прослеживаемости (0 – нет, 1 – да).
                traceable = item.xpath('./@codeTNVED')[0]
                if traceable == '1':
                    traceable = True
                else:
                    traceable = False

                #@codeTNVED- код ТН ВЭД
                tnved = item.xpath('./@codeTNVED')[0]

                product = Product.objects.take_by_party_key(distributor=self.distributor,
                                                            product_key=product_key,
                                                            party_key=party_key,
                                                            part_number=part_number,
                                                            vendor=vendor,
                                                            category=category,
                                                            name=name,
                                                            description=description,
                                                            warranty=warranty,
                                                            gtin=gtin,
                                                            tnved=tnved,
                                                            traceable=traceable,
                                                            unconditional=sale,
                                                            sale=sale,
                                                            promo=promo,
                                                            outoftrade=outoftrade,
                                                            weight=weight,
                                                            width=width,
                                                            height=height,
                                                            depth=depth,
                                                            volume=width*height*depth)

                if product is not None:
                    self.count_products += 1
                    print(product)

                    # Чистим количество
                    quantity_on_stock, great_than_on_stock = self.fix_quantity(quantity=quantity_on_stock)
                    quantity_on_transit, great_than_on_transit = self.fix_quantity(quantity=quantity_on_transit)

                    if quantity_on_stock or (not quantity_on_stock and not quantity_on_transit):
                        if quantity_on_stock > 0:
                            can_reserve, is_available_for_order = True, True
                        else:
                            can_reserve, is_available_for_order = False, False
                        party = Party.objects.create(distributor=self.distributor,
                                                     product=product,
                                                     price_in=price_in,
                                                     currency_in=currency,
                                                     price_out=price_out,
                                                     currency_out=currency,
                                                     location=self.stock,
                                                     quantity=quantity_on_stock,
                                                     quantity_great_than=great_than_on_stock,
                                                     can_reserve=can_reserve,
                                                     is_available_for_order=is_available_for_order)
                        self.count_parties += 1
                        print(party)

                    if quantity_on_transit:
                        if quantity_on_transit > 0:
                            can_reserve, is_available_for_order = True, True
                        else:
                            can_reserve, is_available_for_order = False, False
                        party = Party.objects.create(distributor=self.distributor,
                                                     product=product,
                                                     price_in=price_in,
                                                     currency_in=currency,
                                                     price_out=price_out,
                                                     currency_out=currency,
                                                     location=self.transit,
                                                     quantity=quantity_on_transit,
                                                     quantity_great_than=great_than_on_transit,
                                                     can_reserve=can_reserve,
                                                     is_available_for_order=is_available_for_order)
                        self.count_parties += 1
                        print(party)

    def get_keys_for_update_content(self, mode=None):

        if mode == 'all':
            keys_ = Product.objects.filter(distributor=self.distributor).values('part_number')
            keys = []
            for key_ in keys_:
                keys.append(key_['part_number'])
            return keys

        elif mode == 'clear':
            keys_ = Product.objects.filter(distributor=self.distributor,
                                           content_loaded__isnull=True).values('part_number')
            keys = []
            for key_ in keys_:
                keys.append(key_['part_number'])
            return keys

    def update_content(self, keys):

        for key in keys:
            result = self.client.service.ProductInfoV2(Login=self.login,
                                                       password=self.password,
                                                       Articul=key)
            tree = lxml.etree.fromstring(result['Result'])
            self.parse_content(tree=tree)

    def parse_content(self, tree):

        # Получаем экземпляр продукта
        product_elements = tree.xpath('.//Product')
        product_element = product_elements[0]
        part_number = product_element.xpath('./@Articul')[0]
        product = Product.objects.get(distributor=self.distributor, part_number=part_number)
        print(product)

        # Проходим по всем характеристикам
        property_elements = product_element.xpath('.//Property')
        for property_element in property_elements:
            parameter_name = property_element.xpath('./@Name')[0]
            parameter_name = self.fix_text(parameter_name)
            parameter = Parameter.objects.take(distributor=self.distributor, name=parameter_name)
            value = property_element.xpath('./@Value')[0]
            value = self.fix_text(value)
            parameter_value = ParameterValue.objects.take(distributor=self.distributor,
                                                          product=product,
                                                          parameter=parameter,
                                                          value=value)
            print(parameter_value)

        # Проходим по всех изображениям
        image_elements = tree.xpath('.//PictureLink/row')
        for image_element in image_elements:
            url = image_element.xpath('./@Link')[0]
            ext = image_element.xpath('./@ImageType')[0].lower()
            image = ProductImage.objects.take(product=product, source_url=url, ext=ext)
            print(image)

        product.content_loaded = timezone.now()
        product.save()

        url = f'{self.host}/distributors/product/{product.id}/'
        self.send(f'<b>Content loaded</b>\n'
                  f'<a href="{url}">{product}</a>')

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
            quantity = quantity.replace('<', '')
            quantity = str(int(int(quantity) / 2))

        quantity = quantity.replace('+', '')

        dictionary = {'+': '', '>': '', '*': ''}
        for key in dictionary:
            quantity = quantity.replace(key, dictionary[key])

        return int(quantity), quantity_great_than
