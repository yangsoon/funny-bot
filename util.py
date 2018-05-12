from spider import fetch_lists


def inline_markup(req_name, page, end=False):
    markup = {
        'type': 'InlineKeyboardMarkup',
        'inline_keyboard': [[]]
    }
    page = int(page)
    if page > 1:
        markup['inline_keyboard'][0].append({
            'type': 'InlineKeyboardButton',
            'text': '上一页',
            'callback_data': 'page-' + req_name + '-' + str(page-1)
        })
    markup['inline_keyboard'][0].append({
        'type': 'InlineKeyboardButton',
        'text': '第' + str(page) + '页',
        'callback_data': 'none'      
    })
    if not end:
        markup['inline_keyboard'][0].append({
            'type': 'InlineKeyboardButton',
            'text': '下一页',
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
    markup = inline_markup(req_name, page, end)
    return text, markup
