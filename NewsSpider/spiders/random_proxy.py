#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import random
import requests
from bs4 import BeautifulSoup
from NewsSpider.spiders.random_agent import RandomAgent

class RandomProxy:
    def __init__(self):
        # print("Proxy crawl ......")
        self.proxy_list = list()
        self.verify_proxy_list = list()
        self.random_agent = RandomAgent()
        # 国内高匿代理IP
        self.proxy_spider("nn")
         # 国内普通代理IP
        self.proxy_spider("nt")
        with open("proxies.txt", "r", encoding="utf-8") as f:
            for line in f.readlines():
                self.proxy_list.append(line.strip())

        self.verify_proxies()
        with open("proxies.txt", "w", encoding="utf-8") as f:
            for proxy in self.verify_proxy_list:
                f.write(proxy + '\n')
        print("Proxy crawl finished, number of proxy %d" % len(self.verify_proxy_list))

        # with open("proxies.txt", "r", encoding="utf-8") as f:
        #     for line in f.readlines():
        #         self.verify_proxy_list.append(line.strip())

    def proxy_spider(self, top_url):
        page, page_stop = 1, random.randint(20, 50)
        while page < page_stop:
            try:
                url = 'http://www.xicidaili.com/%s/%d' % (top_url, page)
                headers = {"User-Agent": self.random_agent.get_agent()}
                html = requests.get(url, headers=headers)
                soup = BeautifulSoup(html.text, "html.parser")
                ip_list = soup.find(id='ip_list')
                for odd in ip_list.find_all(class_='odd'):
                    protocol = odd.find_all('td')[5].get_text().lower() + '://'
                    self.proxy_list.append(protocol + ':'.join([x.get_text() for x in odd.find_all('td')[1:3]]))
            except:
                pass
            page += 1

    def verify_proxies(self):
        for proxy in self.proxy_list:
            if self.verify_proxy(proxy):
                self.verify_proxy_list.append(proxy)


    def verify_proxy(self, proxy):
        protocol = 'https' if 'https' in proxy else 'http'
        proxies = {protocol: proxy}
        try:
            if requests.get('http://www.baidu.com', proxies=proxies, timeout=2).status_code == 200:
                return True
        except:
            return False
        return False

    def get_proxy(self):
        proxy = random.choice(self.verify_proxy_list)
        while not self.verify_proxy(proxy):
            proxy = random.choice(self.verify_proxy_list)
        return proxy
