from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'mont.com/events'
    login = None
    password = None
    start_url = 'https://mont.com/ru-ru/events'
    base_url = 'https://www.mont.com'
    company = 'MONT'

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

        items = tree.xpath('//div[@class="events-item"]')
        items.reverse()

        for item in items:
            news_type = 'Мероприятие'
            title = item.xpath('.//h3/text()')[0]
            url = item.xpath('.//a/@href')[0]
            term = item.xpath('.//*[@class="events-item__date-container events-item__date-container--mobile"]//text()')[1]
            text = item.xpath('.//section[@class="events-item__text"]//text()')[0:2]
            text = ' '.join(text)

            title = self.fix_text(title)
            term = self.fix_text(term)
            text = self.fix_text(text)

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
