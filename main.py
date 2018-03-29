import json
from aiotg import Bot, Chat

with open("token.conf") as f:
    conf = json.load(f)

bot = Bot(**conf)

@bot.command(r"/echo (.+)")
def echo(chat: Chat, match):
    return chat.reply(match.group(1))

bot.run()
