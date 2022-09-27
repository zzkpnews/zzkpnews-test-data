import json
from typing import List
import requests
from lxml import etree

ARTICLE_CONTENT_XPATH = "//html/body/div[@class='main-container']/div[@class='main-content']/div[@class='content-content']"

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

def fix_content_url(content: str):
    return content.replace("/d/file", "https://zzkpnews.com/d/file")

def dump_to_article_file(collection: List):
    for i in collection:
        with open('./articles/{articleId}'.format(articleId=i['id']), "w", encoding='UTF-8') as f:
            f.write(fix_content_url(get_article_content(i['url'])))
    f.close()
    print("写入到文章文件完成！")

def load_article_list()->List:
    data = ''
    with open("data/all-articles-list.json", "r", encoding='UTF-8') as f:
        data = f.read()
    collection = json.loads(data)
    return collection

if __name__ == "__main__":
    list = load_article_list()
    dump_to_article_file(list)
