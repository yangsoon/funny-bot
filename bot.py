import json
from aiotg import Bot, Chat, CallbackQuery
from util import format_message, match_category, \
    download_gifs, produce_imgs, log_users
from spider import fetch_lists, fetch_img

with open('token.json') as t, open('category.json') as c:
    token = json.loads(t.read())
    category = json.loads(c.read())

bot = Bot(**token)
root_url = "http://www.gamersky.com/ent/"
help_tetx = "点击按钮查看下一页, 或者点击原网址查看详细内容"


@bot.command(r"/start")
async def list_category(chat: Chat, match):
    kb, row = [], -1
    for idx, item in enumerate(category["name"]):
        if idx % 2 == 0:
            kb.append([])
            row += 1
        kb[row].append(item)
    keyboard = {
        "keyboard": kb,
        "resize_keyboard": True
    }
    message = await chat.send_text(text="请选择你喜欢的图片类型", reply_markup=json.dumps(keyboard))
    await log_users(message)


@bot.command(r".*?\((?P<name>.*?)\)")
async def get_lists(chat: Chat, match):
    req_name = match.group('name')
    try:
        url = category[req_name]
    except KeyError:
        await chat.send_text("没有相应类型的图片，请重新输入")
    text, markup = await format_message(req_name, url, 1)
    await chat.send_text(text, reply_markup=json.dumps(markup))


@bot.callback(r"page-(?P<name>\w+)-(?P<page>\d+)")
async def change_lists(chat: Chat, cq: CallbackQuery, match):
    await cq.answer(text="列表更新中....")
    req_name, page = match.group('name'), match.group('page')
    url = category[req_name]
    text, markup = await format_message(req_name, url, page)
    await chat.edit_text(message_id=chat.message['message_id'], text=text, markup=markup)


@bot.inline
async def inline_default(iq):
    desc = category['desc']
    results = [{
        'type': 'article',
        'id': str(index),
        'title': name,
        'input_message_content': {'message_text': name},
        'description': desc[index]
    } for index, name in enumerate(category['name'])]
    await iq.answer(results)


@bot.inline(r"([\u4e00-\u9fa5]+)")
async def inline_name(iq, match):
    req = match.group(1)
    req_name = match_category(req.strip(), category['name'])
    if req_name is None:
        return
    ptype = 'G' if req_name == "dynamic" else 'P'
    results, _ = await fetch_lists(category[req_name])
    c_results = [{
        'type': 'article',
        'id': str(index),
        'title': item['title'],
        'input_message_content': {
                'message_text': '/' + ptype + item['date'] + '_' + item['key']
        },
        'description': item['desc']
    } for index, item in enumerate(results)]
    await iq.answer(c_results)


@bot.command(r"/G(?P<date>\d+)_(?P<key>\d+)")
async def get_gif(chat: Chat, match):
    date, key = match.group('date'), match.group('key')
    url = root_url + date + '/' + key + '.shtml'
    markup = {
        'type': 'InlineKeyboardMarkup',
        'inline_keyboard': [[{
            'type': 'InlineKeyboardButton',
            'text': "动态图原地址",
            'url': url,
            'callback_data': ' '
        }], [{
            'type': 'InlineKeyboardButton',
            'text': "欢迎在github上提出建议",
            'url': "https://github.com/yangsoon/funny-bot/issues",
            'callback_data': ' '
        }]]
    }
    text = "抱歉,动态图在优化中,如果你有好的想法,欢迎在github上提出issue"
    await chat.send_text(text=text, reply_markup=json.dumps(markup))
    results, _ = await fetch_img(url)
    await download_gifs(chat, results)


@bot.command(r"/P(?P<date>\d+)_(?P<key>\d+)")
async def get_photo(chat: Chat, match):
    date, key = match.group('date'), match.group('key')
    markup = await produce_imgs(chat, date, key, '1')
    await chat.send_text(text=help_tetx, reply_markup=json.dumps(markup))


@bot.callback(r"photo-(?P<date>\d+)-(?P<key>\d+)-(?P<page>\d+)")
async def change_photo(chat: Chat, cq: CallbackQuery, match):
    await cq.answer(text="图片加载中....")
    date, key, page = match.group('date'), match.group(
        'key'), match.group('page')
    markup = await produce_imgs(chat, date, key, page)
    await chat.send_text(text=help_tetx, reply_markup=json.dumps(markup))
