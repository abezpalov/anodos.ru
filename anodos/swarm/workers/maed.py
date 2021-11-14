from datetime import date

from django.conf import settings

import anodos.tools
import swarm.models
import swarm.workers.worker


class Worker(swarm.workers.worker.Worker):

    name = 'MaEd'
    urls = {'start': 'https://webmaed.ru/'}

    def __init__(self):
        self.source = swarm.models.Source.objects.take(name=self.name)
        self.count_of_webinars = 0
        self.message = None
        super().__init__()

    def run(self):

        if self.command == 'update_webinars':
            self.update_webinars()
            self.message = f'- вебинаров: {self.count_of_webinars}.'

        if self.message:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}:\n'
                                      f'{self.message}')
        else:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}.\n')

    def update_webinars(self):

        # Заходим на первую страницу
        tree = self.load(url=self.urls['start'], result_type='html')

        youtube_ids = tree.xpath('//*/@data-youtubeid')

        for youtube_id in youtube_ids:
            news_type = 'мероприятие'
            term = date.today()
            url = f'https://youtu.be/{youtube_id}'

            try:
                swarm.models.SourceData.objects.get(source=self.source, url=url)
            except swarm.models.SourceData.DoesNotExist:

                tree = self.load(url=url, result_type='html')
                title = tree.xpath('//title/text()')[0]
                title = anodos.tools.fix_text(title)

                content = f'<b><a href="{url}">{title}</a></b>\n' \
                          f'<i>{term}</i>\n\n' \
                          f'#{news_type} #{self.name}'
                print(content)

                anodos.tools.send(content, chat_id=settings.TELEGRAM_NEWS_CHAT, disable_web_page_preview=False)
                data = swarm.models.SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()

            self.count_of_webinars += 1
