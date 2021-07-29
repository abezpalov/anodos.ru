from swarm.models import *
from django.conf import settings
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'axoft.ru/events'
    login = None
    password = None
    start_url = 'https://axoft.ru/current/events/list/'
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
        items = tree.xpath('//div[@class="b-content_block"]/div')
        items.reverse()

        for item in items:
            news_type = 'Мероприятие'
            try:
                title = item.xpath('.//h3//a/text()')[0]
                url = item.xpath('.//h3//a/@href')[0]
                term = item.xpath('.//*[@class="b-date_big"]/text()')[0]
                text = item.xpath('.//p[@class="b-content_text"]/text()')[0]
            except IndexError:
                continue
            if not url.startswith(self.base_url):
                url = '{}{}'.format(self.base_url, url)

            title = self.fix_text(title)
            term = self.fix_text(term)
            text = self.fix_text(text)

            try:
                SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:
                content = f'<b>{news_type} {self.company}</b>\n<i>{term}</i>\n\n<a href="{url}">{title}</a>\n{text}\n'
                print(content)
                self.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)
                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
