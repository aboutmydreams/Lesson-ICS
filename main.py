# coding: utf8
from icalendar import Calendar, Event
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup as bs
import json
import re
import time
import requests
import uuid
import cut

# 设定时区
tz_utc_8 = timezone(timedelta(hours=8))

time_dict = {
    0: [(7, 50), (9, 25)],
    1: [(9, 45), (12, 10)],
    2: [(13, 50), (15, 25)],
    3: [(15, 45), (18, 10)],
    4: [(19, 00), (21, 25)],
}
split_string = '---------------------'


begin_year = 2019
begin_month = 2
begin_day = 25
# begin_date = datetime(begin_year, begin_month, begin_day)
# begin_date = datetime(2019, 2, 25)


def cread_event(lesson_name, classroom, teacher, start, end, freq=None):
    # 创建事件/日程
    event = Event()
    event.add('summary', lesson_name)

    dt_now = datetime.now(tz=tz_utc_8)
    event.add('dtstart', start)
    event.add('dtend', end)
    # 创建时间
    event.add('dtstamp', dt_now)
    event.add('LOCATION', classroom)
    event.add('DESCRIPTION', '教师：' + teacher)

    # UID保证唯一
    event['uid'] = str(uuid.uuid1()) + '/wnma3mz@gmail.com'
    if freq:
        event.add('rrule', freq)
    # event.add('priority', 5)
    return event


def init_event(count, begin_week, lesson, freq=None):
    # 学期开始的第一个礼拜每天的日期
    begin_date = datetime(begin_year, begin_month,
                          begin_day) + timedelta(days=count)
    # 课程名字，教师，教室
    name, teacher, cls_room = lesson['name'], lesson['teacher'], lesson['cls_room']
    # 课程开始时间(s1小时，s2分钟)，课程结束时间(e1小时，e2分钟)
    s1, s2 = time_dict[lesson['time']][0]
    e1, e2 = time_dict[lesson['time']][1]

    # 课程第一次上课的日期
    delta = timedelta(days=(int(begin_week) - 1) * 7)
    new_date = begin_date + delta
    # 课程第一次上课的年月日
    new_year, new_month, new_day = new_date.year, new_date.month, new_date.day

    # 课程开始时间和结束时间
    start = datetime(new_year, new_month, new_day,
                     s1, s2, 0, tzinfo=tz_utc_8)
    end = datetime(new_year, new_month, new_day,
                   e1, e2, 0, tzinfo=tz_utc_8)

    # 如果上课时间是规律的，则使用rrule重复创建事件；否则，每次上课创建一次
    if freq:
        cal.add_component(cread_event(
            name, cls_room, teacher, start, end, freq))
    else:
        cal.add_component(cread_event(
            name, cls_room, teacher, start, end))


def get_week_lst(lesson):
    # 获取不规律课程的上课周数，一般是处理单双周字符串和只有单个数字的情况
    week_lst = []
    for item in lesson['week'].split(','):
        if '-' not in item:
            if item:
                week_lst.append(item)
        else:
            week1, week2 = item.split('-')
            for i in range(int(week1), int(week2) + 1):
                week_lst.append(i)
    return week_lst


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
    if '(单周)' in tmp_week:
        tmp_week = tmp_week.replace('(单周)', '')
        start, end = tmp_week.split('-')
        tmp_string = ''
        for i in range(int(start), int(end) + 1):
            if i % 2 == 1:
                tmp_string += str(i) + ','

        tmp_week = tmp_string

    return tmp_week


def get_table(cookie):
    # 获取教务管理系统的table
    url = 'http://jwc104.ncu.edu.cn:8081/jsxsd/xskb/xskb_list.do'

    headers = {
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
    }

    html = requests.get(url, headers=headers).text

    soup = bs(html, 'lxml')
    table = soup.find_all('table')[-1]

    tr_lst = table.find_all('tr')
    columns, data = tr_lst[0], tr_lst[1:-1]

    return data


def insert_json(td, i):
    # 需要插入json的数据

    # 取出每个单元格中的内容
    td_tmp = td.find(class_="kbcontent")

    # 因为每个单元格内容的课程信息不一定只有一条，所以用list保存各种信息
    names = td_tmp.text.split(split_string)

    weeks = td_tmp.find_all(title="周次(节次)")
    teachers = td_tmp.find_all(title="老师")
    # 教室不一定有值，需要额外判断
    if td_tmp.find(title="教室"):
        cls_rooms = td_tmp.find_all(title="教室")
    else:
        cls_rooms = ['' for _ in range(len(weeks))]

    tmp_lst = []

    for name, week, teacher, cls_room in zip(names, weeks, teachers, cls_rooms):
        # 将name中多余的信息去掉
        if cls_room:
            name = name.replace(cls_room.text, '')
        name = name.replace(week.text, '')
        name = name.replace(teacher.text, '')

        lesson_dict = {
            'name': name,
            'teacher': teacher.text,
            'week': deal_week(week.text),
            'cls_room': cls_room.text if cls_room else '',
            'time': i  # 0: 0102, 1: 030405, 2: 0607, 3: 080910, 4:111213
        }

        tmp_lst.append(lesson_dict)

    return tmp_lst


def get_lessons(cookie, f_json):
    # 获取cls_json
    data = get_table(cookie)
    cls_json = {}

    for i, line in enumerate(data):
        tds = line.find_all('td')
        for col, td in zip(['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'], tds):
            if col not in cls_json.keys():
                cls_json[col] = []
            if td.find(class_="kbcontent").find(title="周次(节次)"):
                tmp_lst = insert_json(td, i)
                cls_json[col] += tmp_lst

    with open(f_json, 'w') as f:
        json.dump(cls_json, f)

    return cls_json


if __name__ == '__main__':
    fname = 'cls2'
    f_json = '{}.json'.format(fname)
    # 你的 cookie 或用户名密码
    cookie = cut.get_cookie(username,password)
    # 发起网络请求
    cls_json = get_lessons(cookie, f_json)

    # 如果本地有文件，可以用来测试
    # with open(f_json, 'r') as f:
    # cls_json = json.load(f)

    cal = Calendar()
    cal.add('prodid', '-//JH-L//JH-L Calendar//')
    cal.add('version', '2.0')

    count = 0
    for key, value in cls_json.items():
        for lesson in value:
            if re.search(r'^\w+-\w+$', lesson['week']):
                begin_week, end_week = lesson['week'].split('-')
                freq = {'freq': 'weekly', 'count': int(
                    end_week) - int(begin_week) + 1}
                init_event(count, begin_week, lesson, freq)
            else:
                week_lst = get_week_lst(lesson)
                for week in week_lst:
                    init_event(count, week, lesson)
        count += 1

    with open('{}.ics'.format(fname), 'wb') as f:
        f.write(cal.to_ical())
