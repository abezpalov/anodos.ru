import os
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

        # До тех пор, пока есть что загружать
        while SourceData.objects.filter(source=self.source, file_name=None):

            # Получаем первый обект данных с источников
            data = SourceData.objects.filter(source=self.source, file_name=None)[0]

            # Пробуем получить содержание каталога
            catalog_list = self.get_ftp_catalog(host=self.host, catalog=data.url)

            # Если получили содержание каталога
            if catalog_list is not None:
                for o in catalog_list:
                    if data.url:
                        url = '{}/{}'.format(data.url, o)
                    else:
                        url = o
                    data_ = SourceData.objects.take(source=self.source, url=url)
                    print(data_)
                data.delete()

            # Наверное это всё-таки файл; пробуем скачать
            else:
                data_ = self.get_file_from_ftp(host=self.host, file_name=data.url)
                data.save_file(data_)


