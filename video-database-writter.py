import json
from typing import List
import uuid
import pymysql

db = pymysql.connect(host='localhost',
                     user='zzkpnews',
                     password='zzkpnews',
                     database='zzkpnews_test')

cursor = db.cursor()

column_id_map = {
    '摄影': 'photography',
    '乡村': 'rural',
    '美学': 'aesthetics',
    '学术': 'academic',
    '科普': 'science',
    '科技': 'technology',
    '社会': 'social',
    '教育': 'education',
    '要闻': 'brief',
    '安全': 'security',
    '文化': 'culture',
    '生命': 'live',
    '企业': 'enterprise',
    '自然': 'nature',
    '纪实': 'documentary',
    '推介': 'recommendation',
    '融创': 'sunac',
    '其他': 'other',
}

sql_insert_to_newsitem = """INSERT INTO news_items(news_type,news_id, creator_id, column_id, timestamp, title, citation, bgimg, keywords)
VALUES ('video','{item_id}','{creator_id}','{column_id}','{item_timestamp}','{item_title}','{item_citation}','{item_bgimg}','{item_keywords}')"""


sql_insert_to_videos = """INSERT INTO videos(video_id, author, video_url, origin, origin_url) VALUES ('{video_id}','{author}','{video_url}','中国新闻网视频站','{origin_url}')"""


def load_video_list() -> List:
    data = ''
    with open("data/all-videos-list.json", "r", encoding='UTF-8') as f:
        data = f.read()
    collection = json.loads(data)
    return collection


list = load_video_list()

try:
    for item in list:
        cursor.execute(sql_insert_to_newsitem.format(
            item_id=item['item_id'], creator_id=item['creator_id'],item_timestamp=item['time'], item_title=item['title'],column_id=column_id_map[item['column_title']],
            item_citation=item['citation'], item_bgimg=item['bgimg'], item_keywords=item['keywords']),
        )
    db.commit()
except Exception as e:
    print(e)
    db.rollback()


try:
    for item in list:
        cursor.execute(sql_insert_to_videos.format(
            video_id=item['item_id'], author=item['author'],video_url=item['video_url'], origin_url=item['url']))
    db.commit()
except Exception as e:
    print('ee')
    print(e)
    db.rollback()


db.close()
print('录入成功')
