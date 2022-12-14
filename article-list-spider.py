import json
import uuid
import time
import jieba
import requests
from lxml import etree
from zhon.hanzi import punctuation
from typing import List
import os
import random

NEWS_TITLES_XPATH = '//li/div[@class="news-item-content"]/h3/a/text()'
NEWS_CITATION_XPATH = '//li/div[@class="news-item-content"]/p/text()'
NEWS_PAGE_URLS_XPATH = '//li/div[@class="news-item-content"]/h3/a/@href'
NEWS_COLS_XPATH = '//li/div[@class="news-info"]/span[@class="news-col"]/text()'
NEWS_TIMES_XPATH = '//li/div[@class="news-info"]/span[@class="news-time"]/text()'
NEWS_IMGS_XPATH = '//li/a/img/@src'

ARTICLE_CONTENT_XPATH = "//html/body/div[@class='main-container']/div[@class='main-content']/div[@class='content-content']"

AJAX_URL = "https://www.zzkpnews.com/e/more/loadmore.php?tid=0&page={pagenum}"

PAGE_COUNT = 86

def remove_punctuation(string: str) -> str:
    result = string
    for i in punctuation:
        result = result.replace(i, '')
    return result.replace(' ', '').replace(' ', '')

def get_creator_id() ->str:
    column_names = ['zzkpnews','prinorange','microsoft','dragonbook','apple','starbucks']
    list_len = len(column_names)-1
    return column_names[random.randint(0, list_len)]

def create_uuids(count: int) -> List[str]:
    result: List[str] = []
    for i in range(0, count):
        result.append(str(uuid.uuid1()).replace('-', ''))
    return result


def get_tags(string: str) -> str:
    return ",".join(jieba.cut_for_search(remove_punctuation(string)))


def get_article_content(url: str) -> str:
    data = requests.get(url)
    data.encoding = "utf-8"
    article_content_tree = etree.HTML(data.text)
    etree.strip_elements(article_content_tree, 'script')
    etree.strip_attributes(article_content_tree, 'word_img')
    article_content_xml = article_content_tree.xpath(
        ARTICLE_CONTENT_XPATH)[0]
    return etree.tostring(
        article_content_xml, encoding="utf-8", pretty_print=True).decode("utf-8")


def fix_url(url: str) -> str:
    if url[0:4] != 'http':
        return 'https://zzkpnews.com' + url
    return url


def get_timestamp(timestr: str) -> str:
    return str(time.mktime(time.strptime(timestr, "%Y-%m-%d %H:%M:%S")).__int__())


def collect_list(urlTemplate: str):
    print('开始抓取文章列表数据')
    collection = []
    for i in range(0, PAGE_COUNT):
        sub_list = requests.get(urlTemplate.format(pagenum=i))
        tree = etree.HTML(sub_list.text)

        titles = tree.xpath(NEWS_TITLES_XPATH)
        page_urls = tree.xpath(NEWS_PAGE_URLS_XPATH)
        columnNames = tree.xpath(NEWS_COLS_XPATH)
        times = tree.xpath(NEWS_TIMES_XPATH)
        citations = tree.xpath(NEWS_CITATION_XPATH)
        imgs = tree.xpath(NEWS_IMGS_XPATH)
        ids = create_uuids(len(titles))

        for j in range(0, len(titles)):
            collection.append({
                "subtitle": None,
                "lead_title": None,
                "item_id": ids[j],
                "title": titles[j],
                "url": fix_url(page_urls[j]),
                "citation": citations[j],
                "column_title": columnNames[j],
                "keywords": get_tags(titles[j]),
                "time": get_timestamp(times[j]),
                "bgimg":  fix_url(imgs[j]),
                "author": "中原科技网旧站整理",
                'creator_id':get_creator_id(),
            })
    print('文章列表抓取完成')
    return collection

def dump_to_json_file(collection: List, path: str):
    with open(path, "w", encoding='UTF-8') as f:
        if(json.dump(collection, f, indent=2, sort_keys=True, ensure_ascii=False) != None):
            f.write(json.dump(collection, f, indent=2,
                    sort_keys=True, ensure_ascii=False))
    f.close()
    print("写入到JSON完成！")


if __name__ == "__main__":
    data = collect_list(AJAX_URL)
    if not os.path.isdir("./data"):
        os.makedirs("./data")
    dump_to_json_file(data, "./data/all-articles-list.json")
