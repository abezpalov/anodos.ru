from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    host = 'ftp.zakupki.gov.ru'
    url_list = ['fcs_nsi/',
                'fcs_regions/Adygeja_Resp',
                'fcs_regions/Altaj_Resp',
                'fcs_regions/Altajskij_kraj',
                'fcs_regions/Amurskaja_obl',
                'fcs_regions/Arkhangelskaja_obl',
                'fcs_regions/Astrakhanskaja_obl',
                'fcs_regions/Bajkonur_g',
                'fcs_regions/Bashkortostan_Resp',
                'fcs_regions/Belgorodskaja_obl',
                'fcs_regions/Brjanskaja_obl',
                'fcs_regions/Burjatija_Resp',
                'fcs_regions/Chechenskaja_Resp',
                'fcs_regions/Cheljabinskaja_obl',
                'fcs_regions/Chukotskij_AO',
                'fcs_regions/Chuvashskaja_Resp',
                'fcs_regions/Dagestan_Resp',
                'fcs_regions/Evrejskaja_Aobl',
                'fcs_regions/Ingushetija_Resp',
                'fcs_regions/Irkutskaja_obl',
                'fcs_regions/Ivanovskaja_obl',
                'fcs_regions/Jamalo-Neneckij_AO',
                'fcs_regions/Jaroslavskaja_obl',
                'fcs_regions/',
                ]
    black_list = ['fcs_nsi/nsiUser']
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

        # Если нужно удалить информацию об источниках данных
        #SourceData.objects.filter(source=self.source).delete()
        exit()

        # Создаём записи стартовых позиций загрузки
        if SourceData.objects.filter(source=self.source, file_name=None).count() == 0:
            for url in self.start_list:
                SourceData.objects.take(source=self.source, url=url)

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
                    if url not in self.black_list:
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
