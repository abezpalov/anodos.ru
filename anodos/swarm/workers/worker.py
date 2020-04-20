import requests
import datetime

from ftplib import FTP
from io import BytesIO
from zipfile import ZipFile

from django.utils import timezone
from swarm.models import *


class Worker:

    def __init__(self):
        self.start_time = timezone.now()

    def get_ftp_catalog(self, host, catalog=None):
        """Возвращает содержимое папки"""

        # Авторизуемся
        ftp = FTP(host=host)
        ftp.login(user=self.source.login, passwd=self.source.password)

        # Переходим в нужный каталог
        if catalog:
            ftp.cwd(catalog)

        # Получаем содержимое каталога
        result = ftp.nlst()

        # Закрываем соединение
        ftp.close()

        # Возвращаем результат
        return result



