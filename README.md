## Lesson_ics

使用Cookie，自动导出学校教务管理系统中的课表，并解析成json。再将json转为ics日历格式。

```bash
requests
icalendar
bs4
```

### 运行：

复制cookie到main.py的主函数中，运行。或者用已经生成的本地json文件运行。



### Note

1. `ref.ics`是参考的ics文件格式
2. `tz_utc_8 = timezone(timedelta(hours=8))`表示的北京时间
3. uuid是为了让UID唯一
4. 小米、VIVO经测试不可导入，因为厂商阉割了此功能；魅族、荣耀、三星、苹果均可导入
5. `begin_year`、`begin_month`、`begin_day`表示一个学期开始的年月日
