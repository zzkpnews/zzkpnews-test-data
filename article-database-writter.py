import json
from typing import List

column_names_set = set()

def load_article_list()->List:
    data = ''
    with open("data/all-articles-list.json", "r", encoding='UTF-8') as f:
        data = f.read()
    collection = json.loads(data)
    return collection

list = load_article_list()

for i in list :
    column_names_set.add(i['columnName'])

print(column_names_set)
