# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import re

class NewsspiderPipeline(object):
    def __init__(self):
        root_path = '/'.join(os.path.abspath(__file__).split('/')[:-2])
        self.news_path = os.path.join(root_path, 'news')
        if not os.path.exists(self.news_path):
            os.makedirs(self.news_path)
        self.rep = {'<':'', '>':'', '/':'', '\\':'', '|':'', ':':'', '"':'', '*':'', '?':'', ' ':'', '-':'', '\n':'','\r':''}
        self.rep = dict((re.escape(k), v) for k, v in self.rep.items())
        self.pattern = re.compile("|".join(self.rep.keys()))

    '''处理数据流'''
    def process_item(self, item, spider):
        keyword = item['keyword']
        event_path = os.path.join(self.news_path, keyword)
        if not os.path.exists(event_path):
            os.makedirs(event_path)
        filename = os.path.join(event_path,
                                self.pattern.sub(lambda m: self.rep[re.escape(m.group(0))], item['news_time'])[0:12] + '＠' +
                                self.pattern.sub(lambda m: self.rep[re.escape(m.group(0))], item['news_title']))
        if len(filename) > 200:
            filename = filename[0:200] + "..."

        with open(filename, "w", encoding="utf-8") as f:
            f.write("标题:{0}\n".format(item['news_title']))
            f.write("URL:{0}\n".format(item['news_url']))
            f.write("发布时间:{0}\n".format(item['news_time']))
            f.write("正文:{0}\n".format(item['news_content']))
        f.close()

