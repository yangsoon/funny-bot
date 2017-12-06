# -*- coding : utf-8 -*-
import telegram
import json
import logging
from commands import start, remove, get_list, \
    change_page, get_photo, FilterTypes, FilterKey
from telegram.ext import CommandHandler, CallbackQueryHandler, \
    Updater, MessageHandler

with (open('token.conf', 'r')) as f:
    token = json.loads(f.read())['token']


def error_callback(bot, update, error):
    raise error


class FunnyPhoto:

    def __init__(self):
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        self.begin()

    def begin(self):
        filter_types = FilterTypes()
        filter_key = FilterKey()
        start_handler = CommandHandler('start', start)
        types_handler = MessageHandler(filter_types, get_list)
        key_handler = MessageHandler(filter_key, get_photo)
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(CallbackQueryHandler(change_page))
        self.dispatcher.add_handler(types_handler)
        self.dispatcher.add_handler(key_handler)
        self.dispatcher.add_handler(CommandHandler('remove', remove))
        self.dispatcher.add_error_handler(error_callback)


if __name__ == "__main__":
    bot = FunnyPhoto()
    bot.updater.start_polling()
    bot.updater.idle()