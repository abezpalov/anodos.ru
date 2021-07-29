import os
import sys
import warnings

from django.core.wsgi import get_wsgi_application
from django.conf import settings

import telebot

# Убираем предупреждения
warnings.filterwarnings("ignore")

# Импортируем настройки проекта Django
sys.path.append('/home/abezpalov/anodos.ru/anodos/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'anodos.settings'

# Магия
application = get_wsgi_application()

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
print('Telegram bot loaded')


@bot.message_handler(commands=['start'])
def send_welcome(message):

    # TODO LOG
    bot.forward_message(chat_id=settings.TELEGRAM_LOG_CHAT,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id)

    content = f'Опознана белковая форма жизни!\nid: {message.from_user.id}\nfirst_name: {message.from_user.first_name}\nlast_name: {message.from_user.last_name}'
    bot.reply_to(message, content)

    print(content)

# TODO
    content = f'Пришли мне своё фото для подтверждения!'
    bot.send_message(chat_id=message.chat.id, text=content)
#    bot.send_message(chat_id=settings.TELEGRAM_LOG_CHAT, text=content)
#    print(content)


@bot.message_handler(content_types=['text'])
def content_text(message):

    # TODO LOG
    bot.forward_message(chat_id=settings.TELEGRAM_LOG_CHAT,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id)

    print(message.text)


@bot.message_handler(content_types=['document'])
def content_document(message):

    # TODO LOG
    bot.forward_message(chat_id=settings.TELEGRAM_LOG_CHAT,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id)

    print('Боту отправили документ')


@bot.message_handler(content_types=['photo'])
def content_document(message):

    # TODO LOG
    bot.forward_message(chat_id=settings.TELEGRAM_LOG_CHAT,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id)

    content = 'Бот пошутил, а ему всё равно отправили фото. Боту приятно. Какой наивный мешок с костями))'
    bot.send_message(chat_id=message.chat.id, text=content)


bot.polling(none_stop=True)
