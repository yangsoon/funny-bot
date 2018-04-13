import aiohttp
from aiotg import Bot, Chat

bot = Bot(api_token="450403096:AAHCG8w6GEYoRBPJbm5yCnotpN0GrGewGMU", proxy="http://127.0.0.1:8118")

@bot.command(r"/echo (.+)")
def echo(chat: Chat, match):
    return chat.reply(match.group(1))

bot.run()