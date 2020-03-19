
#下载targetuser的关注者名单


import requests
import json
import time
import re
import sys
import datetime
import pandas as pd

from threading import Thread
import numpy as np
import threading

targetuser = 'excited-vczh'
save_location = targetuser + '(fellower).csv'
def main():
    url = creat_url(targetuser,str(31340))
    thread_main(url)



    


def thread_main(url):
    response = get_data(url)
    if(response == 410):
        return 1
    comments,is_end = parse_data(response)
    save_data(comments)
    while(is_end == False):
        next_url = json.loads(response.text)['paging']['next']
        response = get_data(next_url)
        comments,is_end = parse_data(response)
        save_data(comments)
    return 0





def parse_data(response):
    is_end = json.loads(response.text)['paging']['is_end']
    data = json.loads(response.text)['data']
    comments = []
    try:
        for user in data:
            comment = []
            comment.append(user['url_token']) #用户id
            comments.append(comment) 
        return comments, is_end
                
    except IndexError:
        pass



def save_data(comments):
    filename = save_location
    dataframe = pd.DataFrame(comments)
    dataframe.to_csv(filename, index=False, header=False, sep=',', mode='a', encoding="utf_8_sig" ) # encoding="utf_8_sig",
    #dataframe.to_csv(filename, mode='a', index=False, sep=',', header=['name','gender','user_url','voteup','cmt_count','url'])
    

def creat_url(url_token, offset):
    url = ('https://www.zhihu.com/api/v4/members/' + url_token+ '/followers?&offset='+ offset +'&limit=20')
    return url


def get_data(url):
    print(url)
    return get_data_cookie(url)
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    response = requests.get(url, headers=headers, timeout=90)
    while(response.status_code == 200):
        return response
    print('Error！')
    print(url)
    print(response.status_code)
    if (response.status_code == 443):
        time.sleep(600)
        return get_data(url)
    if (response.status_code == 410):
        return 410
    return get_data_cookie(url)

def get_data_cookie(url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    response = requests.get(url, headers=headers,cookies=cookie, timeout=90)
    while(response.status_code == 200):
        print("use 'get_data_cookie,successful'")
        return response
    for i in range(0,10,1):
        print('Error！')
        print(url)
        print(response.status_code)
        time.sleep(10)
        response = requests.get(url, headers=headers,cookies=cookie, timeout=90)
        if(response.status_code == 200):
            return response
    print("10 times recycle false, cookie may disabled")
    return response











cookie = {
    '__utma': '51854390.780231351.1582628822.1583193203.1583193203.1',
    '__utmv': '51854390.100--|2=registration_date=20160129=1^3=entry_date=20160129=1',
    '__utmz': '51854390.1583193203.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/question/39584012/answer/1051785048',
    '_ga': 'GA1.2.780231351.1582628822',
    '_gid': 'GA1.2.1781748465.1582628822',
    '_xsrf': '8ZZ7pPH5QdhIeoop33sJAYspbVLRsrhi',
    '_zap': 'bf1e84e5-a29f-4aee-8753-7f9865121d3a',
    'd_c0': '"AGBZyRlDxhCPToqgzwgOrdYy9yUvXCkdkVw=|1580963052"',
    'Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49': '1584005239',
    'Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49': '1583997974,1583998363,1583998910,1584002533',
    'KLBRSID': '9d75f80756f65c61b0a50d80b4ca9b13|1584005259|1584002492',
    'q_c1': '12e9f8e64b624afc81c9a76779f36a22|1583632289000|1580964448000',
    'tst': 'f',
    'z_c0': '"2|1:0|10:1580964190|4:z_c0|92:Mi4xU0FtS0FnQUFBQUFBWUZuSkdVUEdFQ1lBQUFCZ0FsVk5YdWNvWHdBNTRnbXkzTllZdy1fY2NOaWxTalYzWmRiRmpR|9eb3c3218aba90820065a3923e010cfd7e126dcc0dff6e8a64615ddfe725a382"'
}