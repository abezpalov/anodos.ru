import time
import ftplib
import requests as r
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

    def send(self, content='test', chat_id=settings.TELEGRAM_LOG_CHAT, disable_web_page_preview=True):
        self.bot.send_message(chat_id=chat_id, text=content, parse_mode='HTML',
                              disable_web_page_preview=disable_web_page_preview)
        time.sleep(1)

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
            self.session = r.Session()

        if self.cookies is None:
            result = self.session.get(url, allow_redirects=True, verify=False)
            self.cookies = result.cookies
        else:
            result = self.session.get(url, allow_redirects=True, verify=False,
                                      cookies=self.cookies)
            self.cookies = result.cookies

        if result_type == 'cookie':
            return result.cookie
        elif result_type == 'text':
            return result.text
        elif result_type == 'html':
            tree = lxml.html.fromstring(result.text)
            return tree
        elif result_type == 'content':
            return result.content

        return result

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
