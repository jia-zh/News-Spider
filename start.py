#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
from scrapy import cmdline

event_list = ['中美贸易', '美朝会谈','红黄蓝幼儿园虐童']
project_name = 'news_spider'
for event in event_list:
    # print("scrapy crawl {0} ......".format(event))
    os.system("scrapy crawl {0} -a keyword={1}".format(project_name, event))
    # cmdline.execute("scrapy crawl {0} -a keyword={1}".format(project_name, event).split())
