import pandas as pd 
import numpy as np
from pandas_datareader import data, wb
import pandas_datareader as pdr
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
import datetime
import math
import os

base = 2          # 변수
 
def square(n):    # 함수
    return base ** n

# cache 사용하여 종목 리스트 가져오기
def get_stock_listing_data():
    path = f'data/stock_listing.json'
    
    if (os.path.isfile(path)):
        #print("get_stocking_listing_data(): exist yes")
        stock_listing_data = pd.read_json(path, orient ='split', compression = 'infer')
    else:
        #print("get_stocking_listing_data(): exist no")
        stock_listing_data = fdr.StockListing('KRX') # 한국거래소 상장종목 전체 - KRX, KOSPI, KOSDAQ
        stock_listing_data.to_json(path, orient = 'split', compression = 'infer', index = 'true')
    return stock_listing_data

def get_stock_listing_dict(count, exclude_code_list=[]):
    stock_listing_dict = { }
    stock_listing_data = get_stock_listing_data()
    stock_listing_kospi = stock_listing_data[stock_listing_data['Market'] == 'KOSPI']
    stock_listing_kospi = stock_listing_kospi[stock_listing_kospi['Sector'].notnull()]
    stock_listing_100 = stock_listing_kospi[0:count]
    
    for idx, row in stock_listing_100.iterrows():
        code = row['Symbol'] + ".KS"
        if (code not in exclude_code_list):
            stock_listing_dict[code] = { "code": code, "stock_name": row['Name']}
    return stock_listing_dict

# TODO memory cache?
def get_stock_name(code):
    icode = code
    if (code.find(".KS")):
        icode = code.replace(".KS", "")
    elif (code.find(".KQ")):
        icode = code.replace(".KQ", "")
        
    stock_listing_data = get_stock_listing_data()
    df = stock_listing_data[stock_listing_data['Symbol'] == icode]
    if (len(df) > 0):
        return df.iloc[0]['Name']
    return "Unknown"

# cache 사용하여 종목 데이터 가져오기
def get_stock_data(code, start_time, end_time, use_fdr=False):
    # 무조건 1년 단위로 자름
    start_time = datetime.datetime(start_time.year, 1, 1)
    end_time = datetime.datetime(start_time.year, 12, 31)
    #print("get_stock_data():", "start_time=", start_time, "end_time=", end_time)
    
    year = start_time.year
    path = f'data/{year}/{code}.json'
    
    stock_data = pd.DataFrame()
    if (os.path.isfile(path)):
        #print("get_stock_data(): exist yes")
        stock_data = pd.read_json(path, orient ='split', compression = 'infer')
    else:
        #print("get_stock_data(): exist no")
        if (use_fdr):
            stock_data = fdr.DataReader(code, start_time, end_time)
            stock_data.to_json(path, orient = 'split', compression = 'infer', index = 'true')
        else:
            try:
                stock_data = pdr.data.get_data_yahoo(code, start_time, end_time)
                stock_data.to_json(path, orient = 'split', compression = 'infer', index = 'true')
            except KeyError:
                print("get_stock_data(): KeyError code=", code)
                stock_data.to_json(path, orient = 'split', compression = 'infer', index = 'true')
                pass
    return stock_data

# 하반기 종목 데이터 가져오기
def get_stock_data_second_half(code, start_time, end_time, use_fdr=False):
    stock_data = get_stock_data(code, start_time, end_time, use_fdr)
    half_iloc = int(len(stock_data)/2)
    return stock_data[half_iloc:-1]

