# -*- coding : utf-8 -*-
import re
import requests
from bs4 import BeautifulSoup

root_url = 'http://www.gamersky.com'


def fetch_list(mark=None, page=None):
    if not mark:
        target_url = root_url + '/ent/111/'
    else:
        target_url = root_url + '/ent/' + mark + '/'
    if page:
        target_url = target_url + page
    print("fecth: {}".format(target_url))
    response = requests.get(target_url).text
    content = BeautifulSoup(response, 'html.parser')
    target_list = content.find(class_="pictxt").find_all("li")
    results = [{
        'thumbnail': item.img['src'],
        'title': item.a['title'],
        'link': item.a['href']
    } for item in target_list]
    try:
        pre = content.find(class_='p1 previous')['href']
    except TypeError:
        pre = None
    try:
        nexe = content.find(class_='p1 nexe')['href']
    except TypeError:
        nexe = None
    return results, pre, nexe


def fetch_photo(key, page=None):
    target_url = root_url + '/ent/' + key
    if page:
        target_url = target_url + '_' + str(page) + '.shtml'
    else:
        target_url += '.shtml'
    print(target_url)
    response = requests.get(target_url)
    response.encoding = 'utf-8'
    response = response.text
    patt_next = re.compile(u'<a href="http://www.gamersky.com/ent/' + key + '_(?P<page>\d+)\.shtml">下', re.S)
    try:
        nexe = patt_next.search(response).group('page')
    except AttributeError:
        nexe = None
    patt_img = re.compile('<p.*?center">.*?<img.*?src="(.*?)".*?>', re.S)
    results = re.findall(patt_img, response)
    if len(results) == 0:
        print("fecth error from url: {}".format(target_url))
    return results, nexe
