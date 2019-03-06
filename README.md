## Lesson_ics

使用Cookie，自动导出学校教务管理系统中的课表，并解析成json。再将json转为ics日历格式。

```bash
requests
icalendar
bs4
```

### 运行：

1. 将cookie复制到`get_lesson.py`中，运行，生成`cls2.json`

2. 运行`main.py`，生成`example2.ics`文件
3. 安卓系统可以直接打开，检查没什么大问题之后，便可导入日程。IOS需要使用邮件功能，将ics文件发送到ios系统中**邮件**中绑定的邮箱，从邮箱中打开附件的ics文件，即可导入。



### Note

1. `main.py`中ref是参考的ics格式，可忽略；`tz_utc_8 = timezone(timedelta(hours=8))`表示的北京时间
2. `main.py`中设置`time.sleep(0.1)`是因为在一些格式要求严格的系统中，ics的**UID**要保证唯一性
3. 小米、VIVO经测试不可导入，因为厂商阉割了此功能。