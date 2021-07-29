from django.conf import settings
from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'mont.com/news'
    login = None
    password = None
    start_url = 'https://mont.com/ru-ru/news'
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

            if not url.startswith(self.base_url):
                url = '{}{}'.format(self.base_url, url)

            try:
                SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:
                content = f'<b>{news_type} {self.company}</b>\n<i>{term}</i>\n\n<a href="{url}">{title}</a>\n{text}\n'
                print(content)
                self.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)
                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
