import os
from swarm.models import *
from swarm.workers.zakupki_44_download import Worker


class Worker(Worker):

    host = 'ftp.zakupki.gov.ru'
    start_url = 'out'
    name = 'ftp.zakupki.gov.ru/223'
    login = 'fz223free'
    password = 'fz223free'

    def __init__(self):
        super().__init__()