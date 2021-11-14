import time
import random
import urllib.parse

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

        self.count_products = 0

        super().__init__()

    def run(self, command=None):

        if command == 'update_content_all':
            self.update_content()

    def update_news(self):
        pass

    def update_content(self):

        self.get_sitemap_urls()
        self.get_product_urls()

        for n, product_url in enumerate(self.product_urls):
            print(f'{n+1} of {len(self.product_urls)} {product_url}')
            self.update_product(product_url)

    def get_sitemap_urls(self):

        print(self.url['product_sitemaps'])
        tree = self.load(url=self.url['product_sitemaps'], result_type='html')

        for n, sitemap_url in enumerate(tree.xpath('//loc/text()')):

            #TODO DEL
            if n > 5:
                return None

            sitemap_url = anodos.tools.fix_url(sitemap_url)
            self.sitemap_urls.add(sitemap_url)

    def get_product_urls(self):

        for sitemap_url in self.sitemap_urls:
            print(sitemap_url)
            tree = self.load(url=sitemap_url, result_type='html')
            for n, product_url in enumerate(tree.xpath('//loc/text()')):

                #TODO DEL
                if n > 2:
                    return None

                self.product_urls.add(product_url)


    def update_product(self, product_url):

        print(product_url)
        tree = self.load(url=product_url, result_type='html')

        characteristics = tree.xpath(".//*[@id='characteristics']//tbody/tr")
        for characteristic in characteristics:
            name = characteristic.xpath('.//th/text()')[0]
            value_elements = characteristic.xpath('.//td//*')
            values = []
            for value_element in value_elements:
                




                value = anodos.tools.fix_text(value)
                if value:
                    values.append(value)

            print(name, '=', values)

        #print(characteristics)


