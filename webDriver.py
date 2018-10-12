# -*- coding: UTF-8 -*-"

'''
HTML爬取器
'''

import time

from selenium import webdriver

from .parser import Parser
from .settings import WAIT_IMPLY, TEST
from .toolkit import checkAd



class Crawler:
    def __init__(self, path, catcher):
        options = webdriver.FirefoxOptions()
        options.set_headless()      # 无头模式
        self.driver = webdriver.Firefox(firefox_options=options)
        self.parser = Parser(path=path, catcher=catcher)
        self.driver.implicitly_wait(WAIT_IMPLY)
        self.driver.maximize_window()
        self.handles = self.driver.window_handles
        self.catcher = catcher
    
    def _crawl_(self, ele, parser):
        '# 网页爬取器'
        try:
            # 初始化页面
            self.driver.switch_to_window(self.handles[0]) # 选取第一个窗口
            self.driver.get(r'http://www.fangdi.com.cn/trade/trade.html')    # 初始化首页
            checkAd(self.driver)    # 查找是否有广告弹出
            # 点击更多按钮
            c = self.driver.find_element_by_xpath(ele)
            self.driver.execute_script("arguments[0].scrollIntoView();", c) #拖动到可见的元素去
            time.sleep(1)
            c.click()
            # 选择窗口
            self.handles = self.driver.window_handles   # 更新窗口
            self.driver.switch_to_window(self.handles[-1])
            checkAd(self.driver)
        except:
            self.catcher.driverException(self.driver, '(webDriver.Crawler._crawl_())数据爬取失败...')
            if TEST:
                raise
        parser(self.driver)
    
    def run(self):
        '# 运行爬虫'
        try:
            self._crawl_(r'//span/i[text()="一手房各区可售统计"]/parent::span/following-sibling::a[text()="更多"]', 
                       self.parser.parseTradeLeving)
            self._crawl_(r'//span/i[text()="一手房各区成交统计"]/parent::span/following-sibling::a[text()="更多"]', 
                       self.parser.parseTradeTransaction)
            self._crawl_(r'//span/i[text()="一手房各区住宅成交"]/parent::span/following-sibling::a[text()="更多"]/span', 
                       self.parser.parseTradeResidence)
            self.parser.subtotal()      # 汇总数据，储存数据
        except Exception:
            self.catcher.driverException(self.driver, '(webDriver.Crawler.run())数据爬取失败...')
            if TEST:
                raise
        finally:
            self.driver.quit()
        
