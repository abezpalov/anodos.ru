import time
import random
import urllib.parse
import lxml.etree

from django.utils import timezone
from django.conf import settings

import anodos.tools
import swarm.models
import distributors.models
import swarm.workers.worker


class Worker(swarm.workers.worker.Worker):

    source_name = 'se.com'
    name = 'Schneder Electric'
    url = {'base': 'https://www.se.com',
           'product_sitemaps': 'https://www.se.com/ru/ru/product/google-product-sitemapindex-RU-ru.xml',
           }

    def __init__(self):
        self.start_time = timezone.now()
        self.source = swarm.models.Source.objects.take(name=self.source_name)
        self.distributor = distributors.models.Distributor.objects.take(name=self.name)
        self.vendor = distributors.models.Vendor.objects.take(distributor=self.distributor,
                                                              name=self.name)

        self.sitemap_urls = set()
        self.product_urls = set()

        self.count_of_products = 0
        self.count_of_parameters = 0
        self.count_of_images = 0

        super().__init__()

    def run(self):

        if self.command == 'update_content_all':
            self.update_content()

            # Отправляем оповещение об успешном завершении
            self.message = f'- продуктов: {self.count_of_products};\n' \
                           f'- характеристик: {self.count_of_parameters};\n' \
                           f'- фотографий: {self.count_of_images}.'

        if self.message:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}:\n'
                                      f'{self.message}')
        else:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}.\n')

    def update_news(self):
        pass

    def update_content(self):

        self.get_sitemap_urls()
        self.get_product_urls()

        for n, product_url in enumerate(self.product_urls):
            print(f'{n+1} of {len(self.product_urls)} {product_url}')
            self.update_product_and_content(product_url)

    def get_sitemap_urls(self):

        print(self.url['product_sitemaps'])
        tree = self.load(url=self.url['product_sitemaps'], result_type='xml')

        for n, sitemap_url in enumerate(tree.xpath('//loc/text()')):
            sitemap_url = anodos.tools.fix_url(sitemap_url)
            if sitemap_url:
                self.sitemap_urls.add(sitemap_url)

    def get_product_urls(self):

        for n, sitemap_url in enumerate(self.sitemap_urls):
            print(f'{n+1} of {len(self.sitemap_urls)} {sitemap_url}')
            tree = self.load(url=sitemap_url, result_type='xml')
            for product_url in tree.xpath('//loc/text()'):
                product_url = anodos.tools.fix_url(product_url)
                if product_url:
                    self.product_urls.add(product_url)

    def update_product_and_content(self, product_url):

        # Загружаем данные
        tree = self.load(url=product_url, result_type='html')

        # part_number, name
        try:
            part_number = tree.xpath(".//h2/text()")[0]
            name = tree.xpath(".//h1/text()")[0]
        except IndexError:
            return None

        # category
        parent = None
        category = None
        category_elements = tree.xpath('.//se-breadcrumb-item')[2:-1]
        for category_element in category_elements:
            category_name = category_element.xpath('.//span/text()')
            category_name = ''.join(category_name)
            category_name = anodos.tools.fix_text(category_name)
            category = distributors.models.Category.objects.take(distributor=self.distributor,
                                                                 key=category_name,
                                                                 name=category_name,
                                                                 parent=parent)
            parent = category

        # ean_128
        ean_128 = None
        for text in tree.xpath(".//*/text()"):
            if text.startswith('Код EAN'):
                text = anodos.tools.fix_text(text)
                ean_128 = text[text.rindex(' ')+1:]
                break

        # Из характеристик
        weight = None
        width = None
        height = None
        depth = None
        volume = None
        warranty = None
        characteristics = tree.xpath(".//tr[@class='specifications-table__row']")
        for characteristic in characteristics:

            try:
                characteristic_name = characteristic.xpath('.//th/text()')[0]
                characteristic_value = characteristic.xpath('.//td/span/text()')[0]
            except IndexError:
                continue

            if characteristic_name == 'Вес упаковки':
                weight = characteristic_value
                weight = self.fix_logistic_value(weight)

            elif characteristic_name == 'Высота упаковки 1':
                height = characteristic_value
                height = self.fix_logistic_value(height)

            elif characteristic_name == 'Ширина упаковки 1':
                width = characteristic_value
                width = self.fix_logistic_value(width)

            elif characteristic_name == 'Длина упаковки 1':
                depth = characteristic_value
                depth = self.fix_logistic_value(depth)

            elif characteristic_name == 'Гарантия':
                warranty = anodos.tools.fix_text(characteristic_value)

            if width and height and depth:
                volume = width * height * depth

        product = distributors.models.Product.objects.take_by_part_number(distributor=self.distributor,
                                                                          name=name,
                                                                          vendor=self.vendor,
                                                                          category=category,
                                                                          part_number=part_number,
                                                                          description=None,
                                                                          ean_128=ean_128,
                                                                          weight=weight,
                                                                          width=width,
                                                                          height=height,
                                                                          depth=depth,
                                                                          volume=volume,
                                                                          warranty=warranty)
        print(product)
        self.count_of_products += 1

        # Характеристики
        characteristics = tree.xpath(".//tr[@class='specifications-table__row']")
        for characteristic in characteristics:
            name = characteristic.xpath('.//th/text()')[0]

            # Пропускаем параметры продукта
            if name in ['Вес упаковки',  'Гарантия',
                        'Высота упаковки 1', 'Ширина упаковки 1', 'Длина упаковки 1', 'Длина упаковки 1',
                        'Высота упаковки 2', 'Ширина упаковки 2', 'Длина упаковки 2', 'Длина упаковки 2',
                        'Высота упаковки 3', 'Ширина упаковки 3', 'Длина упаковки 3', 'Длина упаковки 3']:
                continue

            value_elements = characteristic.xpath('.//td/*')
            values = []
            for value_element in value_elements:

                text = None
                url = None

                if value_element.tag in ['span', 'div']:
                    text = value_element.text
                    text = anodos.tools.fix_text(text)
                    if text:
                        values.append(f'<span>{text}</span>')

                value = '; '.join(values)

                if name and value:
                    parameter = distributors.models.Parameter.objects.take(distributor=self.distributor,
                                                                           name=name)
                    parameter_value = distributors.models.ParameterValue.objects.take(distributor=self.distributor,
                                                                                      product=product,
                                                                                      parameter=parameter,
                                                                                      value=value)
                print(parameter_value)
                self.count_of_parameters += 1

        # Изображения
        images_ = tree.xpath('.//@src')
        # src = "https://download.schneider-electric.com/files?p_Doc_Ref=C63W32M500-image&p_File_Type=rendition_520_jpg"
        # src = "https://download.schneider-electric.com/files?p_Doc_Ref=C63W32M500-image&p_File_Type=rendition_1500_jpg"

        for url in images_:

            if url.endswith('rendition_520_jpg'):
                url.replace('rendition_520_jpg', 'rendition_1500_jpg')
                image = distributors.models.ProductImage.objects.take(product=product, source_url=url)
                print(image)
                self.count_of_images += 1

    @staticmethod
    def fix_logistic_value(text):

        text = str(text)

        value = text.split(' ')

        if len(value) != 2:
            print(f'Не опознана единица измерения [{text}]')
            exit()

        value[0] = value[0].replace(',', '.')

        if value[1] == 'г':
            result = float(value[0]) / 1000
        elif value[1] == 'кг':
            result = float(value[0])
        elif value[1] == 'мм':
            result = float(value[0]) / 1000
        elif value[1] == 'см':
            result = float(value[0]) / 100
        elif value[1] == 'дм³':
            result = float(value[0]) / 10
        else:
            print(f'Не опознана единица измерения [{text}]')
            exit()


        return result
