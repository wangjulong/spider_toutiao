import json
import os
import re
from multiprocessing.pool import Pool

import requests
from urllib.parse import urlencode
from requests.exceptions import RequestException
from hashlib import md5
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


def get_page_detail(url):
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.text
    except RequestException:
        print(">>> 获取具体的页面内容失败：", url)


def parse_json_detail(html):
    image_pattern = re.compile(r'gallery: JSON.parse(.*?)siblingList', re.S)
    result = re.search(image_pattern, html)
    if result:
        content = result.group(1)
        content = content.strip()
        content = content.strip('"(),')
        content = content.replace(r'\"', '"')
        json_data = json.loads(content)
        arr = json_data.get('sub_images')
        if arr:
            images_address = [x.get('url').replace('\\', '') for x in arr]
            return images_address
        else:
            print(">>> Parse image address FAILED！！！！！")
    else:
        print(">>> Parse gallery FAILED！！！！！")
    return False


def save_image(path_name, image_content):
    save_dir = os.path.join(HOME_DIR, path_name)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    file_path = '{0}/{1}.{2}'.format(save_dir, md5(image_content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as file:
            file.write(image_content)
            print(">>> image has been saved: ", file_path)
    else:
        print(">>> 文件已存在：", file_path)


def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(">>> Download Image SUCCESSFUL：", url)
            return response.content
        print(">>> Download Image FAILED：", url)
    except RequestException:
        print(">>> Download Image FAILED：", url)
        return None


def main(offset):
    # 1 传入偏移量和关键词，获取搜索结果的 json 数据
    json = get_page_list(offset, KEYWORDS)

    # 2 循环 json 数据中的每一条记录（title, url），对应每一个网页标题和网页地址
    for item in parse_page_list(json):
        # 3 获取具体的网页内容
        html = get_page_detail(item.get('url'))

        # 4 从网页内容中提取图片的地址
        image_list = parse_json_detail(html)

        for image_address in image_list:
            image_content = download_image(image_address)
            save_image(item.get('title'), image_content)


if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
