import time
import ftplib
import requests
import lxml.html
from io import BytesIO
import telebot

from django.conf import settings
from django.utils import timezone
from swarm.models import *


class Worker:

    def __init__(self):
        self.start_time = timezone.now()
        self.ftp = None
        self.session = None
        self.cookies = None
        self.bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

    def send(self, content='test', disable_web_page_preview=True):
        self.bot.send_message(chat_id=settings.TELEGRAM_CHAT, text=content, parse_mode='HTML',
                              disable_web_page_preview=disable_web_page_preview)
        # time.sleep(10)

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

    def load(self, url, result_type=None):

        if self.session is None:
            self.session = requests.Session()

        if self.cookies is None:
            r = self.session.get(url, allow_redirects=True, verify=False)
            self.cookies = r.cookies
        else:
            r = self.session.get(url, allow_redirects=True, verify=False,
                                 cookies=self.cookies)
            self.cookies = r.cookies

        if result_type == 'cookie':
            return r.cookie
        elif result_type == 'text':
            return r.text
        elif result_type == 'html':
            tree = lxml.html.fromstring(r.text)
            return tree
        elif result_type == 'content':
            return r.content

        return r

    @staticmethod
    def fix_text(text):
        while '  ' in text:
            text = text.replace('  ', ' ')
        while '/n/n' in text:
            text = text.replace('/n/n', '/n')
        text = text.replace(' : ', ': ')
        text = text.replace(' - ', ' — ')
        text = text.strip()

        return text
