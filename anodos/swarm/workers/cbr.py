import swarm.models
import swarm.workers.worker
import pflops.models
import distributors.models


class Worker(swarm.workers.worker.Worker):

    name = 'cbr.ru'
    urls = {'base': 'http://cbr.ru'}
    company = 'ЦБР'

    def __init__(self):
        self.source = swarm.models.Source.objects.take(name=self.name)
        self.count_currencies = 0
        self.urls['data'] = f'https://cbr.ru/currency_base/daily/'

        self.cols = {'Цифр. код': None,
                     'Букв. код': None,
                     'Единиц': None,
                     'Валюта': None,
                     'Курс': None}

        super().__init__()

    def run(self, command=None):

        if command == 'update_currencies':
            self.update_currencies()

    def update_currencies(self):

        # Получаем данные
        tree = self.load(self.urls['data'], result_type='html')
        table = tree.xpath('.//table[@class="data"]')[0]

        # Проходим по строкам полученной таблицы
        trs = table.xpath('.//tr')
        for n, tr in enumerate(trs):

            if n == 0:
                # Определяем номера колонок
                ths = tr.xpath('.//th//text()')
                for m, th in enumerate(ths):
                    self.cols[th] = m

            else:
                tds = tr.xpath('.//td//text()')
                key = tds[self.cols['Букв. код']]
                key_digit = tds[self.cols['Цифр. код']]
                name = tds[self.cols['Валюта']]
                quantity = tds[self.cols['Единиц']]
                rate = tds[self.cols['Курс']]
                currency = pflops.models.Currency.objects.take(key=key,
                                                               name=name,
                                                               key_digit=key_digit,
                                                               quantity=quantity,
                                                               rate=rate)
                print(currency)
                currency = distributors.models.Currency.objects.take(key=key,
                                                                     name=name,
                                                                     key_digit=key_digit,
                                                                     quantity=quantity,
                                                                     rate=rate)
                print(currency)
