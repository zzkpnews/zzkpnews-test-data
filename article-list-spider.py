import json
import uuid
import time
import jieba
import requests
from lxml import etree
from zhon.hanzi import punctuation
from typing import List
import pymysql

NEWS_TITLES_XPATH = '//li/div[@class="news-item-content"]/h3/a/text()'
NEWS_CITATION_XPATH = '//li/div[@class="news-item-content"]/p/text()'
NEWS_PAGE_URLS_XPATH = '//li/div[@class="news-item-content"]/h3/a/@href'
NEWS_COLS_XPATH = '//li/div[@class="news-info"]/span[@class="news-col"]/text()'
NEWS_TIMES_XPATH = '//li/div[@class="news-info"]/span[@class="news-time"]/text()'
NEWS_IMGS_XPATH = '//li/a/img/@src'

ARTICLE_EDITOR_XPATH = "//html/body/div[@class='main-container']/div[@class='main-content']/div[@class='content-info']/span[@class='content-source']/text()"
ARTICLE_CONTENT_XPATH = "//html/body/div[@class='main-container']/div[@class='main-content']/div[@class='content-content']"

ajax_url = "https://www.zzkpnews.com/e/more/loadmore.php?tid=0&page={pagenum}"

sql = """INSERT INTO items(id, bgimg, title,citation, type, postDate)
VALUES ('{id}','{bgimg}','{title}','{citation}','ARTICLE','{postDate}')"""

db = pymysql.connect(host='localhost',
                     user='zzkpnews',
                     password='mysql-zzkpnews',
                     database='zzkpnews_site')

def remove_punctuation(string: str) -> str:
    result = string
    for i in punctuation:
        result = result.replace(i, '')
    return result.replace(' ', '').replace(' ', '')


def create_uuids(count: int) -> List[str]:
    result: List[str] = []
    for i in range(0, count):
        result.append(str(uuid.uuid4()).replace('-', ''))
    return result


def get_tags(string: str) -> str:
    return ",".join(jieba.cut_for_search(remove_punctuation(string)))


def fix_url(url: str) -> str:
    if url[0:4] != 'http':
        return 'https://zzkpnews.com' + url
    return url


def fix_time(timestr: str) -> str:
    return str(time.mktime(time.strptime(timestr, "%Y-%m-%d %H:%M:%S")).__int__())

# 将爬取的数据储存到指定容器中
def collect_list(urlTemplate: str):
    collection = []
    for i in range(0, 86):
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
                "leadTitle": None,
                "id": ids[j],
                "title": titles[j],
                "url": fix_url(page_urls[j]),
                "citation": citations[j],
                "columnName": columnNames[j],
                "keywords": get_tags(titles[j]),
                "time": fix_time(times[j]),
                "bgimg":  fix_url(imgs[j]),
                "author": "中原科技网旧站整理"
            })
    return collection

# 将指定容器中的数据转成json文件并储存到指定位置中
def dump_to_json_file(collection, path):
    with open(path, "w", encoding='UTF-8') as f:
        if(json.dump(collection, f, indent=2, sort_keys=True, ensure_ascii=False) != None):
            f.write(json.dump(collection, f, indent=2,
                    sort_keys=True, ensure_ascii=False))
    print("写入完成！")


def write_in_database(collection):

    return


data = collect_list(ajax_url)
dump_to_json_file(data, "./data/all-articles-list.json")
