# -*- coding: UTF-8 -*-"

'''
# 工具箱
'''

import datetime, os, time, zipfile, logging, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .settings import WAIT_IMPLY, TEST, WORKTIME


def breakWork(delta=1, hour=0, minute=0):
    '''
    description: 爬虫停止工作时间。若连续爬取失败直至这个设定的时间，爬虫停止工作，报告错误。
    param delta: 和当天相比的天数差,大于0表示向后延续。
    param hour：设定 时
    param minute: 设定分
    '''
    date_ = datetime.datetime.now().date()
    y, m, d = date_.year, date_.month, date_.day
    breakTime = datetime.datetime(y, m, d, hour, minute, 0) + datetime.timedelta(days=delta)
    return breakTime


def checkAd(driver):
    '# 检测小广告'
    adFrame = driver.find_elements_by_xpath('//iframe[@id="adframe"]')
    if adFrame:     # 有小广告弹出，点击关闭
        print('有广告！！！')
        closeButton = driver.find_element_by_xpath('//a[@class="icon-close close_"]')  # 找到关闭按钮
#        closeButton = driver.find_element_by_xpath('//span[text()="X"]')  # 找到关闭按钮
        closeButton.click()
        print('广告已关闭！！！')
        driver.refresh()
        time.sleep(5)


def initPath(*args):
    '# 创建路径'
    path = os.path.join(*args)
    if not os.path.exists(path):
        os.makedirs(path)      # 创建文件夹。
        print(NOW(), '路径({})创建完毕...'.format(path))
    else:
        print(NOW(), '路径({})已存在...'.format(path))
    return path


def NOW():
    '# 返回当前时间字符串,精度到秒'
    return '{}'.format(str(datetime.datetime.now())[:19])


def screenshot(driver, fp, w=1200, h=1200):
    '''
    # 截图工具
    # param driver: webdriver对象
    # param fp: 保存图片的路径
    # w, h: 保存图片额宽度与高度(像素)
    '''
    time.sleep(WAIT_IMPLY)
    driver.set_window_size(w, h)
    driver.save_screenshot(fp)
    print(NOW(), '网页截图完成,保存路径: {}'.format(fp))


def sleep():
    'description: 根据设定的时间休眠，直至设定时间。24小时制。'
    now = datetime.datetime.now()
    if TEST:
        workTime = now
    else:
        workTime = datetime.datetime.combine(now.date(), datetime.time(*WORKTIME))
        if now > workTime:  # 如果当天的时间已经超过了预设的工作时间，则安排到明天
            workTime += datetime.timedelta(days=1)
    timeRemain = workTime - now
    sec = timeRemain.total_seconds()
    h, m, s = sec//3600, (sec%3600)//60, int(sec%60)
    print(NOW(), '距离下次爬取({0})还有{1:0>2.0f}小时{2:0>2.0f}分钟{3:0>2.0f}秒...\n'.format(str(workTime)[:19], h, m, s))
    time.sleep(sec)
    
         
# 文件打包
def zipFile(path):
    '''
    # 文件夹压缩工具
    # param path: 需要压缩的文件夹路径,压缩后为和文件夹同名同目录的zip文件
    '''
    zpath = path + '.zip'
    z = zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED)
    try:
        fnames = next(os.walk(path))[2] # 打包文件夹下所有文件
        for fname in fnames:
            fpath = os.path.join(path, fname)
            z.write(fpath, fname)
        print(NOW(), '数据压缩成功({})'.format(zpath))
    except Exception:
        raise
    finally:
        z.close()


class ExceptionCatcher():
    '''
    # 异常捕捉器
    '''
    def __init__(self, path):
        self.path = path                    # 日志路径
        self.logger = logging.getLogger()
        # 配置FileHandler
        fmt = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")     # 格式
        self.fHandler = logging.FileHandler(os.path.join(path, 'log.txt' ))     # 日志文档
        self.fHandler.setFormatter(fmt)
        self.fHandler.setLevel(logging.WARNING)
        # 配置StreamHandler
        self.sHandler = logging.StreamHandler()
        self.sHandler = logging.StreamHandler()
        self.sHandler.setLevel(logging.WARNING)
        # 添加Handler
        self.logger.addHandler(self.fHandler)
        self.logger.addHandler(self.sHandler)
    
    def driverException(self, driver, msg):
        '# 附带webdriver截图功能的异常记录器'
        now = datetime.datetime.now()
        fname = '{0:0>4.0f}{1:0>2.0f}{2:0>2.0f}_{3:0>2.0f}{4:0>2.0f}{5:0>2.0f}_{6}.png'.format(now.year, now.month, now.day, 
                                                                                               now.hour, now.minute, now.second, 
                                                                                               now.microsecond) # 截图名称
        fpath = os.path.join(self.path, fname)  # 截图保存路径
        screenshot(driver=driver, fp=fpath, w=2000, h=2000)
        self.logger.exception(msg)
    
    def exception(self, msg):
        self.logger.exception(msg)
    
    def close(self):
        '# 关闭错误日志文档通道'
        self.fHandler.close()


class MailRobot():
    '''
    # 邮件机器人
    '''
    def __init__(self):
        self.smtpHost = 'smtp.163.com'                #发件邮箱的smtp服务器地址
        self.popHost = 'pop.163.com'                  #收件邮箱的pop3服务器地址
        self.userName = 'Watchman'                    #邮箱用户名
        self.mailName = 'shawnpy'                     #邮箱名
        self.mailPWD = "GuidovanRossum00"             #密码(授权码)
        self.mailPostfix = '163.com'                  #邮箱的后缀
            
    def sendMail(self, to, subject, msg, attachment=None):
        '''
        param to: 收件人
        param subject: 标题
        param msg: 文本信息
        param attachment: 附件,附件必须是英文或数字命名,否则无法显示附件名。
        '''
        sender = '{0}<{1}@{2}>'.format(self.userName, self.mailName, self.mailPostfix)
        MSG = MIMEMultipart('related')
        msgText = MIMEText(msg, _subtype='plain')
        MSG.attach(msgText)
        MSG['Subject'] = subject            #输入标题
        MSG['From'] = sender
        MSG['To'] = to
        # 发送附件
        if attachment:
            with open(attachment, 'rb') as f:
                # ??
                fname = os.path.basename(attachment)
                att = MIMEText(f.read(), "base64", "utf-8")
                att["Content-Type"] = "application/octet-stream"
                att.add_header('Content-Disposition', 'attachment', filename=fname)
                MSG.attach(att)
        try:
            server = smtplib.SMTP()
            server.connect(self.smtpHost)    #连接SMTP服务器
            server.login(self.mailName,self.mailPWD)    #登录SMTP服务器
            server.sendmail(sender, to, MSG.as_string())
            print(NOW(), '邮件发送成功(To: {})...'.format(to))
        except Exception:
            raise
        finally:
            server.close()



    