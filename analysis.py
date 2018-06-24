# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pandas import DataFrame,Series


# 去掉Chrome显示 “正受到自动测试软件的控制”的提示
# 或者让浏览器采用静默模式加载，让它在后台运行，option.add_argument（'headless')
option = webdriver.ChromeOptions()
# option.add_argument('disable-infobars')
option.add_argument('headless')

# phantomjs
# browser = webdriver.PhantomJS('F:\phantomjs\phantomjs_119912/bin/phantomjs.exe')
# browser.set_window_size(120, 60)

browser = webdriver.Chrome('C:/Users/chen/AppData/Local/Google/Chrome/Application/chromedriver',chrome_options=option)
column_name = ['股票代码', '公司名称', '营业收入', '净利润', '净资产收益率(%)']
file_content = DataFrame(columns=column_name)  # 创建空 DataFrame
years = ['201712','201612','201512']

# 读取三年的业绩报表
for year in years:
    url_path = 'http://data.eastmoney.com/bbsj/' + year + '/yjkb.html'
    print(url_path)
    file_name = year + '.csv'
    # 得到网页
    browser.get(url_path)
    print('a')
    # 点击网页页面业绩报表
    result1=WebDriverWait(browser, 10).until(EC.presence_of_element_located((
            By.XPATH, "//li[contains(text(),'业绩报表')]"))).click()  # 元素加载出，传入定位元组，如(By.ID, 'p')
    print('b')
    time.sleep(1)
    # 点击网页页面 沪深A股
    result2=WebDriverWait(browser, 30).until(EC.presence_of_element_located((
            By.XPATH,"//*[text()='沪深A股']"))).click()  # 直接查找页面当中所有的”沪深A股“，不用知道它是什么元素。
    print('c')
    while True :
        html_content = BeautifulSoup(browser.page_source, "html.parser")
        all_tr_content = html_content.find('table', id='dt_1').find('tbody').find_all('tr')

        for tr in all_tr_content:
            all_ta_content = tr.find_all('td')
            temp_list = [all_ta_content[1].get_text(),all_ta_content[2].get_text(),
                         all_ta_content[5].get_text(),all_ta_content[8].get_text(),all_ta_content[12].get_text()]

            temp_content = Series(temp_list,index=column_name)
            file_content = file_content.append(temp_content,ignore_index=True)
        print('d')
        nextPage = WebDriverWait(browser, 10).until(EC.presence_of_element_located((
            By.XPATH, "//a[contains(text(),'下一页')]")))

        if nextPage.get_attribute('class') == 'nolink':
            break
        nextPage.click()
        print('e')
        time.sleep(5)

    # 保存数据位.csv文件
    file_content.to_csv(file_name,encoding='utf-8')
    print('f')
    # 将DataFrame内容清空
    file_content.drop(file_content.index,inplace=True)
    print('g')