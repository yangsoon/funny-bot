import json
import asyncio
from aiotg import Bot, Chat
from util import format_message, match_category
from spider import fetch_lists, fetch_img

with open('token.json') as t, open('category.json') as c:
    token = json.loads(t.read())
    category = json.loads(c.read())
  
bot = Bot(**token)
root_url = "http://www.gamersky.com/ent/"


@bot.command(r"/lists")
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
    await chat.send_text(text="请选择你喜欢的图片类型", reply_markup=json.dumps(keyboard))


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
async def change_lists(chat: Chat, cq, match):
    req_name = match.group('name')
    page = match.group('page')
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
    results, _ = await fetch_lists(category[req_name])
    c_results = [{
            'type': 'article',
            'id': str(index),
            'title': item['title'],
            'input_message_content': {
                'message_text': '/P' + item['date'] + '_' + item['key']
            },
            'description': item['desc']
        } for index, item in enumerate(results)]
    await iq.answer(c_results)


@bot.command(r"/P(?P<date>\d+)_(?P<key>\d+)")
async def get_img(chat: Chat, match):
    # date = match.group('date')
    # key = match.group('key')
    # url = root_url + date + '/' + key + '.shtml'
    # results = await fetch_img(url)
    # tasks = (chat.send_document(document=img['src'], caption=img['desc']) for img in results)
    # await asyncio.gather(*tasks)
    # with open("./imgs/test.gif", "rb") as f:
    #     doc_id  = await chat.send_document(f)
    #     print("doc_id=".format(doc_id))
    await chat.send_document(document='CgADBQADGAADH27gV-4mqdF3JjbOAg')