#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import json
import scrapy
import urllib.parse
import urllib.request
from NewsSpider.items import NewsspiderItem
from NewsSpider.spiders.extract_news import *

class NewsSpider(scrapy.Spider):
    name = 'news_spider'
    def __init__(self, keyword):
        self.keyword = keyword
        self.parser = NewsParser()

    '''获取百度新闻列表'''
    def collect_baidu_newslist(self, html):
        selector = etree.HTML(html, parser=etree.HTMLParser(encoding='utf-8'))
        urls = selector.xpath('//h3[@class="c-title"]/a/@href')
        return set(urls)

    '''获取搜狗新闻列表'''
    def collect_sogou_newslist(self, html):
        selector = etree.HTML(html, parser=etree.HTMLParser(encoding='utf-8'))
        urls = selector.xpath('//h3[@class="vrTitle"]/a/@href')
        return set(urls)

    '''获取新浪新闻列表'''
    def collect_sina_newslist(self, html):
        selector = etree.HTML(html, parser=etree.HTMLParser(encoding='utf-8'))
        urls = selector.xpath('//div[@class="r-info r-info2"]/h2/a/@href')
        return set(urls)

    '''获取360新闻列表'''
    def collect_360_newslist(self, html):
        selector = etree.HTML(html, parser=etree.HTMLParser(encoding='utf-8'))
        urls = selector.xpath('//a[@class="news_title"]/@href')
        return set(urls)

    '''获取新华社新闻列表'''
    def collect_xinhuashe_newslist(self, html):
        data = json.loads(html)
        try:
            results = data["content"]["results"]
            if results != None:
                urls = [result["url"] for result in results]
                return set(urls)
        except:
            pass
        return []

    '''采集主函数'''
    def start_requests(self):
        word = urllib.parse.quote_plus(self.keyword)
        news_list_links = list()
        # 百度新闻
        for page_num in range(0, 800, 20):
            url = 'http://news.baidu.com/ns?word=intitle%3A%28' + word + '%29&pn=' + str(
                page_num) + '&cl=2&ct=1&tn=newstitle&rn=20&ie=utf-8&bt=0&et=0'
            news_list_links.append(url)
        # 搜狗新闻
        for page_num in range(0, 100):
            url = 'https://news.sogou.com/news?mode=2&manual=&query=' + word + '&time=0&sort=0&page=' + str(
                page_num) + '&w=03009900&dr=1&_asf=news.sogou.com&_ast=1553047168'
            news_list_links.append(url)
        # 新浪新闻
        for page_num in range(0, 100):
            url = 'https://search.sina.com.cn/?q=' + word + '&range=title&c=news&sort=time&col=&source=&from=&country=&size=&time=&a=&page=' + str(
                page_num) + '&pf=2131490991&ps=2134309112&dpc=1'
            news_list_links.append(url)
        # 360新闻
        for page_num in range(0, 100):
            url = 'https://news.so.com/ns?q=' + word + '&pn=' + str(
                page_num) + '&tn=newstitle&rank=rank&j=0&nso=0&tp=2&nc=0&src=page'
            news_list_links.append(url)
        # 新华社搜索新闻
        for page_num in range(0, 100):
            url = 'http://search.news.cn/getNews?keyword=' + word + '&curPage=' + str(
                page_num) + '&sortField=0&searchFields=1&lang=cn'
            news_list_links.append(url)

        news_list_links = list(set(news_list_links))
        for news_link in news_list_links:
            try:
                param = ""
                if "news.baidu.com" in news_link:
                    param = {'url': news_link, 'host': 'baidu'}
                # 搜狗新闻
                elif "news.sogou.com" in news_link:
                    param = {'url': news_link, 'host': 'sogou'}
                # 新浪新闻
                elif "search.sina.com.cn" in news_link:
                    param = {'url': news_link, 'host': 'sina'}
                # 360新闻
                elif "news.so.com" in news_link:
                    param = {'url': news_link, 'host': '360'}
                # 新华社搜索新闻
                elif "search.news.cn" in news_link:
                    param = {'url': news_link, 'host': 'xinhuashe'}
                yield scrapy.Request(url=news_link, meta=param, callback=self.get_news_list, dont_filter=True)
            except:
                pass

    def get_news_list(self, response):
        host = response.meta['host']
        news_links = list()
        # 百度新闻
        if host == "baidu":
            news_links += self.collect_baidu_newslist(response.text)
        # 搜狗新闻
        elif host == "sogou":
            news_links += self.collect_sogou_newslist(response.text)
        # 新浪新闻
        elif host == "sina":
            news_links += self.collect_sina_newslist(response.text)
        # 360新闻
        elif host == "360":
            news_links += self.collect_360_newslist(response.text)
        # 新华社搜索新闻
        elif host == "xinhuashe":
            news_links += self.collect_xinhuashe_newslist(response.text)

        news_links = list(set(news_links))
        for news_link in news_links:
            try:
                param = {'url': news_link}
                yield scrapy.Request(url=news_link, meta=param, callback=self.page_parser, dont_filter=True)
            except:
                pass


    '''对网站新闻进行结构化抽取'''
    def page_parser(self, response):
        data = self.parser.extract_news(response.text)
        if data:
            item = NewsspiderItem()
            item['keyword'] = self.keyword
            item['news_url'] = response.meta['url']
            item['news_time'] = data['news_pubtime']
            item['news_date'] = data['news_date']
            item['news_title'] = data['news_title']
            item['news_content'] = data['news_content']
            yield item
        return
