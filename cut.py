# 安装依赖：numpy, pandas, Pillow, request, pyexecjs

from PIL import Image
from io import BytesIO
import os,requests,execjs
import numpy as np
import pandas as pd


np.set_printoptions(threshold = np.inf)


# 将图片转化为模型
def get_modes(imgs):
    modes = []
    for img in imgs:
        mode = np.asarray(img)
        mode = np.where(mode < 120, 0, 1)
        modes.append(mode)
    return modes


# 破解前端js加密
def trans_id(username, password):
    node = execjs.get()
    jsfile = 'encodeInp.js'
    ctx = node.compile(open(jsfile).read())
    # 原 JS 函数名 为 encodeInp()
    user = f'encodeInp("{username}")'
    pwd = f'encodeInp("{password}")'
    return f'{str(ctx.eval(user))}%%%{str(ctx.eval(pwd))}'


# 识别验证码
def get_captcha(img):
    # 导入模型名称
    def get_fname():
        path = 'mode/'
        dirs = os.listdir(path)
        return list(dirs)
    # 灰度化 切割 转化为数组模型
    img = img.convert('L')
    box1 = (4, 4, 12, 16)
    box2 = (14, 4, 22, 16)
    box3 = (24, 4, 32, 16)
    box4 = (34, 4, 42, 16)
    img1 = img.crop(box1)
    img2 = img.crop(box2)
    img3 = img.crop(box3)
    img4 = img.crop(box4)
    imgs = [img1, img2, img3, img4]
    modes = get_modes(imgs)
    # print(modes[1])
    # print(modes[3])
    # np.save('mode/n.npy',modes[1])
    # np.save('mode/m1.npy',modes[3])
    name_list = get_fname()
    last_num = ''
    # 分别计算验证码中4个模型的最小欧拉距离的值
    for mode in modes:
        disk_log = {}
        for name in name_list:
            npdata = np.load('mode/{}'.format(name))
            dist = np.linalg.norm(npdata - mode)
            disk_log[name] = dist
        last_num = last_num + min(disk_log,key=disk_log.get)[0]
    return last_num


def get_cookie(username, password):
    url = 'http://jwc104.ncu.edu.cn:8081/jsxsd/verifycode.servlet'
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    }
    response = session.get(url,headers=headers)
    img = Image.open(BytesIO(response.content))
    # img.show()
    cookies = requests.utils.dict_from_cookiejar(response.cookies)
    cookies = f"JSESSIONID={cookies['JSESSIONID']};SERVERID={cookies['SERVERID']}"
    post_url = 'http://jwc104.ncu.edu.cn:8081/jsxsd/xk/LoginToXk'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
        'Cookie': cookies
    }
    user = trans_id(str(username), str(password))
    captcha = get_captcha(img)
    print(captcha)
    data = {
        'encoded': user,
        'RANDOMCODE': captcha
    }
    res = session.post(post_url,headers=headers,data=data)
    if '验证码错误' in res.text:
        print('验证码错误')
        return '验证码错误'
    elif '密码错误' in res.text:
        print('用户名或没密码错误')
        return '用户名或没密码错误'
    else:
        return cookies
    
# 测试识别率 2次都是78%
def test():
    n=0
    for _ in range(100):
        a = get_cookie('123123', '123123')
        if '验证' not in a:
            n+=1
    print(n/100)
    return n/100



