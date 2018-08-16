import re

import requests
from requests.packages.urllib3.packages.six.moves.urllib.parse import urlencode

from config import *


def get_page_list(offset, keyword):
    # 1 列表页面
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '3',
        'from': 'gallery'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None


def parse_page_list(json):
    data = json.get('data')
    if data:
        for item in data:
            article_url = item.get('article_url')
            url = re.sub('group/', 'a', article_url)
            title = item.get('title')
            yield {
                'title': title,
                'url': url
            }


def save_image(item):
    pass


def main():
    json = get_page_list(0, KEYWORDS)
    for item in parse_page_list(json):
        download_image()
        print(item)
        save_image(item)


if __name__ == '__main__':
    main()
