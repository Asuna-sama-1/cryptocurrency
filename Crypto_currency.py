# -*- coding: utf-8 -*-
"""cryto_currency.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ByjgB7kHlsODkJCZJO6HeP5f-GrSmrfX
"""

import requests         
from bs4 import BeautifulSoup 
import pandas as pd      
from datetime import datetime

import json

raw_header='''User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'''

headers = dict([line.split(": ",1) for line in raw_header.split("\n")])

"""## Web Scarp

### Coin names
"""

all_data=[]

from datetime import datetime

for i in range(1,57):
    url= 'https://coinmarketcap.com/?page='+str(i)
    response  = requests.get(url, headers=headers).text   
    soup =  BeautifulSoup(response)
    # soup.prettify()
    data = soup.find('script',id="__NEXT_DATA__").get_text()
    jsdata = json.loads(data)
    list_data = jsdata['props']['initialState']['cryptocurrency']['listingLatest']['data']
    all_data.extend(list_data)
    print(i)

df = pd.DataFrame(all_data)

df.to_csv('all_data_01.csv')

#df

df = pd.read_csv('all_data_01.csv')

# https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id=8000&convertId=2785&timeStart=1367078400&timeEnd=1622764800

urls = ['https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id={0}&convertId=2785&timeStart=1367078400&timeEnd=1622764800'.format(i) for i in df['id'].tolist()]

urls[0]

"""### All Data"""

import os,time

dn = len(os.listdir('data/'))
dn

num=dn
for url in urls[dn:]:
    response  = requests.get(url).text
    jsdata = json.loads(response)
    name = jsdata['data']['name'].replace('/',' ')
    quote = [i['quote'] for i in  jsdata['data']['quotes']]
    df = pd.DataFrame(quote)
    df.to_csv('data/'+name+'.csv')
    time.sleep(3)
    num+=1
    print(num,name,'Done!')

"""## lcoal saving"""

dfs=[]
for i in os.listdir('data/'):
    try:   
        df = pd.read_csv('data/'+i)
        df['name']=i.strip('.csv')
        dfs.append(df)
    except:
        pass
#         print('data/'+i)

df = pd.concat(dfs,axis=0)

df.head()

df.to_csv('all_data.csv')

"""## Local read and analyze"""

df_all = pd.read_csv('all_data.csv')

df_all = df_all.drop(['Unnamed: 0','Unnamed: 0.1'],axis=1)

df_all.head()

df_all.tail()

"""### Filter out volume <500000(2020/01/01- current)"""

# change to timestamp 
df_all['timestamp'] =  pd.to_datetime(df_all['timestamp'], format='%Y-%m-%dT%H:%M:%S.%f%z')

# fillter acoin coin's sum(volume) <500000
year_2020= df_all.loc[df_all['timestamp'] > '2020-01-01 23:59:59.999000+00:00'] # select date range
s=year_2020.groupby('name').volume.agg(['sum'])
s=s[s['sum']<500000]               # calculate coin's sum(volume) <500000 for each coins 
s=s.reset_index()
#print(len(year_2020))

filtered = year_2020[~year_2020['name'].isin(s['name'])]

# join tables 

df_all_filtered = pd.concat ([df_all.loc[df_all['timestamp'] <= '2020-01-01 23:59:59.999000+00:00'],filtered])
len(df_all_filtered)

"""### Remove coin's total days is below 180"""

group=df_all_filtered.groupby('name').timestamp.agg(['count'])
count=group[group['count']<180].reset_index()         
final_df = df_all_filtered[~df_all_filtered['name'].isin(count['name'])]
final_df

"""### Replace 0 and NA values"""

final_df.isnull().sum()#check for null values

# replace 0 value with the previous valid value
for i in final_df:
    final_df[i]=final_df[i].mask(final_df[i]== 0).ffill(downcast='infer')

    
final_df.describe()

