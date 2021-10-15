from csv import reader

from django.conf import settings
from swarm.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'gisp.gov.ru'
    login = None
    password = None
    urls = {'719': 'https://gisp.gov.ru/opendata/files/gispdata-current-pp719-products-structure.csv',
            'test': 'https://gisp.gov.ru/opendata/files/pp719-products-structure.csv'}
    company = 'МинПромТорг России'

    def __init__(self):
        self.source = Source.objects.take(name=self.name)
        self.file_name = f'{settings.MEDIA_ROOT}gisp_temp.csv'
        self.cell_numbers = {'Nameoforg': None,
                             'OGRN': None,
                             'INN': None,
                             'Registernumber': None,
                             'Productname': None,
                             'OKPD2': None,
                             'TNVED': None,
                             'Nameofregulations': None}
        super().__init__()


    def run(self, command=None):

        data = self.load(url=self.urls['719'], result_type='content')
        f = open(self.file_name, 'wb')
        f.write(data)
        f.close()

        with open(self.file_name, 'r') as read_obj:
            # pass the file object to reader() to get the reader object
            csv_reader = reader(read_obj)
            # Pass reader object to list() to get a list of lists
            list_of_rows = list(csv_reader)

        for n, row in enumerate(list_of_rows):

            # Заголовок таблицы
            if n == 0:
                for m, cell in enumerate(row):
                    self.cell_numbers[cell] = m

            else:
                organisation_name = row[self.cell_numbers['Nameoforg']]
                ogrn = row[self.cell_numbers['OGRN']]
                inn = row[self.cell_numbers['INN']]
                organisation = Organisation.objects.take(ogrn=ogrn,
                                                         name=organisation_name,
                                                         inn=inn)

                register_number = row[self.cell_numbers['Registernumber']]
                product_name = row[self.cell_numbers['Productname']]
                okpd2 = row[self.cell_numbers['OKPD2']]
                tnved = row[self.cell_numbers['TNVED']]
                name_of_regulation = row[self.cell_numbers['Nameofregulations']]
                product = Product.objects.take(register_number=register_number,
                                               organisation=organisation,
                                               name=product_name,
                                               okpd2=okpd2,
                                               tnved=tnved,
                                               name_of_regulation=name_of_regulation)

                if product.new:
                    content = f'<b>{product.register_number}</b>\n' \
                              f'{organisation.name}\n' \
                              f'<i>ОГРН: {organisation.ogrn}</i>\n' \
                              f'<i>ИНН: {organisation.inn}</i>\n\n' \
                              f'{product.name}\n' \
                              f'<i>ОКВЭД2: {product.okpd2}</i>\n' \
                              f'<i>ТН ВЭД: {product.tnved}</i>\n' \
                              f'<i>Регулирование: {product.name_of_regulation}</i>'
                    self.send(content=content, chat_id=settings.TELEGRAM_GISP_CHAT)
                    print(product)

