import zipfile
from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    def __init__(self):
        super().__init__()

    def run(self):
        # При необходимости удаляем предыдущие версии
        self.clear()

        # Забираем все объекты, требующие обработку
        count = SourceData.objects.filter(parsed=None, file_name__endswith='.zip').count()
        print(f'Нераспакованных файлов: {count}')
        for source_data in SourceData.objects.filter(parsed=None, file_name__icontains='.zip'):

            # Получаем список файлов в архиве
            try:
                with zipfile.ZipFile(source_data.file_name, 'r') as zip:
                    for file_name in zip.namelist():
                        content_type = file_name.split('.')[-1]
                        content = zip.open(file_name).read()
                        data = Data.objects.add(source_data=source_data,
                                                content_type=content_type,
                                                file_name=file_name,
                                                content=content)
                    source_data.set_parsed()
                    print(source_data, '- parced', len(zip.namelist()))

            except zipfile.BadZipFile:
                source_data.delete()

    def clear(self):
        print(Data.objects.all().count())
        Data.objects.all().delete()
        print(Data.objects.all().count())

        print(SourceData.objects.filter(parsed=None, file_name__endswith='.zip').count())
        SourceData.objects.filter(file_name__endswith='.zip').update(parsed=None)
        print(SourceData.objects.filter(parsed=None, file_name__endswith='.zip').count())
        exit()