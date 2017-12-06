# -*- coding : utf-8 -*-
import re
import json
import telegram
from spider import fetch_list, fetch_photo
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import BaseFilter
from telegram.error import TimedOut, BadRequest

types = {
    "FunnyGif": "111",
    "FunnyPhoto": "147"
}

patt = re.compile('/FunnyGif|/FunnyPhoto')
patt_key = re.compile('/D|/G\d{6}_\d+$')
patt_url = re.compile('www.gamersky.com/ent/(?P<date>.*?)/(?P<key>.*?)\.shtml')


class FilterTypes(BaseFilter):
    def filter(self, message):
        if re.match(patt, message.text):
            return True


class FilterKey(BaseFilter):
    def filter(self, message):
        if re.match(patt_key, message.text):
            return True


def start(bot, update):
    response = u'''
    欢迎使用FunnyPhoto，我是游民星空趣图非官方机器人，
    输入 /FunnyGif 获取动态趣图列表
    输入 /FunnyPhoto 获取内涵囧途
    轻松一刻、冷知识、美女、福利图还在开发中...
    '''
    update.message.reply_text(text=response)


def remove(bot, update):
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(update.message.chat_id, text='clear',
                     reply_markup=reply_markup)


def get_list(bot, update):
    callback_data = {
        "type": "list",
        "mark": types[update.message.text.replace('/', '')],
        "page": "List_2.html"
    }
    keyboard = [[InlineKeyboardButton(
        u"下一页", callback_data=json.dumps(callback_data))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    results, _, _ = fetch_list(mark=callback_data['mark'])
    text = '你好！这里是 ' + \
        update.message.text.replace('/', '') + ' 列表，点击每个趣图后的命令，查看详情\n'
    if update.message.text == '/FunnyGif':
        prefix = '/G'
    else:
        prefix = '/D'
    for index, item in enumerate(results):
        command = patt_url.search(item['link'])
        text = text + str(index + 1) + '. ' + item['title'] + '\n' + prefix + \
            command.group('date') + '_' + command.group('key') + '\n'
    update.message.reply_text(text=text, reply_markup=reply_markup)


def change_page(bot, update):
    query = update.callback_query
    params = json.loads(query.data)
    if params['type'] == 'list':
        results, pre, nexe = fetch_list(
            mark=params['mark'], page=params['page'])
        text = ''
        if params['mark'] == types['FunnyGif']:
            prefix = '/G'
        else:
            prefix = '/D'
        for index, item in enumerate(results):
            command = patt_url.search(item['link'])
            text = text + str(index + 1) + '. ' + item['title'] + '\n' + prefix + \
                command.group('date') + '_' + command.group('key') + '\n'
        keyboard = [[]]
        if pre:
            if pre == "/ent/" + params['mark'] + '/':
                pre = ""
            callback_data = {
                "type": "list",
                "mark": params['mark'],
                "page": pre
            }
            keyboard[0].append(InlineKeyboardButton(
                u"上一页", callback_data=json.dumps(callback_data)))
        if nexe:
            callback_data = {
                "type": "list",
                "mark": params['mark'],
                "page": nexe
            }
            keyboard[0].append(InlineKeyboardButton(
                u"下一页", callback_data=json.dumps(callback_data)))
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text=text,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup)

    if params['type'] == 'photo':
        results, nexe = fetch_photo(params['key'], params['page'])
        print('fetch {0} photo from {1} {2}'.format(
            len(results), params['key'], params['page']))
        for img in results:
            print('send {0} to {1}'.format(img, query.message.chat_id))
            try:
                bot.send_document(chat_id=query.message.chat_id,
                                  document=img,
                                  disable_notification=True,
                                  timeout=40)
            except TimedOut:
                continue
            except BadRequest:
                continue
        if nexe:
            callback_data = {
                "type": "photo",
                "key": params['key'],
                "page": nexe
            }
            keyboard = [[InlineKeyboardButton(
                u"下一页", callback_data=json.dumps(callback_data))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(chat_id=query.message.chat_id,
                             text='点击下面的按钮查看下一页吧!',
                             reply_markup=reply_markup)
        else:
            bot.send_message(chat_id=query.message.chat_id,
                             text='你已经全部看完啦! 输入 /FunnyGif 或者 /FunnyPhoto 查看更多趣图')


def get_photo(bot, update):
    message = update.message.text.replace('/', '')
    if message[0] == 'G':
        key = '/'.join(message.replace('G', '').split('_'))
    else:
        key = '/'.join(message.replace('D', '').split('_'))
    results, nexe = fetch_photo(key)
    print('fetch {0} photo from {1}'.format(len(results), key))
    for img in results:
        print('send {0} to {1}'.format(img, update.message.chat_id))
        if message[0] == 'G':
            try:
                bot.send_document(chat_id=update.message.chat_id,
                                  document=img,
                                  disable_notification=True,
                                  timeout=40)
            except TimedOut:
                continue
            except BadRequest:
                continue
        else:
            try:
                bot.send_photo(chat_id=update.message.chat_id,
                               photo=img,
                               disable_notification=True,
                               timeout=40)
            except TimedOut:
                continue
    if nexe:
        callback_data = {
            "type": "photo",
            "key": key,
            "page": nexe
        }
        keyboard = [[InlineKeyboardButton(
            u"下一页", callback_data=json.dumps(callback_data))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=update.message.chat_id,
                         text='点击下面的按钮查看下一页吧!',
                         reply_markup=reply_markup)
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text='你已经全部看完啦! 输入 /FunnyGif 或者 /FunnyPhoto 查看更多趣图')
