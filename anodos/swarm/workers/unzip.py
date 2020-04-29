import zipfile
from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    def __init__(self):
        super().__init__()

    def run(self):
        # Забираем все объекты, требующие обработку
        count = SourceData.objects.filter(parsed=None, file_name__icontains='.zip').count()
        print(f'Нераспакованных файлов: {count}')
        for source_data in SourceData.objects.filter(parsed=None, file_name__icontains='.zip'):

            # Получаем список файлов в архиве
            try:
                with zipfile.ZipFile(source_data.file_name, 'r') as zip:
                    for file_name in zip.namelist():
                        content_type = None
                        if file_name.endswith('.xml'):
                            content_type = 'xml'
                        if content_type:
                            content = zip.open(file_name).read()
                            data = Data.objects.add(source_data=source_data,
                                                    content_type=content_type,
                                                    file_name=file_name,
                                                    content=content)
                            print(data)
                    source_data.set_parsed()
                    print(source_data, '- parced', len(zip.namelist()))

            except zipfile.BadZipFile:
                source_data.delete()
