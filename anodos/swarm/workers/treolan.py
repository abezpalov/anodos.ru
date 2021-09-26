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

        self.count_products = 0
        self.count_parties = 0
        self.count_news = 0

        self.client = None

        super().__init__()

    def run(self, command=None):

        self.send(f'Treolan run {command}')

        if command == 'update_news':
            self.update_news()
            self.send(f'Обновил публикации {self.distributor}.\n'
                      f'{self.count_news} новостей.')

        elif command == 'update_stocks':

            # Инициализируем SOAP-клиента
            settings_ = zeep.Settings(strict=False, xml_huge_tree=True)
            self.client = zeep.Client(wsdl=self.url['wsdl'], settings=settings_)

            # self.update_categories()
            self.update_catalog()

            # Удаляем устаревшие партии
            Party.objects.filter(distributor=self.distributor,
                                 created__lte=self.start_time).delete()

        elif command == 'update_content_all':
            pass

        elif command == 'test':
            pass

        elif command == 'all_delete':
            self.distributor.delete()

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
                content = f'<b>{content_type} {self.distributor}</b>\n' \
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
        print(result['Result'])
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

    def parse_catalog(self, tree):
        print(tree)
        categories = tree.xpath('.//category')
        for category_element in categories:
            key = category_element.xpath('./@id')[0]
            name = category_element.xpath('./@name')[0]
            category = Category.objects.get_by_key(distributor=self.distributor, key=key)
            print(key, name, category)
            products = category_element.xpath('./position')
            for product_element in products:

                # @id - Идентификатор позиции
                product_key = product_element.xpath('./@id')[0]
                print('product_key', product_key)

                # @prid - Внутренний идентификатор позиции.
                party_key = product_element.xpath('./@prid')[0]
                print('party_key', party_key)

                # @articul - Артикул.
                part_number = product_element.xpath('./@articul')[0]
                print('part_number', part_number)

                # @name - Наименование.
                name = product_element.xpath('./@name')[0]
                print('name', name)

                # @rusDescr - Русское описание.
                description = product_element.xpath('./@rusDescr')[0]
                print('description', description)

                # @vendor - Производитель.
                vendor = product_element.xpath('./@vendor')[0]
                print('vendor', vendor)

                # @vendor-id - Идентификатор производителя.
                vendor_id = product_element.xpath('./@vendor-id')[0]
                print('vendor_id', vendor_id)

                # @gp - Срок гарантийного обслуживания.
                try:
                    gp = product_element.xpath('./@gp')[0]
                except IndexError:
                    gp = None
                print('gp', gp)

                # @price - Цена.
                price = product_element.xpath('./@price')[0]
                print('price', price)

                # @dprice - Цена c учетом скидки.
                dprice = product_element.xpath('./@dprice')[0]
                print('dprice', dprice)

                # @currency - Валюта, в которой указана стоимость товара.
                # Значением является международный код валюты из трёх латинских символов(RUB, USD и тд.).
                currency = product_element.xpath('./@currency')[0]
                print('currency', currency)

                # @discount - Размер скидки.
                try:
                    discount = product_element.xpath('./@discount')[0]
                except IndexError:
                    discount = None
                print('discount', discount)

                # @outoftrade - Не закупается на склад (X - снимается).
                outoftrade = product_element.xpath('./@outoftrade')[0]
                print('outoftrade', outoftrade)

                # @uchmark - Участие в маркетинговых программах(0 – не участвует, 2 – участвует).
                uchmark = product_element.xpath('./@uchmark')[0]
                print('uchmark', uchmark)

                # @sale - Участие в распродажах некондиции(0 – не участвует, 1 – участвует).
                sale = product_element.xpath('./@sale')[0]
                print('sale', sale)

                # @freenom - Свободно на складе.
                freenom = product_element.xpath('./@freenom')[0]
                print('freenom', freenom)

                # @freeptrans - Свободнов транзите.
                freeptrans = product_element.xpath('./@freeptrans')[0]
                print('freeptrans', freeptrans)

                # @ntdate - Дата ближайшего транзита.
                ntdate = product_element.xpath('./@ntdate')[0]
                print('ntdate', ntdate)

                # @ntstatus - Статус ближайшего транзита.
                ntstatus = product_element.xpath('./@ntstatus')[0]
                print('ntstatus', ntstatus)

                # @width - Ширина, см.
                width = product_element.xpath('./@width')[0]
                print('width', width)

                # @length - Длина, см.
                length = product_element.xpath('./@length')[0]
                print('length', length)

                # @height - Высота, см.
                height = product_element.xpath('./@height')[0]
                print('height', height)

                # @brutto - Вес в упаковке, кг.
                brutto = product_element.xpath('./@brutto')[0]
                print('brutto', brutto)

                # @GTIN - Код GTIN (используется Dictionary.Ean).
                GTIN = product_element.xpath('./@GTIN')[0]
                print('GTIN', GTIN)


                print()
                print()
                print()


    @staticmethod
    def datetime_to_str(x):
        x = str(x)
        x = x.split('.')[0]
        x = x.replace(' ', 'T')
        x = f'{x}.000000%2B00%3A00'
        return x
