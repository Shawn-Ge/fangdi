# -*- coding: UTF-8 -*-"

'''
HTML代码解析器
'''

import datetime, os
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait

from .settings import WAIT, TEST
from .toolkit import NOW, screenshot


class Parser:
    '# 网房解析器'
    def __init__(self, path, catcher):
        self.tradeTransaction = []      # 一手房区域成交统计(住宅、办公、商业、其他)
        self.path = path
        self.catcher = catcher    # initLogger(self.logPath)

    def parseTradeLeving(self, driver):
        '# 一手房区域可售统计'
        screenshot(driver, os.path.join(self.path, '一手房区域可售统计.png'))     # 保存截图
        try:
            WebDriverWait(driver, WAIT).until(lambda d: d.find_element_by_xpath(r'//div[@class="today_trade_info"]/ul/li/span[text()="全市"]'))
            uls = driver.find_elements_by_xpath(r'//div[@class="today_trade_info"]/ul')
            data = []
            idx = []
            cols = ['普通住宅可售套数（套）', '普通住宅可售面积 （万㎡）', 
                    '住宅可售套数（套）', '住宅可售面积（万㎡）', 
                    '办公可售套数（套）', '办公可售面积（万㎡）',
                    '商业成交套数（套）', '商业可售面积（万㎡）', 
                    '其他成交套数（套）', '其他可售面积（万㎡）']
            for ul in uls:
                lis = ul.find_elements_by_xpath(r'./li')
                district = lis[0].find_element_by_xpath(r'./span').text # 获取区域
                idx.append(district)
                d = []
                for li in lis[1:]:  # 获取该地区的数据
                    spans = li.find_elements_by_xpath(r'./span')
                    d.append(spans[0].find_element_by_xpath(r'./i').text)
                    d.append(spans[1].find_element_by_xpath(r'./i').text)
                data.append(d)
                print(NOW(), '一手房各区可售统计:区域({})获取完毕...'.format(district))
            self.tradeLeving = pd.DataFrame(data, index=idx, columns=cols)
            print(NOW(), '一手房各区可售统计数据获取完毕...')
        except:
            self.catcher.driverException(driver, '(parser.Parser.parseTradeLeving())一手房区域可售统计数据爬取失败...')
            if TEST:
                raise
        
    def parseTradeTransaction(self, driver):
        '# 一手房区域成交统计(住宅、办公、商业、其他)'
        T = {'住宅': '', '办公': '2', '商业': '3', '其他': '4'}     # 分别是：住宅，办公，商业，其他
        for t in T:
            try:
                # 先点击分页,然后截图
                button = driver.find_element_by_xpath(r'//h6/span[text()="{}"]'.format(t))
                button.click()
            except:
                self.catcher.driverException(driver, '(parser.Parser.parseTradeTransaction())一手房区域成交统计按钮选取...')
                if TEST:
                    raise
            screenshot(driver, os.path.join(self.path, '一手房区域成交统计({}).png'.format(t)))   # 保存截图
            try:
                WebDriverWait(driver, WAIT).until(lambda d: d.find_element_by_xpath(r'//div[@id="TransactionStat{}"]/ul/li/span[text()="全市"]'.format(T[t])))
                uls = driver.find_elements_by_xpath(r'//div[@id="TransactionStat{}"]/ul'.format(T[t]))
                data = []
                idx = []
                cols = ['{}今年成交套数（套）'.format(t), '{}今年成交面积（万㎡）'.format(t), 
                        '{}今日成交套数（套）'.format(t), '{}今日成交面积（㎡）'.format(t), 
                        ]
                for ul in uls:
                    lis = ul.find_elements_by_xpath(r'./li')
                    district = lis[0].find_element_by_xpath(r'./span').text # 获取区域
                    idx.append(district)
                    d = []
                    for li in lis[1:]:  # 获取该地区的数据
                        spans = li.find_elements_by_xpath(r'./span')
                        d.append(spans[0].find_element_by_xpath(r'./i').text)
                        d.append(spans[1].find_element_by_xpath(r'./i').text)
                    data.append(d)
                    print(NOW(), '一手房区域成交统计({0}):区域({1})获取完毕...'.format(t, district))
                df = pd.DataFrame(data, index=idx, columns=cols)
                self.tradeTransaction.append(df)
                print(NOW(), '一手房区域成交统计({})数据获取完毕...'.format(t))
            except:
                self.catcher.driverException(driver, '(parser.Parser.parseTradeTransaction())一手房区域成交统计数据爬取失败...')
                if TEST:
                    raise
    
    def parseTradeResidence(self, driver):
        '# 一手房区域住宅成交统计'
        screenshot(driver, os.path.join(self.path, '一手房区域住宅成交统计.png'))       # 保存截图
        try:
            WebDriverWait(driver, WAIT).until(lambda d: d.find_element_by_xpath(r'//div[@class="today_trade_info"]/ul/li/span[text()="全市"]'))
            uls = driver.find_elements_by_xpath(r'//div[@class="today_trade_info"]/ul')
            data = []
            idx = []
            cols = ['普通住宅今年成交套数（套）', '普通住宅今年成交面积（万㎡）', 
                    '配套住宅今年成交套数（套）', '配套住宅今年成交面积（万㎡）', 
                    '普通住宅今日成交套数（套）', '普通住宅今日成交面积（㎡）', 
                    '配套住宅今日成交套数（套）', '配套住宅今日成交面积（㎡）', 
                    ]
            for ul in uls:
                lis = ul.find_elements_by_xpath(r'./li')
                district = lis[0].find_element_by_xpath(r'./span').text # 获取区域
                idx.append(district)
                d = []
                for li in lis[1:]:  # 获取该地区的数据
                    spans = li.find_elements_by_xpath(r'./span')
                    d.append(spans[0].find_element_by_xpath(r'./i').text)
                    d.append(spans[1].find_element_by_xpath(r'./i').text)
                data.append(d)
                print(NOW(), '一手房区域住宅成交统计:区域({})获取完毕...'.format(district))
            self.tradeResidence = pd.DataFrame(data, index=idx, columns=cols)
            print(NOW(), '一手房区域住宅成交统计数据获取完毕...')
        except:
            self.catcher.driverException(driver, '(parser.Parser.parseTradeResidence())一手房区域住宅成交统计数据爬取失败...')
            if TEST:
                raise
        
    def subtotal(self):
        '# 将爬取的数据整合分类汇总'
        try:
            date_ = str(datetime.date.today())
            chengjiaoCols = ['住宅今日成交套数（套）', '住宅今日成交面积（㎡）', 
                             '普通住宅今日成交套数（套）', '普通住宅今日成交面积（㎡）', 
                             '办公今日成交套数（套）', '办公今日成交面积（㎡）' ,
                             '商业今日成交套数（套）', '商业今日成交面积（㎡）', 
                             '其他今日成交套数（套）', '其他今日成交面积（㎡）']
            
            keshouCols = ['住宅可售套数（套）', '住宅可售面积（万㎡）', 
                          '普通住宅可售套数（套）', '普通住宅可售面积 （万㎡）', 
                          '办公可售套数（套）', '办公可售面积（万㎡）' ,
                          '商业成交套数（套）', '商业可售面积（万㎡）', 
                          '其他成交套数（套）', '其他可售面积（万㎡）']
            # 整合成交数据
            chengjiao = self.tradeResidence[['普通住宅今日成交套数（套）', '普通住宅今日成交面积（㎡）']].copy()
            for t, df in zip(['住宅', '办公', '商业', '其他'], self.tradeTransaction):
                chengjiao = chengjiao.join(df[['{}今日成交套数（套）'.format(t), '{}今日成交面积（㎡）'.format(t)]].copy(), how='outer')
            chengjiao = chengjiao[chengjiaoCols].copy()
            # 整合可售数据
            keshou = self.tradeLeving[keshouCols].copy()
            # 抽取全市数据
            total = pd.DataFrame([chengjiaoCols, list(chengjiao.loc['全市', :]), 
                                  keshouCols, list(keshou.loc['全市', :])], 
                                  index=['成交案例', date_, '可售案例', date_])
            # 写入excel
            excelPath = os.path.join(self.path, '{}_网房数据.xlsx'.format(date_))
            writer = pd.ExcelWriter(excelPath)                                                 # 初始化excel文件写入器
            total.to_excel(writer, sheet_name='全市统计数据', encoding='gbk', header=False)        # 全市统计数据
            chengjiao.to_excel(writer, sheet_name='成交案例统计数据', encoding='gbk')               # 成交案例统计数据
            keshou.to_excel(writer, sheet_name='可售案例统计数据', encoding='gbk')                  # 可售案例统计数据
            self.tradeLeving.to_excel(writer, sheet_name='一手房区域可售统计', encoding='gbk')       # 一手房区域可售统计
            for t, df in zip(['住宅', '办公', '商业', '其他'], self.tradeTransaction):              # 一手房区域成交统计(住宅,办公,商业,其他)
                df.to_excel(writer, sheet_name='一手房区域成交统计({})'.format(t), encoding='gbk')
            self.tradeResidence.to_excel(writer, sheet_name='一手房区域住宅成交统计', encoding='gbk')  # 一手房区域住宅成交统计
            writer.save()
            print(NOW(), '数据成功写入excel文件({})...'.format(excelPath))
        except:
            self.catcher.exception('(parser.Parser.subtotal())写入excel失败...')
            if TEST:
                raise
        
        