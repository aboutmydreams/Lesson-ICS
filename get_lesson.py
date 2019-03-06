# coding: utf8

import requests
from bs4 import BeautifulSoup as bs
import re
import json


def deal_week(tmp_week):
    if '(周)' in tmp_week:
        tmp_week = tmp_week.replace('(周)', '')
    if '(双周)' in tmp_week:
        tmp_week = tmp_week.replace('(双周)', '')
        start, end = tmp_week.split('-')
        tmp_string = ''
        for i in range(int(start), int(end) + 1):
            if i % 2 == 0:
                tmp_string += str(i) + ','

        tmp_week = tmp_string

    return tmp_week


url = 'http://jwc104.ncu.edu.cn:8081/jsxsd/xskb/xskb_list.do'
cookie = cookie


headers = {
    'Cookie': cookie,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
}

html = requests.get(url, headers=headers).text

soup = bs(html, 'lxml')
table = soup.find_all('table')[-1]

tr_lst = table.find_all('tr')
columns, data = tr_lst[0], tr_lst[1:-1]

cls_json = {}

split_string = '---------------------'

for i, line in enumerate(data):
    tds = line.find_all('td')
    line_lst = [line.find('th')]
    for col, td in zip(['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'], tds):
        if col not in cls_json.keys():
            cls_json[col] = []

        if td.find(class_="kbcontent").find(title="周次(节次)"):

            td_tmp = td.find(class_="kbcontent")
            names = td_tmp.text.split(split_string)

            weeks = td_tmp.find_all(title="周次(节次)")
            teachers = td_tmp.find_all(title="老师")
            if td_tmp.find(title="教室"):
                cls_rooms = td_tmp.find_all(title="教室")
            else:
                cls_rooms = ['' for _ in range(len(weeks))]

            for name, week, teacher, cls_room in zip(names, weeks, teachers, cls_rooms):
                if cls_room:
                    name = name.replace(cls_room.text, '')
                name = name.replace(week.text, '')
                name = name.replace(teacher.text, '')

                cls_json[col].append({
                    'name': name,
                    'teacher': teacher.text,
                    'week': deal_week(week.text),
                    'cls_room': cls_room.text if cls_room else '',
                    'time': i  # 0: 0102, 1: 030405, 2: 0607, 3: 080910, 4:111213
                })

with open('cls2.json', 'w') as f:
    json.dump(cls_json, f)
