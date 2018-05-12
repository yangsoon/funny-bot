import json
from aiotg import Bot, Chat
from util import format_message


with open('token.json') as t, open('category.json') as c:
    token = json.loads(t.read())
    category = json.loads(c.read())
  
bot = Bot(**token)


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


@bot.callback(r'page-(?P<name>\w+)-(?P<page>\d+)')
async def change_lists(chat: Chat, cq, match):
    req_name = match.group('name')
    page = match.group('page')
    url = category[req_name]
    text, markup = await format_message(req_name, url, page)
    await chat.edit_text(message_id=chat.message['message_id'], text=text, markup=markup)


@bot.inline
async def inline_mode(iq):
    desc = category['desc']
    results = [{
            'type': 'article',
            'id': str(index),
            'title': name,
            'input_message_content': { 'message_text': name},
            'description': desc[index]
        } for index, name in enumerate(category['name'])]
    await iq.answer(results)