## Lesson_ics

使用Cookie，自动导出学校教务管理系统中的课表，并解析成json。再将json转为ics日历格式。运行环境python3+

```bash
requests
icalendar
bs4
numpy
pandas
Pillow
pyexecjs

```

### 运行：

复制cookie到main.py的主函数中，运行。或者用已经生成的本地json文件运行。

### 验证码识别
https://www.yuque.com/zhiwa/deepin/leiod0

目前识别率78% 还有缺陷 错误可以多试几次，当然也可以改下直到正确为止。

### Note

1. `ref.ics`是参考的ics文件格式
2. `tz_utc_8 = timezone(timedelta(hours=8))`表示的北京时间
3. uuid是为了让UID唯一
4. 小米、VIVO经测试不可导入，因为厂商阉割了此功能；魅族、荣耀、三星、苹果、华为均可导入，其中苹果导入的方式是用邮件发送到ios设备上的已绑定的邮件中。
5. `begin_year`、`begin_month`、`begin_day`表示一个学期开始的年月日
6. `time_dict`是我校课程时间安排，由于1和3存在差异，即有的课上两节有的课上三节，教务管理系统中未标记，这里统一标记为三节

### 我们还可以做什么

* 课表（/提前）查询
* 空闲教室
* 查看成绩
* 课程执行计划
* 考过的四六级成绩
* 选课
* 评教
* 毕设选题

