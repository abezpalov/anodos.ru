import anodos.tools
import swarm.models
import pflops.models
import distributors.models
import swarm.workers.worker


class Worker(swarm.workers.worker.Worker):

    name = 'Центральный банк России'
    urls = {'base': 'http://cbr.ru',
            'data': 'https://cbr.ru/currency_base/daily/'}
    cols = {'Цифр. код': None,
            'Букв. код': None,
            'Единиц': None,
            'Валюта': None,
            'Курс': None}

    def __init__(self):
        self.source = swarm.models.Source.objects.take(name=self.name)
        self.count_of_currencies = 0
        self.message = None
        super().__init__()

    def run(self):

        if self.command == 'update_currencies':
            self.update_currencies()
            self.message = f'- валют: {self.count_of_currencies}.'

        if self.message:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}:\n'
                                      f'{self.message}')
        else:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}.\n')

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
                currency = distributors.models.Currency.objects.take(key=key,
                                                                     name=name,
                                                                     key_digit=key_digit,
                                                                     quantity=quantity,
                                                                     rate=rate)
                currency = pflops.models.Currency.objects.take(key=key,
                                                               name=name,
                                                               key_digit=key_digit,
                                                               quantity=quantity,
                                                               rate=rate)
                print(currency)

                self.count_of_currencies += 1
