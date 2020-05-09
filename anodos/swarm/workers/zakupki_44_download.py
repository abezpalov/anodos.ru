import os
from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    host = 'ftp.zakupki.gov.ru'
    start_url = None
    name = 'ftp.zakupki.gov.ru'
    login = 'free'
    password = 'free'

    def __init__(self):
        self.source = Source.objects.take(
            name=self.name,
            login=self.login,
            password=self.password)
        super().__init__()

    def run(self):

        # Создаём запись о корневой папке в источнике
        SourceData.objects.take(source=self.source, url=self.start_url)

        # До тех пор, пока есть что загружать
        while SourceData.objects.filter(source=self.source, file_name=None).count():

            # Получаем первый объект данных с источников
            data = SourceData.objects.filter(source=self.source, file_name=None)[0]
            all = SourceData.objects.filter(source=self.source).count()
            other = all - SourceData.objects.filter(source=self.source, file_name=None).count()
            print(f'{other:,} / {all:,} {data}'.replace(',', ' '))

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
                if data_ is not None:
                    data.save_file(data_)
                else:
                    print('Delete', data)
                    data.delete()
