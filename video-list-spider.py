import json
import uuid
import time
import jieba
import requests
from lxml import etree
from zhon.hanzi import punctuation
from typing import List
import random
import os

PAGENUM = 800

url = 'http://channel.chinanews.com.cn/video/cns/vcl/sh.shtml?&pager=1&pagenum={page_num}&t=11_6'.format(
    page_num=PAGENUM)


def get_column_name() -> str:
    column_names = ['科技', '要闻', '自然', '社会', '生命', '安全', '学术', '文化',
                    '教育', '融创', '美学', '乡村', '企业', '纪实', '摄影', '推介', '科普']
    list_len = len(column_names)-1
    return column_names[random.randint(0, list_len)]


def create_uuid() -> str:
    return (str(uuid.uuid1()).replace('-', ''))

def get_creator_id() ->str:
    column_names = ['zzkpnews','prinorange','microsoft','dragonbook','apple','starbucks']
    list_len = len(column_names)-1
    return column_names[random.randint(0, list_len)]

def remove_punctuation(string: str) -> str:
    result = string
    for i in punctuation:
        result = result.replace(i, '')
    return result.replace(' ', '').replace(' ', '')


def get_tags(string: str) -> str:
    return ",".join(jieba.cut_for_search(remove_punctuation(string)))


def fix_time(timestr: str) -> str:
    return str(time.mktime(time.strptime(timestr, "%Y-%m-%d %H:%M:%S")).__int__())


def fix_rawdata(string: str) -> str:
    return string.replace('\n', '').replace('\r', '').replace(
        ';newslist = specialcnsdata;', '').replace('specialcnsdata =', '')


def get_video_url(url: str):
    content = requests.get(url).text
    startStr = 'so.addVariable("vInfo", "'
    endStr = '")'
    startIndex = content.index(startStr)
    if startIndex >= 0:
        startIndex += len(startStr)
    endIndex = content.index(endStr, startIndex)
    return content[startIndex:endIndex]

def collect_list():
    collected_list = []
    rawdata_list = json.loads(fix_rawdata(requests.get(url).text))['docs']
    print('开始抓取视频列表数据')
    for i in rawdata_list:
        collected_list.append({
            "subtitle": None,
            "lead_title": None,
            "item_id": create_uuid(),
            "title": i['title'],
            "url": i['url'],
            "citation": i['content'],
            "column_title": get_column_name(),
            "keywords": get_tags(i['title']),
            "time": fix_time(i['pubtime']),
            "bgimg":  i['img_cns'],
            "author": "中国新闻网视频站",
            "video_url": get_video_url(i['url']),
            'creator_id':get_creator_id(),
        })
    print('视频列表数据抓取完成')
    return collected_list

def dump_to_json_file(collection, path):
    with open(path, "w", encoding='UTF-8') as f:
        if(json.dump(collection, f, indent=2, sort_keys=True, ensure_ascii=False) != None):
            f.write(json.dump(collection, f, indent=2,
                    sort_keys=True, ensure_ascii=False))
    print("写入完成！")


if __name__ == "__main__":
    if not os.path.isdir("./data"):
        os.makedirs("./data")
    list = collect_list()
    dump_to_json_file(list, './data/all-videos-list.json')
