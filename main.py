# coding: utf8
from icalendar import Calendar, Event
from datetime import datetime, timedelta, timezone
import json
import re
import time

tz_utc_8 = timezone(timedelta(hours=8))

ref = """
BEGIN:VCALENDAR
PRODID:-//JH-L//JH-L Calendar //CN
VERSION:2.0
CALSCALE:GREGORIAN \\ 日历类型，阳历
METHOD:PUBLISH
X-WR-CALNAME:课程表
X-WR-TIMEZONE:Asia/Shanghai
X-WR-CALDESC:
BEGIN:VTIMEZONE
TZID:Asia/Shanghai
X-LIC-LOCATION:Asia/Shanghai
BEGIN:STANDARD
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
TZNAME:CST
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
DTSTART;TZID=Asia/Shanghai:20120901T092000
DTEND;TZID=Asia/Shanghai:20120901T105000
DTSTAMP:20120622T160054Z      \\ 创建时间
UID:%u4F20%u70ED%u5B66%20%u5BF9%u6D41%u5B9E%u9A8C35@第 1 次 \\ ID，不重复即可
CREATED:20120622T154824Z
DESCRIPTION:教师：王五n
LAST-MODIFIED:20120622T160041Z
LOCATION:大礼堂
STATUS:CONFIRMED
SUMMARY:实验2
END:VEVENT
END:VCALENDAR
"""


def cread_event(lesson_name, classroom, teacher, start, end, freq=None):
    event = Event()
    event.add('summary', lesson_name)

    dt_now = datetime.now(tz=tz_utc_8)
    event.add('dtstart', start)
    event.add('dtend', end)
    event.add('dtstamp', dt_now)
    event.add('LOCATION', classroom)
    event.add('DESCRIPTION', '教师：' + teacher)

    uid = dt_now.strftime(str(dt_now) + '/wnma3mz@gmail.com')
    event['uid'] = uid
    if freq:
        event.add('rrule', freq)

    # event.add('priority', 5)

    return event


cal = Calendar()
cal.add('prodid', '-//JH-L//JH-L Calendar//')
cal.add('version', '2.0')


with open('cls2.json', 'r') as f:
    cls_json = json.load(f)

time_dict = {
    0: [(7, 50), (9, 25)],
    1: [(9, 45), (12, 10)],
    2: [(13, 50), (15, 25)],
    3: [(15, 45), (18, 10)],
    4: [(19, 00), (21, 25)],
}

begin_year = 2019
begin_month = 2
begin_day = 25
# begin_date = datetime(begin_year, begin_month, begin_day)
# begin_date = datetime(2019, 2, 25)

count = 0
for key, value in cls_json.items():

    for lesson in value:

        name, teacher, cls_room = lesson['name'], lesson['teacher'], lesson['cls_room']
        s1, s2 = time_dict[lesson['time']][0]
        e1, e2 = time_dict[lesson['time']][1]

        if re.search(r'^\w+-\w+$', lesson['week']):
            begin_week, end_week = lesson['week'].split('-')

            begin_date = datetime(begin_year, begin_month,
                                  begin_day) + timedelta(days=count)

            # 某天日期
            delta = timedelta(days=(int(begin_week) - 1) * 7)
            new_date = begin_date + delta
            new_year, new_month, new_day = new_date.year, new_date.month, new_date.day

            freq = {'freq': 'weekly', 'count': int(
                end_week) - int(begin_week) + 1}

            start = datetime(new_year, new_month, new_day,
                             s1, s2, 0, tzinfo=tz_utc_8)
            end = datetime(new_year, new_month, new_day,
                           e1, e2, 0, tzinfo=tz_utc_8)

            cal.add_component(cread_event(
                name, cls_room, teacher, start, end, freq))
        else:
            week_lst = []
            for item in lesson['week'].split(','):
                if '-' not in item:
                    if item:
                        week_lst.append(item)
                else:
                    week1, week2 = item.split('-')
                    for i in range(int(week1), int(week2) + 1):
                        week_lst.append(i)

            for week in week_lst:

                begin_date = datetime(begin_year, begin_month,
                                      begin_day) + timedelta(days=count)

                delta = timedelta(days=(int(week) - 1) * 7)
                new_date = begin_date + delta
                new_year, new_month, new_day = new_date.year, new_date.month, new_date.day

                start = datetime(new_year, new_month, new_day,
                                 s1, s2, 0, tzinfo=tz_utc_8)
                end = datetime(new_year, new_month, new_day,
                               e1, e2, 0, tzinfo=tz_utc_8)

                cal.add_component(cread_event(
                    name, cls_room, teacher, start, end))

        time.sleep(0.1)
    count += 1


f = open('example2.ics', 'wb')
f.write(cal.to_ical())
f.close()
