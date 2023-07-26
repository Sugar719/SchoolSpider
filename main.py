## 导包
from lxml import etree
import requests
from html.parser import HTMLParser
import pandas as pd
import random
import time
import datetime
import smtplib
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import csv


def request_yanjiusheng():
    """
    访问xxxx
    :return: 以列表形式 title_text（标题） time_text（时间） href_text（链接）
    """
    # 设置请求头参数：User-Agent, cookie, referer
    headers = {
        'User-Agent': '**',
        'cookie': "**",
        # 设置从何处跳转过来
        'referer': '**'
    }

    for i in range(1, 2):  # 暂取1页
        if i != 1:
            url = 'xxx' + str(i) + '.jhtml'
        else:
            url = 'xxx'

        # url = 'xxx' # 首页网址URL
        page_text = requests.get(url=url, headers=headers).text  # 请求发送
        tree = etree.HTML(page_text)  # 数据解析

        # 分割出标题、时间、链接
        title_text = tree.xpath('//ul[@class="article-list"]//a//text()')
        time_text = tree.xpath('//ul[@class="article-list"]//span//text()')
        href_text = tree.xpath('//ul[@class="article-list"]//a/@href')

        # for i in range(len(title_text)):
        #     print("{} {} {}".format(time_text[i], title_text[i], href_text[i]))

        return [title_text, time_text, href_text]


def send_email(href, title):
    """
    发送邮件
    =========发送内容尚未编辑完成
    """
    host_server = 'smtp.qq.com'  # qq邮箱smtp服务器
    sender_qq = 'xxxx@foxmail.com'  # 发件人邮箱
    pwd = '**'
    receivers = ['xxxx@qq.com']
    mail_title = "【研究生院通知更新】{} {}".format(datetime.datetime.now().strftime('%Y-%m-%d'), time.strftime("%H:%M:%S"))  # 邮件标题

    # 邮件正文内容
    mail_content = "研究生院有新通知，<p>这是研究生院的新通知：</p> <p><a href={}>{}</a></p>".format(href, title)
    print(mail_content)

    msg = MIMEMultipart()
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_qq
    msg["To"] = receivers[0]

    msg.attach(MIMEText(mail_content, 'html'))

    try:
        smtp = SMTP_SSL(host_server)  # ssl登录连接到邮件服务器
        smtp.set_debuglevel(1)  # 0是关闭，1是开启debug
        smtp.ehlo(host_server)  # 跟服务器打招呼，告诉它我们准备连接，最好加上这行代码
        smtp.login(sender_qq, pwd)
        smtp.sendmail(sender_qq, receivers[0], msg.as_string())
        smtp.quit()
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("无法发送邮件")


def update(filename):
    """
    更新网页
    """
    try:
        df = pd.read_excel('./研究生教务通知.xls')
    except FileNotFoundError:
        print('找不到储存文件，已终止程序')
        exit()

    # 获取请求
    result = request_yanjiusheng()
    title_request = result[0]
    date_request = result[1]
    href_request = result[2]

    href_data = df['href'].tolist()  # 文件中的href列表
    data_return = pd.DataFrame(columns=['title', 'time', 'href']) # 存放所有更新信息汇总

    for i in range(len(href_request)):
        href = href_request[i]  # 当前网站上href、标题、时间
        title = title_request[i]
        date = date_request[i]
        # 检查每一个href是否已经存在xls中
        if href not in href_data:  # 不存在->有更新
            # 新增标题、时间、href进入xls中
            result = list(map(list, zip(*[[title], [date], [href]])))
            new_data = pd.DataFrame(result, columns=['title', 'time', 'href'])
            data_return = pd.concat([data_return, new_data])
    df = pd.concat([df, data_return])
    df.to_excel('**.xls', index=False)
    return data_return

def new_xls():
    """
    初始化文件列表
    :return:
    """
    df = pd.DataFrame(columns=['title', 'time', 'href']) # 新建表格
    result = request_yanjiusheng() # 获取请求
    result = list(map(list, zip(*result)))
    new_data = pd.DataFrame(result, columns=['title','time','href']) # 写入数据
    df = pd.concat([df, new_data])
    df.to_excel('**.xls', index=False)
    print("已获取通知并初始化文件")


if __name__=='__main__':
    while True:
        new_dataframe = update('./研究生教务通知.xls')
        if not new_dataframe.empty:
            href_list = new_dataframe['href'].tolist()
            title_list = new_dataframe['title'].tolist()
            for i in range(len(title_list)):
                send_email(href=href_list[i], title=title_list[i])
        time.sleep(60)