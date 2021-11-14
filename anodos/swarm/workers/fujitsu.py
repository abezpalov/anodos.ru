from django.conf import settings

import anodos.tools
import swarm.models
import swarm.workers.worker


class Worker(swarm.workers.worker.Worker):

    name = 'Fujitsu'
    urls = {'blogs_base': 'https://techcommunity.ts.fujitsu.com',
            'blogs_start': 'https://techcommunity.ts.fujitsu.com/en/blog.html'}

    def __init__(self):
        self.source = swarm.models.Source.objects.take(name=self.name)
        self.count_of_blogs = 0
        self.message = None
        super().__init__()

    def run(self):

        if self.command == 'update_news':
            self.update_blogs()
            self.message = f'- публикаций в блоге: {self.count_of_blogs}.'

        if self.message:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}:\n'
                                      f'{self.message}')
        else:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}.\n')

    def update_blogs(self):

        # Заходим на первую страницу
        tree = self.load(url=self.urls['blogs_start'], result_type='html')

        # Получаем все элементы
        items = tree.xpath('//div[@class="newsplusEntry"]')
        items.reverse()

        for item in items:
            news_type = 'блог'
            title = item.xpath('.//*[@class="newsplusTitle"]//a/text()')[0]
            term = item.xpath('.//*[@class="newsplusTeaser"]/text()')[0]
            url = item.xpath('.//*[@class="newsplusTitle"]//a/@href')[0]
            text = item.xpath('.//*[@class="newsplusTeaser newsplusTeaserText"]/text()')[0]

            if not url.startswith(self.urls['blogs_base']):
                url = f'{self.urls["blogs_base"]}{url}'

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

            self.count_of_blogs += 1
