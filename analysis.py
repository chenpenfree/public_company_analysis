# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pandas import DataFrame,Series
import pandas as pd


def crawel_east_money():
    """
    爬取东方财富网上市公司三年的营收、净利润和ROE数据
    """

    # 让浏览器采用静默模式加载，让它在后台运行，option.add_argument（'headless')
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('User-Agent="Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/60.0.3112.113 Safari/537.36"')

    browser = webdriver.Chrome(r'C:/Users/chen/AppData/Local/Google/Chrome/Application/chromedriver',chrome_options=option)
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
        # 点击网页页面业绩报表
        result1=WebDriverWait(browser, 10).until(EC.presence_of_element_located((
                By.XPATH, "//li[contains(text(),'业绩报表')]"))).click()  # 元素加载出，传入定位元组，如(By.ID, 'p')
        time.sleep(1)
        # 点击网页页面 沪深A股
        result2=WebDriverWait(browser, 30).until(EC.presence_of_element_located((
                By.XPATH,"//*[text()='沪深A股']"))).click()  # 直接查找页面当中所有的”沪深A股“，不用知道它是什么元素。

        while True :
            html_content = BeautifulSoup(browser.page_source, "html.parser")
            all_tr_content = html_content.find('table', id='dt_1').find('tbody').find_all('tr')

            for tr in all_tr_content:
                all_ta_content = tr.find_all('td')
                temp_list = [all_ta_content[1].get_text(),all_ta_content[2].get_text(),
                             all_ta_content[5].get_text(),all_ta_content[8].get_text(),all_ta_content[12].get_text()]

                temp_content = Series(temp_list,index=column_name)
                file_content = file_content.append(temp_content,ignore_index=True)

            browser.execute_script("window.scrollBy(0,document.body.scrollHeight)", "")  # 向下滚动到页面底部
            time.sleep(1)
            nextPage = WebDriverWait(browser, 10).until(EC.presence_of_element_located((
                By.XPATH, "//a[contains(text(),'下一页')]")))

            if nextPage.get_attribute('class') == 'nolink':
                break
            nextPage.click()
            time.sleep(5)

        # 保存数据位.csv文件
        file_content.to_csv(file_name,encoding='utf-8')
        # 将DataFrame内容清空
        file_content.drop(file_content.index,inplace=True)


def data_deal():
    """
    得到上市满三年，每年roe大于8%的上市公司
    :return:
    """
    file_path = r'F:\git\public_company_analysis'
    file_name = 'result.csv'
    dataframe_2015 = pd.read_csv(file_path + r'\201512.csv',index_col=0,converters = {u'股票代码':str})
    dataframe_2016 = pd.read_csv(file_path + r'\201612.csv', index_col=0, converters={u'股票代码': str})
    dataframe_2017 = pd.read_csv(file_path + r'\201712.csv', index_col=0, converters={u'股票代码': str})

    column_name = ['code', 'name', 'income_2015', 'profit_2015', 'roe_2015(%)','income_2016', 'profit_2016',
                   'roe_2016(%)','income_2017', 'profit_2017', 'roe_2017(%)']
    file_content = DataFrame(columns=column_name)  # 创建空 DataFrame

    # 遍历2015年的上市公司
    for i in range(0,len(dataframe_2015)-1):
        roe2015 = dataframe_2015.iloc[i][4]  # 得到2015年 roe
        # 对缺失值做处理
        if roe2015 == '' or roe2015 == '-':
            roe2015 = '0'
        roe2015 = float(roe2015)
        company_name = dataframe_2015.iloc[i][1]

        if roe2015 >= 8.0:  # 规定只分析roe大于8的上市公司
            code = dataframe_2015.iloc[i][0]  # 得到股票代码
        else:  # 继续下一个公司
            continue

        # 遍历2016年的上市公司，寻找股票代码相同的公司
        for j in range(0, len(dataframe_2016) - 1):
            status_indict = 0  # 状态标志
            if code == dataframe_2016.iloc[j][0]:
                roe2016 = dataframe_2016.iloc[j][4]
                # 对缺失值做处理
                if roe2016 == '' or roe2016 == '-':
                    roe2016 = '0'
            else:  # 继续下一个公司对比
                continue
            roe2016 = float(roe2016)
            if roe2016 < 8.0:  # 当不满足roe要求时，直接跳出循环
                break

            # 遍历2017年的上市公司，寻找股票代码相同的公司
            for k in range(0, len(dataframe_2017) - 1):
                if code == dataframe_2017.iloc[k][0]:
                    roe2017 = dataframe_2017.iloc[k][4]
                    # 对缺失值做处理
                    if roe2017 == '' or roe2017 == '-':
                        roe2017 = '0'
                else:
                    continue
                roe2017 = float(roe2017)
                if roe2017 < 8.0:
                    status_indict = 1
                    break  # 当不满足roe要求时，直接跳出循环

                temp_list = [code, company_name, dataframe_2015.iloc[i][2], dataframe_2015.iloc[i][3], roe2015,
                             dataframe_2016.iloc[j][2], dataframe_2016.iloc[j][3], roe2016,
                             dataframe_2017.iloc[k][2], dataframe_2017.iloc[k][3], roe2017]
                temp_content = Series(temp_list, index=column_name)
                file_content = file_content.append(temp_content, ignore_index=True)
                print('continue')

            if status_indict == 1:
                break

    # 存储csv文件
    file_content.to_csv(file_name, encoding='utf-8')
    print('ok')


if __name__ == '__main__':
    # crawel_east_money()
    data_deal()

    pass
