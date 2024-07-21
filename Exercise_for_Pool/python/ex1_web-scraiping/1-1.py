import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import time

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

#ユーザーエージェントの設定
headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
}

#店舗ページ一覧から個別ページのURLを取得
detail_page_url_list = []
pagenum = 1

while True:

    URL = 'https://r.gnavi.co.jp/area/jp/rs/?p={0}'.format(pagenum)
    time.sleep(3)
    res = requests.get(URL, headers=headers)

    soup = BeautifulSoup(res.text, 'html.parser')

    elems = soup.find_all('article')
    elems_a = soup.find_all("a", attrs={"class": "style_titleLink__oiHVJ"})
    
    #1, 2ページからそれぞれ20レコード, 3ページから10レコード取得
    if pagenum == 3:
        elems_num = 10
    else:
        elems_num = 20
    
    for i in range(elems_num):
        detail_page_url_list.append(elems_a[i].attrs['href'])

    pagenum += 1
    
    if pagenum == 4:
        break

#取得した個別ページのURLから店舗の情報を抽出
data = []
for detail_url in detail_page_url_list:
    
    time.sleep(3)
    res = requests.get(detail_url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    number = soup.find(attrs={'class': 'number'}).get_text()
    name = soup.find(attrs={'id': 'info-name'}).get_text()
    address = soup.find(attrs={'class': 'region'}).get_text()
    if (soup.find(attrs={'class': 'locality'})):
        building = soup.find(attrs={'class': 'locality'}).get_text()
    else:
        building = ''
   
    data_tmp = {}

    data_tmp['店舗名'] = name.replace('\xa0', '').replace('\uff5e', '')
    data_tmp['電話番号'] = number
    data_tmp['メールアドレス'] = ''
    address_list = divide_address(address.replace('\xa0', '').replace('\uff5e', ''))
    data_tmp['都道府県'] = address_list[0]
    data_tmp['市区町村'] = address_list[1]
    data_tmp['番地'] = address_list[2]
    
    data_tmp['建物名'] = building.replace('\xa0', '').replace('\uff5e', '')
    data_tmp['URL'] = ''
    data_tmp['SSL'] = ''

    data.append(data_tmp)

#データフレームの作成とcsvへの出力
df = pd.DataFrame(data)
df.to_csv('1-1.csv', encoding='shift-jis')