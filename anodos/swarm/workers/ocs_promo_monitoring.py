from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'ocs.ru/promo'
    login = None
    password = None
    start_url = 'https://www.ocs.ru/Promo'
    base_url = 'https://www.ocs.ru'
    company = 'OCS'

    def __init__(self):
        self.source = Source.objects.take(
            name=self.name,
            login=self.login,
            password=self.password)
        super().__init__()

    def run(self):

        # Заходим на первую страницу
        tree = self.load(url=self.start_url, result_type='html')

        # Получаем все ссылки
        items = tree.xpath('//div[@class="item"]')
        for item in items:
            vendor = item.xpath('.//*[@class="vendor"]//text()')[0]
            term = item.xpath('.//*[@class="term"]//text()')[0]
            title = item.xpath('.//h2//text()')[0]
            text = item.xpath('.//div[@class="info"]/p//text()')[0]
            url = item.xpath('.//h2/a/@href')[0]
            if not url.startswith(self.base_url):
                url = '{}{}'.format(self.base_url, url)

            try:
                SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:
                content = f'<b>Промо-акция {self.company} и {vendor}</b>\n<i>{term}</i>\n\n<a href="{url}">{title}</a>\n{text}\n'
                print(content)
                self.send(content)
                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
