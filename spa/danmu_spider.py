# -*- coding：utf-8 -*-
import re
import requests
import time
import random
from multiprocessing import Pool
import sys
import jieba

def LoadUserAgent(uafile):
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1])
    random.shuffle(uas)
    return uas

uas = LoadUserAgent("txt_file/user_agents.txt")


def LoadProxies(uafile):
    ips = []
    with open(uafile, 'r') as proxies:
        for ip in proxies.readlines():
            if ip:
                ips.append(ip.strip())
    random.shuffle(ips)
    return ips

ips = LoadProxies("txt_file/proxies.txt")

# def LoadCookies(cookiefile):
#     cks=[]
#     with open(cookiefile,'r') as cookies:
#         for ck in cookies.readlines():
#             if ck:
#                 cks.append(ck.strip())
#     random.shuffle(cks)
#     return cks
#
# cks=LoadCookies("txt_file/cookies.txt")

def getHtmlInfo(url):
    ua = random.choice(uas)
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'www.bilibili.com',
        'Origin': 'https://www.bilibili.com',
        'User-Agent': ua
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        html = response.text
        #记录视频av号
        aid = url.rpartition('av')[2]

        # 正则表达式找出弹幕文件的cid
        chat_id = re.findall('"cid":(.*?),"page":\d,"from":"vupload"', html)[0]
        print(chat_id)
        # danmuku_url='https://api.bilibili.com/x/v2/dm/history/index?type=1&oid=???&month=2018-05'
        headers['Host'] = 'comment.bilibili.com'
        headers['Origin'] = 'https://www.bilibili.com'

        danmuku_url = 'https://comment.bilibili.com/'+chat_id+'.xml'
        html = requests.get(danmuku_url, headers=headers, timeout=20)
        html.encoding = 'utf-8'
        #正则表达式匹配弹幕文本
        danmuku_text_list=re.findall('">([^\[].*?)</d>', html.text)
        print(danmuku_text_list)

        with open('danmuku_text/av'+aid+'_danmu_text.txt', 'w+', encoding='utf-8') as f:
            for item in danmuku_text_list:
                f.write(item+'\n')
        time.sleep(5)
    except:
        print("Unexpected Error:"+sys.exc_info())
        time.sleep(5)



def danmuku_text_spider():
    #存放各分区前十视频av号的list
    # av_list = []
    # filename = 'txt_file/guichuAV.txt'
    # with open(filename) as file:
    #     for line in file:
    #         av_list.append(line.split('\n')[0])
    # print(av_list)

    av_list = [24757971]
    pool = Pool()
    urls = ['https://www.bilibili.com/video/av{}'.format(i) for i in av_list]
    pool.map(getHtmlInfo, urls)
    # 将统计信息写入json文件
    pool.close()
    pool.join()

def jiebaClear():
    with open('danmuku_text/av24757971_danmu_text.txt','r',encoding='utf-8') as f1:
        for line in f1.readlines():
            wordlist = []
            seg_list = jieba.cut(line, cut_all=False)
            with open('danmuku_text/av24757971_corpus.txt','a+',encoding='utf-8') as f3:
                f3.write(' '.join(seg_list))


if __name__ == '__main__':
    danmuku_text_spider()
    jiebaClear()
