import re
import logging
import asyncio
import aioredis
from io import BytesIO
from aiotg import BotApiError
from spider import aioget, fetch_lists, fetch_img


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(message)s',
    datefmt='%Y-%m-%d %A %H:%M:%S')

c_patt = re.compile('.*?\((?P<name>.*?)\)')
root_url = "http://www.gamersky.com/ent/"


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
    logging.info(f'fetch {req_name} lists from {url}')
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
            logging.info(error.response)
        return dict(file_ids=message['result']['photo'], desc=img['desc'])


async def download_photo(chat, imgs):
    tasks = (download_one(chat, img) for img in imgs)
    return await asyncio.gather(*tasks)


async def get_fileid(key, page):
    conn = await aioredis.create_connection(('redis', 6379))
    return await conn.execute('hget', key, page)


async def store_fileid(fileid, key, page, nexe):
    conn = await aioredis.create_connection(('redis', 6379))
    img_page = dict(imgs=fileid, nexe=nexe)
    await conn.execute('hset', key, page, str(img_page))
    logging.info(f'{key}-{page} stored')


async def log_users(message):
    conn = await aioredis.create_connection(('redis', 6379))
    await conn.execute('sadd', 'users', str(message['result']['chat']))
    number = await conn.execute('scard', 'users')
    logging.info(f'add a new user! there are {number} users')


async def produce_imgs(chat, date, key, page):
    dbs = await get_fileid(date+key, page)
    if page == '1':
        url = root_url + date + '/' + key + '.shtml'
    else:
        url = root_url + date + '/' + key + '_' + page + '.shtml'
    if dbs:
        logging.info(f'fetch {date+key}-{page} fileid from redis')
        dbs = eval(dbs)
        tasks = (chat.send_photo(photo=img['file_ids'][0]['file_id'], caption=img['desc']) for img in dbs['imgs'])
        await asyncio.gather(*tasks)
        nexe = dbs['nexe']
    else:
        logging.info(f'fetch imgs from {url}')
        results, nexe = await fetch_img(url)
        file_id = await download_photo(chat, results)
        await store_fileid(file_id, date+key, page, nexe)
    if nexe:
        text = '下一页(第' + str(int(page) + 1) + '页)'
        page = str(int(page) + 1)
    else:
        text = "您已全部看完"
        page = None
    markup = photo_inline_markup(date, key, text, url, page)
    return markup
