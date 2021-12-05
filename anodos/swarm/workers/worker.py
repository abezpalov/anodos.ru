import sys
import ftplib
import requests
import lxml.html
import lxml.etree
import json
from io import BytesIO
import chardet

from django.conf import settings
from django.utils import timezone

import anodos.tools


class Worker:

    name = None

    def __init__(self):
        self.start_time = timezone.now()
        self.ftp = None
        self.session = None
        self.cookies = None
        self.message = None
        try:
            self.command = sys.argv[2]
        except IndexError:
            self.command = None

    def __del__(self):
        delta = timezone.now() - self.start_time
        print(f'{self.name} finish at {delta}')

    def delta(self):
        return timezone.now() - self.start_time

    def ftp_login(self, host):
        self.ftp = ftplib.FTP(host=host, timeout=30)
        self.ftp.set_pasv(val=True)
        self.ftp.login(user=self.source.login, passwd=self.source.password)
        self.ftp.encoding = 'utf-8'

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

    def load(self, url, result_type=None, request_type='GET', timeout=600.0):

        if self.session is None:
            self.session = requests.Session()

        if request_type == 'POST':
            result = self.session.post(url, allow_redirects=True, verify=False, timeout=timeout)
        else:
            try:
                if self.cookies is None:
                    result = self.session.get(url, allow_redirects=True, verify=False, timeout=timeout)
                    self.cookies = result.cookies
                else:
                    result = self.session.get(url, allow_redirects=True, verify=False,
                                              cookies=self.cookies, timeout=timeout)
                    self.cookies = result.cookies
            except requests.exceptions.TooManyRedirects:
                return None

        if result_type == 'cookie':
            return result.cookie
        elif result_type == 'text':
            return result.text
        elif result_type == 'html':
            tree = lxml.html.fromstring(result.content)
            return tree
        elif result_type == 'html+text':
            tree = lxml.html.fromstring(result.content)
            return tree, result.text
        elif result_type == 'xml':
            tree = lxml.etree.fromstring(result.content)
            for el in tree.iter():
                if el.tag.startswith('{'):
                    el.tag = el.tag[el.tag.index('}')+1:]
            return tree
        elif result_type == 'json':
            data = json.loads(result.text)
            return data
        elif result_type == 'content':
            return result.content

        return result
