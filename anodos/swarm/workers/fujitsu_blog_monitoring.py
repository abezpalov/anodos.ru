from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'fujitsu.ru/news'
    login = None
    password = None
    start_url = 'https://blog.global.fujitsu.com/fgb/'
    base_url = 'https://blog.global.fujitsu.com'
    company = 'Fujitsu'

    def __init__(self):
        self.source = Source.objects.take(
            name=self.name,
            login=self.login,
            password=self.password)
        super().__init__()

    def run(self):

        # Заходим на первую страницу
        tree = self.load(url=self.start_url, result_type='html')

        # Получаем все элементы
        items = tree.xpath('//ul[@id="recent-article"]/li')
        items.reverse()

        for item in items:
            news_type = 'Блог'
            title = item.xpath('.//*[@class="p-post__title"]/text()')[0]
            term = item.xpath('.//ul[@class="c-post-meta"]/li[2]/text()')[0]
            url = item.xpath('.//a/@href')[0]
            text = item.xpath('.//*[@class="p-post__text"]/text()')[0]
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
