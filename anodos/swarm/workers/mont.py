from django.conf import settings
from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'mont.com'
    login = None
    password = None
    urls = {'base': 'https://www.mont.com',
            'events': 'https://mont.com/ru-ru/events',
            'news': 'https://mont.com/ru-ru/news'}
    company = 'MONT'

    def __init__(self):
        self.source = Source.objects.take(
            name=self.name,
            login=self.login,
            password=self.password)
        self.count_events = 0
        self.count_news = 0
        super().__init__()

    def run(self, command=None):

        if command == 'update_news':
            self.update_events()
            self.update_news()
            self.send(f'{self.source} {command} finish:\n'
                      f'- мероприятий: {self.count_events};\n'
                      f'- новостей: {self.count_news}.')

    def update_events(self):
        # Заходим на первую страницу
        tree = self.load(url=self.urls['events'], result_type='html')

        # Получаем все ссылки
        items = tree.xpath('//div[@class="events-item"]')
        items.reverse()

        for item in items:
            news_type = 'Мероприятие'
            title = item.xpath('.//h3/text()')[0]
            url = item.xpath('.//a/@href')[0]
            term = item.xpath('.//*[@class="events-item__date-container '
                              'events-item__date-container--mobile"]//text()')[1]
            text = item.xpath('.//section[@class="events-item__text"]//text()')[0:2]
            text = ' '.join(text)

            title = self.fix_text(title)
            term = self.fix_text(term)
            text = self.fix_text(text)

            if not url.startswith(self.urls['base']):
                url = '{}{}'.format(self.urls['base'], url)

            try:
                SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:
                content = f'<b>{news_type} {self.company}</b>\n<i>{term}</i>\n\n<a href="{url}">{title}</a>\n{text}\n'
                print(content)
                self.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)
                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
            self.count_events += 1

    def update_news(self):

        # Заходим на первую страницу
        tree = self.load(url=self.urls['news'], result_type='html')

        # Получаем все ссылки

        items = tree.xpath('//div[@class="news-item"]')
        items.reverse()

        for item in items:
            news_type = 'Новость'
            title = item.xpath('.//h3/text()')[0]
            url = item.xpath('.//a/@href')[0]
            term = item.xpath('.//span[@class="news-item__date news-item__date--mobile"]/text()')[0]
            text = item.xpath('.//p/text()')[0]

            title = self.fix_text(title)
            term = self.fix_text(term)
            text = self.fix_text(text)

            if not url.startswith(self.urls['base']):
                url = '{}{}'.format(self.urls['base'], url)

            try:
                SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:
                content = f'<b>{news_type} {self.company}</b>\n<i>{term}</i>\n\n<a href="{url}">{title}</a>\n{text}\n'
                print(content)
                self.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)
                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
            self.count_news += 1
