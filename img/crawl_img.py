#!/usr/bin/env python
# -*- coding: utf-8 -*-
# file name :'crawl_img.py'
# created on:'2018/12/8'
__author__ = 'turbobin'

from bs4 import BeautifulSoup
import requests
from lxml import etree
import pdfkit
import os


def parse_url(url):
    header = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
    }
    response = requests.get(url, headers=header)
    return response.content


def get_url_list(url):
    response = parse_url(url)
    soup = BeautifulSoup(response, 'html.parser')
    urls = []
    for li in soup.find_all(class_="toctree-l1"):
        href = url + li.a.get("href")
        urls.append(href)

    # print(urls)
    return urls


def get_img(url):
    print('正在请求:', url)
    response = parse_url(url)
    soup = BeautifulSoup(response, 'html.parser')
    body = soup.find_all(class_="body")[0]  # 获取内容体
    # sections = body.find_all('div', {'class': 'section'}, recursive=False)
    # 将图片链接补全
    # print(body)
    # body = body.replace('../_images/', 'https://pythonguidecn.readthedocs.io/zh/latest/_images/')
    imgs = body.find_all('img')
    for img in imgs:
        img_src = img.get('src').replace('../_images/', 'https://pythonguidecn.readthedocs.io/zh/latest/_images/')
        img_name = img_src.split('/')[-1]
        content = parse_url(img_src)
        with open(img_name, 'wb') as f:
            f.write(content)
            print('已下载：', img_name)


def main():
    url = 'https://pythonguidecn.readthedocs.io/zh/latest/'
    url_list = get_url_list(url)
    # 其中有一个url请求的是相同的页面，将它剔除
    repeat_url = 'https://pythonguidecn.readthedocs.io/zh/latest/dev/virtualenvs.html#virtualenv'
    url_list = list(filter(lambda x: x != repeat_url, url_list))
    print('urls:', len(url_list))
    for url in url_list:
        get_img(url)


if __name__ == '__main__':
    main()