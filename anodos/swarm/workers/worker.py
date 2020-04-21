import requests
import datetime

import ftplib
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
        ftp = ftplib.FTP(host=host)
        ftp.login(user=self.source.login, passwd=self.source.password)

        # Переходим в нужный каталог
        if catalog:
            try:
                ftp.cwd(catalog)
            except ftplib.error_perm:
                return None

        # Получаем содержимое каталога
        result = ftp.nlst()

        # Закрываем соединение
        ftp.close()

        # Возвращаем результат
        return result

    def get_file_from_ftp(self, host, file_name):
        """Скачивает и возвращает файл с FTP-сервера"""

        # Инициализируем переменные
        ftp = ftplib.FTP(host=host)
        data = BytesIO(b"")

        # Авторизуемся
        ftp.login(user=self.source.login, passwd=self.source.password)

        # Переходим в нужный каталог
        # ftp.cwd(catalog)

        # Скачиваем файл
        print("Load: {}".format(file_name))
        ftp.retrbinary("RETR {}".format(file_name), data.write)
        return data
