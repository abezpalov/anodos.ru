import requests as r
import json

from swarm.models import *
from trader.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    name = 'ocs.ru/b2b'
    login = None
    password = None
    company = 'OCS'
    url = 'https://testconnector.b2b.ocs.ru/api/v2/'

    def __init__(self):
        self.source = Source.objects.take(
            name=self.name,
            login=self.login,
            password=self.password)
        self.token = settings.OCS_TOKEN

        super().__init__()

    def run(self):

        self.update_catalog_categories()

    def get(self, command=''):
        url = f'{self.url}{command}'
        print(url)
        headers = {'X-API-Key': self.token,
                   'accept': 'application/json'}
        print(headers)
        result = r.get(url, headers=headers, verify=None)
        return result.text()

    def update_catalog_categories(self):
        command = 'catalog/categories'

        currencies_exchanges = self.get(command)
        print(currencies_exchanges)

