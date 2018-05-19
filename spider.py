import re
import aiohttp
from bs4 import BeautifulSoup

patt_url = re.compile('www.gamersky.com/(ent|wenku|news)/(?P<date>.*?)/(?P<key>.*?)\.shtml')
patt_next = re.compile(u'下一页')


def aioget(url):
    return aiohttp.request('GET', url)


async def fetch_lists(url):
    async with aioget(url) as resp:
        resp_text = await resp.text()
        content = BeautifulSoup(resp_text, "lxml")
        target_lists = content.find(class_="pictxt").find_all("li")
        results = []
        for item in target_lists:
            match = patt_url.search(item.a['href'])
            results.append({
                'title': item.a['title'],
                'date': match.group('date'),
                'key': match.group('key'),
                'desc': item.find(class_="txt").string
            })
        try:
            nexe = content.find(class_='p1 nexe')['href']
        except TypeError:
            nexe = None
        return results, nexe


def filter_img(tag):
    if tag.name != 'p':
        return False
    try:
        if tag.attrs['align'] == 'center':
            for child in tag.contents:
                if child.name == 'img' or child.name == 'a':
                    return True
        else:
            return False
    except KeyError:
        if 'style' in tag.attrs:
            return True
        else:
            return False


async def fetch_img(url):
    async with aioget(url) as resp:
        resp_text = await resp.text()
        content = BeautifulSoup(resp_text, "lxml")
        imgs = content.find(class_="Mid2L_con").findAll(filter_img)
        results = []
        for img in imgs:
            try:
                results.append({
                    'src':  img.find('img').attrs['src'],
                    'desc': '\n'.join(list(img.stripped_strings))
                })
            except AttributeError:
                continue
        nexe = True if patt_next.search(resp_text) else False
        return results, nexe
