import re
import asyncio
from aiotg import BotApiError
from io import BytesIO
from spider import aioget, fetch_lists
from PIL import Image

c_patt = re.compile('.*?\((?P<name>.*?)\)')


def lists_inline_markup(req_name, page, end=False):
    markup = {
        'type': 'InlineKeyboardMarkup',
        'inline_keyboard': [[]]
    }
    page = int(page)
    if page > 1:
        markup['inline_keyboard'][0].append({
            'type': 'InlineKeyboardButton',
            'text': '<< 上一页',
            'callback_data': 'page-' + req_name + '-' + str(page - 1)
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


def photo_inline_markup(date, key, text, url, page):
    markup = {
        'type': 'InlineKeyboardMarkup',
        'inline_keyboard': [[{
            'type': 'InlineKeyboardButton',
            'text': url,
            'url': url,
            'callback_data': ' '
        }]]
    }
    if page:
        markup['inline_keyboard'].append([{
            'type': 'InlineKeyboardButton',
            'text': text,
            'callback_data': 'photo-' + date + '-' + key + '-' + page
        }])
    else:
        markup['inline_keyboard'].append([{
            'type': 'InlineKeyboardButton',
            'text': text,
            'callback_data': ' '
        }])
    return markup


def format_url(req_name, base, page):
    if page == 1:
        return base
    if req_name == 'beauty':
        return 'http://tag.gamersky.com/news/1626' + '-' + str(page) + '.html'
    else:
        return base + 'List_' + str(page) + '.html'


def format_text(results, ptype):
    text = ""
    for index, item in enumerate(results):
        text += "%02d" % (index + 1) + '.' + item['title'] + \
            ' /' + ptype + item['date'] + '_' + item['key'] + '\n'
    return text


async def format_message(req_name, url, page):
    ptype = 'G' if req_name == "dynamic" else 'P'
    url = format_url(req_name, url, page)
    results, nexe = await fetch_lists(url)
    end = True if nexe is None else False
    text = format_text(results, ptype)
    markup = lists_inline_markup(req_name, page, end)
    return text, markup


def match_category(req, name):
    patt = re.compile(req + ".*?")
    for item in name:
        if patt.match(item):
            return c_patt.search(item).groups('name')[0]
    return None


async def download_gif(chat, img):
    # async with aioget(img['src']) as resp:
    #     r = await resp.read()
    #     img_raw = BytesIO(r)
    #     im = Image.open(img_raw)
    #     gif = BytesIO()
    #     im.save(gif, "gif")
    await chat.send_document(document=img['src'], caption=img['desc'])


async def download_gifs(chat, imgs):
    tasks = (download_gif(chat, img) for img in imgs)
    await asyncio.gather(*tasks)


async def download_one(chat, img):
    async with aioget(img['src']) as resp:
        r = await resp.read()
        img_raw = BytesIO(r)
        try:
            message = await chat.send_photo(photo=img_raw.read(), caption=img['desc'])
        except BotApiError as error:
            print(error.response)
        return message['result']['photo']


async def download_photo(chat, imgs):
    tasks = (download_one(chat, img) for img in imgs)
    return await asyncio.gather(*tasks)
