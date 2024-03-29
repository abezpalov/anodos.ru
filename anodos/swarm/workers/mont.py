from django.conf import settings

import anodos.tools
import swarm.models
import swarm.workers.worker


class Worker(swarm.workers.worker.Worker):

    name = 'MONT'
    urls = {'base': 'https://www.mont.com',
            'events': 'https://mont.com/ru-ru/events',
            'news': 'https://mont.com/ru-ru/news'}

    def __init__(self):
        self.source = swarm.models.Source.objects.take(name=self.name)
        self.count_of_news = 0
        self.count_of_events = 0
        self.message = None
        super().__init__()

    def run(self):

        if self.command == 'update_news':
            self.update_news()
            self.update_events()
            self.message = f'- новостей: {self.count_of_news};\n' \
                           f'- событий: {self.count_of_events}.'

        if self.message:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}:\n'
                                      f'{self.message}')
        else:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}.\n')

    def update_news(self):

        # Заходим на первую страницу
        tree = self.load(url=self.urls['news'], result_type='html')

        # Получаем все элементы
        items = tree.xpath('//div[@class="news-item"]')
        items.reverse()

        for item in items:
            news_type = 'новость'
            try:
                title = item.xpath('.//h3/text()')[0]
                url = item.xpath('.//a/@href')[0]
                term = item.xpath('.//span[@class="news-item__date news-item__date--mobile"]/text()')[0]
                text = item.xpath('.//p/text()')[0]
            except IndexError:
                continue

            if not url.startswith(self.urls['base']):
                url = f'{self.urls["base"]}{url}'

            title = anodos.tools.fix_text(title)
            term = anodos.tools.fix_text(term)
            text = anodos.tools.fix_text(text)

            try:
                swarm.models.SourceData.objects.get(source=self.source, url=url)
            except swarm.models.SourceData.DoesNotExist:
                content = f'<b><a href="{url}">{title}</a></b>\n' \
                          f'<i>{term}</i>\n\n' \
                          f'{text}\n' \
                          f'#{news_type} #{self.name}'
                print(content)
                anodos.tools.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)
                data = swarm.models.SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()

            self.count_of_news += 1

    def update_events(self):

        # Заходим на первую страницу
        tree = self.load(url=self.urls['events'], result_type='html')

        # Получаем все ссылки
        items = tree.xpath('//div[@class="events-item"]')
        items.reverse()

        for item in items:
            news_type = 'мероприятие'
            try:
                title = item.xpath('.//h3/text()')[0]
                url = item.xpath('.//a/@href')[0]
                term = item.xpath('.//*[@class="events-item__date-container '
                                  'events-item__date-container--mobile"]//text()')[1]
                text = item.xpath('.//section[@class="events-item__text"]//text()')[0:2]
                text = ' '.join(text)
            except IndexError:
                continue
            if not url.startswith(self.urls['base']):
                url = f'{self.urls["base"]}{url}'

            title = anodos.tools.fix_text(title)
            term = anodos.tools.fix_text(term)
            text = anodos.tools.fix_text(text)

            try:
                swarm.models.SourceData.objects.get(source=self.source, url=url)
            except swarm.models.SourceData.DoesNotExist:
                content = f'<b><a href="{url}">{title}</a></b>\n' \
                          f'<i>{term}</i>\n\n' \
                          f'{text}\n' \
                          f'#{news_type} #{self.name}'
                print(content)
                anodos.tools.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT)
                data = swarm.models.SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()

            self.count_of_events += 1
