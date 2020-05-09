import ftplib
from io import BytesIO

from django.utils import timezone
from swarm.models import *


class Worker:

    def __init__(self):
        self.start_time = timezone.now()
        self.ftp = None

    def ftp_login(self, host):
        if self.ftp is None:
            self.ftp = ftplib.FTP(host=host, timeout=30)
            self.ftp.set_pasv(val=True)
            self.ftp.login(user=self.source.login, passwd=self.source.password)

    def get_ftp_catalog(self, host, catalog=None):
        """Возвращает содержимое папки"""

        # Авторизуемся
        self.ftp_login(host)

        # Переходим в нужный каталог
        if catalog:
            try:
                self.ftp.cwd(catalog)
            except ftplib.error_perm:
                return None

        # Получаем содержимое каталога
        result = self.ftp.nlst()
        return result

    def get_file_from_ftp(self, host, file_name):
        """Скачивает и возвращает файл с FTP-сервера"""

        # Авторизуемся
        self.ftp_login(host)

        # Инициализируем переменные
        data = BytesIO(b"")

        # Скачиваем файл
        try:
            self.ftp.retrbinary("RETR {}".format(file_name), data.write)
        except ftplib.error_perm:
            self.ftp.close()
            self.ftp = None
            return None
        return data
