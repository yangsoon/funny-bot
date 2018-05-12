import aiohttp
import json
from aiotg import Bot, Chat
from spider import fecth_lists

with open('token.json') as t, open('category.json') as c:
    token = json.loads(t.read())
    category = json.loads(c.read())
  
bot = Bot(**token)

@bot.command(r".*?\((.*?)\)")
async def async_fecth(chat: Chat, match):
    req_name = match.group(1)
    try:
        url = category[req_name]
    except KeyError:
        await chat.send_text("没有相应类型的图片，请重新输入")
    mark = 'G' if req_name == "dynamic" else 'P'
    results = await fecth_lists(url)
    text = ""
    for index, item in enumerate(results):
        text += "%02d" % (index + 1) + '.' + item['title'] + \
        ' /' + mark + item['date'] + '_' + item['key'] + '\n'
    ikmarkup = {
        'type': 'InlineKeyboardMarkup',
        'inline_keyboard': [
            [{'type': 'InlineKeyboardButton',
              'text': '第1页',
              'callback_data': ''},
             {'type': 'InlineKeyboardButton',
              'text': '下一页',
              'callback_data': 'page-' + req_name + '-2'}]
            ]
        }
    await chat.send_text(text, reply_makeup=json.dumps(ikmarkup))


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


@bot.callback(r'page-(\w+)')
async def buttonclick(chat, cq, match):
    await chat.edit_text(message_id=chat.message['message_id'], text="消息被修改了")

@bot.inline
async def inlinemode(iq):
    results = [{
            'type': 'article',
            'id': str(index),
            'title': article['title'],
            'input_message_content': { 'message_text': article['title']},
            'description': f"这里是{article['title']}"
        } for index, article in enumerate(category)]
    await iq.answer(results)