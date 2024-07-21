from selenium import webdriver
import time 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re

#住所の分割
def divide_address(address):
    
    if re.findall(r'(...??[都道府県])', address):
        prefecture = re.findall(r'(...??[都道府県])', address)[0]
    else:
        prefecture = ''

    if re.findall(r'([0-9].*[0-9])', address):
        banti = re.findall(r'([0-9].*[0-9])', address)[0]
    else:
        banti = ''
    
    city = re.sub(prefecture, '', address)
    city = re.sub(banti, '', city)

    return [prefecture, city, banti]

options = Options()
options.add_argument('--headless')
options.add_argument(f'--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"')

#店舗ページ一覧から個別ページのURLを取得
driver = webdriver.Chrome(options=options)

detail_page_url_list = []
pagenum = 1

URL = 'https://r.gnavi.co.jp/area/jp/rs/'
time.sleep(3)
driver.get(URL)

while True:
    
    elems = driver.find_elements(by=By.CSS_SELECTOR, value='article')
    if pagenum == 3:
        elems_num = 10
    else:
        elems_num = 20
   
    for i in range(elems_num):
        url = elems[i].find_element(by=By.CLASS_NAME, value='style_titleLink__oiHVJ')
        detail_page_url_list.append(url.get_attribute('href'))
    
    #ページの遷移
    time.sleep(3)
    page_move = driver.find_element(by=By.CLASS_NAME, value='style_pages__Y9bbR')
    page_move.find_elements(by=By.CSS_SELECTOR, value="li")[-2].find_element(by=By.CSS_SELECTOR, value='a').click()

    
    if pagenum == 3:
        driver.quit()
        break
    pagenum += 1

#取得した個別ページのURLから店舗の情報を抽出
data = []
driver = webdriver.Chrome(options=options)

for detail_url in detail_page_url_list:
    
    time.sleep(3)
    driver.get(detail_url)
    
    name = driver.find_element(by=By.ID, value="info-name").text
    number = driver.find_element(by=By.CLASS_NAME, value="number").text
    address = driver.find_element(by=By.CLASS_NAME, value="region").text

    try:
        building = driver.find_element(by=By.CLASS_NAME, value="locality").text
    except:
        building = ''
    
    try:
        home_page_url = driver.find_element(by=By.LINK_TEXT, value="オフィシャル\nページ").get_attribute('href')
    except:
        home_page_url = ''
    
    pattern = re.compile(r'^https')
    if (home_page_url == ''):
        SSL = ''
    else:
        SSL = bool(pattern.search(home_page_url))
    

    data_tmp = {}

    data_tmp['店舗名'] = name.replace('\xa0', '').replace('\uff5e', '')
    data_tmp['電話番号'] = number
    data_tmp['メールアドレス'] = ''
    address_list = divide_address(address.replace('\xa0', ''))
    data_tmp['都道府県'] = address_list[0]
    data_tmp['市区町村'] = address_list[1]
    data_tmp['番地'] = address_list[2]
  
    data_tmp['建物名'] = building.replace('\xa0', '').replace('\uff5e', '')
    data_tmp['URL'] = home_page_url
    data_tmp['SSL'] = SSL

    data.append(data_tmp)

driver.quit()

#データフレームの作成とcsvへの出力
df = pd.DataFrame(data)
df.to_csv('1-2.csv', encoding='shift-jis')