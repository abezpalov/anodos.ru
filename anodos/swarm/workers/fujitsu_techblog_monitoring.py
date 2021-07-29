from django.conf import settings
from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'fujitsu.ru/techblog'
    login = None
    password = None
    start_url = 'https://techcommunity.ts.fujitsu.com/en/blog.html'
    base_url = 'https://techcommunity.ts.fujitsu.com'
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
        items = tree.xpath('//div[@class="newsplusEntry"]')
        items.reverse()

        for item in items:
            news_type = 'Технический блог'
            title = item.xpath('.//*[@class="newsplusTitle"]//a/text()')[0]
            term = item.xpath('.//*[@class="newsplusTeaser"]/text()')[0]
            url = item.xpath('.//*[@class="newsplusTitle"]//a/@href')[0]
            text = item.xpath('.//*[@class="newsplusTeaser newsplusTeaserText"]/text()')[0]
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
