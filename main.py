# -*- coding: UTF-8 -*-"

'''
# 主框架
'''

import datetime, time

from .webDriver import Crawler
from .toolkit import MailRobot, zipFile, NOW, sleep, breakWork, initPath, ExceptionCatcher
from .settings import PATH, TEST, TO, TOTEST, TOMONITOR


def run():
    if TEST:
        to = TOTEST
    else:
        to = TO
    while True:
        collectingComplete = False
        sleep()     # 休眠至工作时间
        print(NOW(), '{}开始爬取网房数据...'.format('(测试模式)' if TEST else ''))
        date_ = str(datetime.date.today())      # 获取当天日期字符串
        bt = breakWork()                        # 生成停止爬取时间
        dataPath = initPath(PATH, date_)        # 数据存储路径初始化
        logPath = initPath(PATH, 'log', date_)  # 日志存储路径
        TOM = MailRobot()                       # 邮件机器人初始化
        MIKE = ExceptionCatcher(logPath)        # 错误捕捉器
        # 进入工作循环
        try:
            while True:
                if datetime.datetime.now() < bt:
                    try:
                        JACK = Crawler(path=dataPath, catcher=MIKE)
                        JACK.run()
                        collectingComplete = True
                        break
                    except Exception as e:
                        MIKE.exception('(main.run())数据爬取失败...')
                        if TEST:
                            raise
                else:   # 过了breakWork的时间点，就停止爬取数据
                    break
            # 发送邮件(就一次)
            if collectingComplete:  # 采集成功
                try:
                    zipFile(dataPath)       # 数据文件文件打包
                    zipFile(logPath)        # 日志文件文件打包
                    TOM.sendMail(to=to,         # geshaowei@surea.com; 115683956@qq.com
                                 subject='{}的网房数据'.format(date_), 
                                 msg='{}的网房数据'.format(date_), 
                                 attachment=dataPath+'.zip')
                    TOM.sendMail(to=TOMONITOR,  #to='geshaowei@surea.com',
                                 subject='{}的网房数据发送成功'.format(date_), 
                                 msg=NOW()+' {}的网房数据发送成功'.format(date_), 
                                 attachment=logPath+'.zip')
                    print('\n')
                except Exception as e:
                    print(NOW(), '数据发送失败...')
                    zipFile(logPath)            # 日志文件文件打包
                    TOM.sendMail(to=TOMONITOR,  #to='geshaowei@surea.com',
                                 subject='数据发送失败'.format(date_), 
                                 msg=NOW()+' 数据采集成功，但是数据发送失败!\n{0}的网房数据发送失败\n{1}'.format(date_, e), 
                                 attachment=logPath+'.zip')
                    MIKE.exception('(main.run())邮件(数据)发送失败...')
                    if TEST:
                        raise
            else:       # 数据采集失败
                zipFile(logPath)            # 日志文件文件打包
                TOM.sendMail(to=TOMONITOR,  #to='geshaowei@surea.com', 
                             subject='数据爬取失败'.format(date_), 
                             msg=NOW()+' 数据爬取失败!\n{}的网房数据数据爬取失败\n'.format(date_), 
                             attachment=logPath+'.zip')
        
        except:
            MIKE.exception('(main.run())工作循环异常...')
            if TEST:
                raise
        
        finally:
            MIKE.close()
            if TEST:    # 测试模式下连续两次爬取直接相隔
                s = 10
                print('*********测试模式暂停{}秒**********\n'.format(s))
                time.sleep(s)

        
        