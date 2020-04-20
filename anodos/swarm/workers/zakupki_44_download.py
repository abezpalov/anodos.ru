from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    host = 'ftp.zakupki.gov.ru'

    def __init__(self):
        self.source = Source.objects.take(
            name='ftp.zakupki.gov.ru',
            login='free',
            password='free')
        super().__init__()

    def run(self):
        print(self.source)

        # Создаём запись о корневой папке в источнике
        SourceData.objects.take(source=self.source, url=None)

        while SourceData.objects.filter(source=self.source, file_name=None):
            data = SourceData.objects.filter(source=self.source, file_name=None)[0]
            print(f'Загружаю каталог: {data}')
            catalog_list = self.get_ftp_catalog(host=self.host, catalog=data.url)
            print(catalog_list)

            for o in catalog_list:
                if data.url:
                    url = '{}/{}'.format(data.url, o)
                else:
                    url = o
                data_ = SourceData.objects.take(source=self.source, url=url)
                print(data_)

            data.delete()