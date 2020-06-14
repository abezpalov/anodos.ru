from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'arxiv.org/cv'
    login = None
    password = None
    start_url = 'https://arxiv.org/list/cs.CV/recent'
    base_url = 'https://arxiv.org'
    company = 'Cornell Univercity'

    def __init__(self):
        self.source = Source.objects.take(
            name=self.name,
            login=self.login,
            password=self.password)
        super().__init__()

    def run(self):

        # Заходим на первую страницу
        tree = self.load(url=self.start_url, result_type='html')
        exit()

        # Получаем все ссылки
        items = tree.xpath('//div[@class="item"]')

        for item in items:
            date = item.xpath('.//*[@class="date"]/strong/text()')[0]
            location = item.xpath('.//*[@class="date"]/span/text()')[0]
            title = item.xpath('.//h2/a/text()')[0]
            url = item.xpath('.//h2/a/@href')[0]
            try:
                text = item.xpath('.//div[@class="info"]/p//text()')[0]
            except IndexError:
                text = ''

            if not url.startswith(self.base_url):
                url = '{}{}'.format(self.base_url, url)

            try:
                SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:
                content = f'<b>Мероприятие {self.company}</b>\n<i>{date} {location}</i>\n\n<a href="{url}">{title}</a>\n{text}\n'
                print(content)
                self.send(content)
                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
