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
    访问***
    :return: 以列表形式 title_text（标题） time_text（时间） href_text（链接）
    """
    # 设置请求头参数：User-Agent, cookie, referer
    headers = {
        'User-Agent': '***',
        'cookie': "***",
        # 设置从何处跳转过来
        'referer': '***'
    }

    for i in range(1, 5):  # 暂取5页
        if i != 1:
            url = '***' + str(i) + '.jhtml'
        else:
            url = '***'

        # url = '***' # 首页网址URL
        page_text = requests.get(url=url, headers=headers).text  # 请求发送
        tree = etree.HTML(page_text)  # 数据解析

        # 分割出标题、时间、链接
        title_text = tree.xpath('//ul[@class="article-list"]//a//text()')
        time_text = tree.xpath('//ul[@class="article-list"]//span//text()')
        href_text = tree.xpath('//ul[@class="article-list"]//a/@href')

        # for i in range(len(title_text)):
        #     print("{} {} {}".format(time_text[i], title_text[i], href_text[i]))

        return [title_text, time_text, href_text]


def send_email():
    """
    发送邮件
    =========发送内容尚未编辑完成
    """
    host_server = 'smtp.qq.com'  # qq邮箱smtp服务器
    sender_qq = '***'  # 发件人邮箱
    pwd = '***'
    receiver = '***'
    mail_title = 'Python自动发送html格式的邮件'  # 邮件标题

    # 邮件正文内容
    mail_content = "您好，<p>这是使用python登录QQ邮箱发送HTNL格式邮件的测试：</p> <p><a href='https://blog.csdn.net/weixin_44827418?spm=1000.2115.3001.5113'>CSDN个人主页</a></p>"

    msg = MIMEMultipart()
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_qq
    msg["To"] = Header("测试邮箱", "utf-8")

    msg.attach(MIMEText(mail_content, 'html'))

    try:
        smtp = SMTP_SSL(host_server)  # ssl登录连接到邮件服务器
        smtp.set_debuglevel(1)  # 0是关闭，1是开启debug
        smtp.ehlo(host_server)  # 跟服务器打招呼，告诉它我们准备连接，最好加上这行代码
        smtp.login(sender_qq, pwd)
        smtp.sendmail(sender_qq, receiver, msg.as_string())
        smtp.quit()
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("无法发送邮件")


def update():
    """
    更新网页
    每5分钟更新一次
    ========更新内容尚未完成
    """
    print('通知系统启动中')
    old_pattern = request_yanjiusheng()  # 记录原始内容列表
    title_df = pd.DataFrame({'标题': old_pattern[0]})
    time_df = pd.DataFrame({'时间': old_pattern[1]})
    href_df = pd.DataFrame({'链接': old_pattern[2]})


    while True:
        new_pattern = request_yanjiusheng()  # 记录新内容列表
        if new_pattern != old_pattern:  # 判断内容列表是否更新
            old_pattern = new_pattern  # 原始内容列表改变
            send_email()  # 发送邮件
        else:
            now = datetime.datetime.now()
            print(now, "尚无更新")
        time.sleep(300)  # 五分钟检测一次
