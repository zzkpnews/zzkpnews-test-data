import json
import uuid
import time
import jieba
import requests
from lxml import etree
from zhon.hanzi import punctuation
from typing import List
import random
import pymysql

# http://channel.chinanews.com.cn/video/cns/vcl/sh.shtml?&pager=7&pagenum=3&t=11_6

url = 'http://channel.chinanews.com.cn/video/cns/vcl/sh.shtml?&pager=1&pagenum=800&t=11_6'


def get_column_name() -> str:
    column_names = ['科技', '要闻', '自然', '社会', '生命', '安全', '学术', '文化',
                    '教育', '融创', '美学', '乡村', '时尚', '企业', '纪实', '摄影', '推介', '科普']
    list_len = len(column_names)-1
    return column_names[random.randint(0, list_len)]


def create_uuid() -> str:
    return (str(uuid.uuid4()).replace('-', ''))

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

def get_video_url(url:str):
    content = requests.get(url).text
    startStr = 'so.addVariable("vInfo", "'
    endStr = '")'
    startIndex = content.index(startStr)
    if startIndex >= 0:
        startIndex += len(startStr)
    endIndex = content.index(endStr,startIndex)
    return content[startIndex:endIndex]


rawdata_list = json.loads(fix_rawdata(requests.get(url).text))['docs']

collected_list = []

for i in rawdata_list:
    print(i['url'])
    collected_list.append({
        "subtitle": None,
        "leadTitle": None,
        "id": create_uuid(),
        "title": i['title'],
        "url": i['url'],
        "citation": i['content'],
        "columnName": get_column_name(),
        "keywords": get_tags(i['title']),
        "time": fix_time(i['pubtime']),
        "bgimg":  i['img_cns'],
        "author": "中国新闻网视频站",
        "videoUrl":get_video_url(i['url'])
    })


def dump_to_json_file(collection, path):
    with open(path, "w", encoding='UTF-8') as f:
        if(json.dump(collection, f, indent=2, sort_keys=True, ensure_ascii=False) != None):
            f.write(json.dump(collection, f, indent=2,
                    sort_keys=True, ensure_ascii=False))
    print("写入完成！")


dump_to_json_file(collected_list, './data/all-videos-list.json')
