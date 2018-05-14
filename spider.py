import re
import aiohttp
from bs4 import BeautifulSoup

patt_url = re.compile('www.gamersky.com/(ent|wenku|news)/(?P<date>.*?)/(?P<key>.*?)\.shtml')


def aioget(url):
    return aiohttp.request('GET', url)


async def fetch_lists(url):
    async with aioget(url) as resp:
        resp_text = await resp.text()
        content = BeautifulSoup(resp_text, "html.parser")
        target_lists = content.find(class_="pictxt").find_all("li")
        results = []
        for item in target_lists:
            # print(item.a['href'])
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
