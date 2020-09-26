from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'axoft.ru/news'
    login = None
    password = None
    start_url = 'https://axoft.ru/current/news/'
    base_url = 'https://axoft.ru'
    company = 'Axoft'

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
        items = tree.xpath('//div[@class="b-news_block"]//div[@class="b-text_block"]')
        items.reverse()

        for item in items:
            news_type = 'Новость'
            try:
                title = item.xpath('.//h3//a/text()')[0]
                url = item.xpath('.//h3//a/@href')[0]
                term = item.xpath('.//*[@class="b-date"]/text()')[0]
                text = item.xpath('.//*[@class="b-content_text"]//p/text()')[0]
            except IndexError:
                continue
            if not url.startswith(self.base_url):
                url = '{}{}'.format(self.base_url, url)

            try:
                SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:
                content = f'<b>{news_type} {self.company}</b>\n<i>{term}</i>\n\n<a href="{url}">{title}</a>\n{text}\n'
                print(content)
                self.send(content)
                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
