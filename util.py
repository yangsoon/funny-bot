import re
from spider import fetch_lists

c_patt = re.compile('.*?\((?P<name>.*?)\)')


def inline_markup(req_name, page, end=False):
    markup = {
        'type': 'InlineKeyboardMarkup',
        'inline_keyboard': [[]]
    }
    page = int(page)
    if page > 1:
        markup['inline_keyboard'][0].append({
            'type': 'InlineKeyboardButton',
            'text': '<< 上一页',
            'callback_data': 'page-' + req_name + '-' + str(page-1)
        })
    markup['inline_keyboard'][0].append({
        'type': 'InlineKeyboardButton',
        'text': '第' + str(page) + '页',
        'callback_data': ' '
    })
    if not end:
        markup['inline_keyboard'][0].append({
            'type': 'InlineKeyboardButton',
            'text': '下一页 >>',
            'callback_data': 'page-' + req_name + '-' + str(page + 1)      
        })
    return markup


def format_url(req_name, base, page):
    if page == 1:
        return base
    if req_name == 'beauty':
        return 'http://tag.gamersky.com/news/1626' + '-' + str(page) + '.html'
    else:
        return base + 'List_' + str(page) + '.html'


def format_text(results):
    text = ""
    for index, item in enumerate(results):
        text += "%02d" % (index + 1) + '.' + item['title'] + \
            ' /P' + item['date'] + '_' + item['key'] + '\n'
    return text


async def format_message(req_name, url, page):
    url = format_url(req_name, url, page)
    results, nexe = await fetch_lists(url)
    end = True if nexe is None else False
    text = format_text(results)
    markup = inline_markup(req_name, page, end)
    return text, markup


def match_category(req, name):
    patt = re.compile(req+".*?")
    for item in name:
        if patt.match(item):
            return c_patt.search(item).groups('name')[0]
    return None
