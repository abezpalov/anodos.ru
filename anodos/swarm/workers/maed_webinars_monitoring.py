from datetime import date
from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'web.maed.ru'
    login = None
    password = None
    start_url = 'https://web.maed.ru/'
    base_url = 'https://web.maed.ru/'
    company = 'MaEd'

    def __init__(self):
        self.source = Source.objects.take(
            name=self.name,
            login=self.login,
            password=self.password)
        super().__init__()

    def run(self):

        # Заходим на первую страницу
        tree = self.load(url=self.start_url, result_type='html')

        youtube_ids = tree.xpath('//div[@class="tn-atom__videoiframe"]/@data-youtubeid')

        for youtube_id in youtube_ids:
            news_type = 'Мероприятие'
            term = date.today()
            url = f'https://youtu.be/{youtube_id}'

            try:
                SourceData.objects.get(source=self.source, url=url)
            except SourceData.DoesNotExist:

                tree = self.load(url=url, result_type='html')
                title = tree.xpath('//title/text()')[0].split(' - ')[0]

                content = f'<b>{news_type} {self.company}</b>\n<i>{term}</i>\n\n<a href="{url}">{title}</a>\n'
                print(content)

                self.send(content)
                data = SourceData.objects.take(source=self.source, url=url)
                data.content = content
                data.save()
