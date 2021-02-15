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
    url = 'https://connector.b2b.ocs.ru'

    def __init__(self):
        self.source = Source.objects.take(
            name=self.name,
            login=self.login,
            password=self.password)
        self.token = settings.OCS_TOKEN

        super().__init__()

    def run(self):

        pass

    def get(self, command=''):
        url = f'{self.url}{command}'
        print(url)
        headers = {'Authorization': f'Bearer {self.token}',
                   'accept': 'application/json'}
        result = r.get(url, headers=headers, verify=None)
        return result.json()

