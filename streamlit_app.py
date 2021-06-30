import streamlit as st
from nsepython import *
import pandas as pd
from time import strptime
from datetime import datetime, timedelta
import json
from stqdm import stqdm
import time
import numpy as np

def curl_nse_fetch(symbol):
    command = "curl 'https://www.nseindia.com/api/option-chain-equities?symbol="+symbol+"' \
  -H 'authority: www.nseindia.com' \
  -H 'sec-ch-ua: \" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36' \
  -H 'accept: */*' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-dest: empty' \
  -H 'referer: https://www.nseindia.com/option-chain' \
  -H 'accept-language: en-US,en;q=0.9,hi;q=0.8' \
  --compressed"
    return json.loads(os.popen(command).read())['filtered']['data']

def convert_date(date_string):
    date,month,year = date_string.split('-')
    month = str(strptime(month,'%b').tm_mon)
    return '-'.join([date,month,year])

def get_30_days_low_high(symbol):
    series = "EQ"
    start_date = (datetime.today() - timedelta(days=30)).strftime("%d-%m-%Y")
    end_date = datetime.today().strftime("%d-%m-%Y")
    return 0,0
    df = equity_history(symbol,series,start_date,end_date)
    if len(df) == 0:
        return 0,0
    low_price = min(df['CH_TRADE_LOW_PRICE'])
    high_price = max(df['CH_TRADE_HIGH_PRICE'])
    return low_price,high_price

def get_underlying_from_data(data):
    if 'PE' in data[0]:
        ltp = data[0]['PE']['underlyingValue']
    elif 'CE' in data[0]:
        ltp = data[0]['CE']['underlyingValue'] 
    return ltp

def get_atm_strike_from_data(data):
    if 'PE' in data[0]:
        ltp = data[0]['PE']['underlyingValue']
    elif 'CE' in data[0]:
        ltp = data[0]['CE']['underlyingValue'] 
    strike_price_list = [x['strikePrice'] for x in data]
    atm_strike = sorted([[round(abs(ltp-i),2),i] for i in strike_price_list])[0][1]
    return atm_strike

def get_pe_ce_price_from_data(data,atm_strike):
    for dictt in data:
        if dictt['strikePrice'] ==atm_strike:
            pe_price = dictt['PE']['askPrice']
            ce_price = dictt['CE']['askPrice']
    return pe_price,ce_price

def get_oi_from_data(data,atm_strike):
    for dictt in data:
        if dictt['strikePrice'] ==atm_strike:
            return dictt['PE']['openInterest']

def load_stocks(list_stocks):
    result_list = []
    for symbolname in stqdm(list_stocks):
        symbolname = symbolname.upper()
        #st.write(symbolname)
        # latest_iteration.text(f'Iteration {i+1}')
        # bar.progress(i + 1)
        running = True
        success = False
        start_time = time.time()
        seconds = 4
        while running:
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time > seconds:
                running = False
            try:
               data = curl_nse_fetch(symbolname)
               # st.write(symbolname)
               running=False
               success = True
            except:
                pass
        if success == False:
            continue
        atm_strike = get_atm_strike_from_data(data)
    #     print(atm_strike)
        lot_size = nse_get_fno_lot_sizes(symbolname)
        # month_low,month_high = get_30_days_low_high(symbolname)
        underlying_value = get_underlying_from_data(data)
        pe_price,ce_price = get_pe_ce_price_from_data(data, atm_strike)
        percent_premium = (pe_price+ce_price)/underlying_value*100
        result_list.append([symbolname,underlying_value,lot_size,atm_strike,pe_price,ce_price, percent_premium])
    return result_list

def main():
    st.title('FnO Premium Screener')
    most_active_fno = pd.read_csv('most_active_fno.tsv',sep='\t')

    fno_stocks = most_active_fno.symbolname.values
    result_list = []
    step_size = 10
    st.write('Getting straddle premiums of top stocks!!!')
    if st.sidebar.button("Load first time"):
        start_index = len(result_list)
        end_index = start_index+step_size
        if end_index < len(fno_stocks):
            result_list.extend(load_stocks(fno_stocks[start_index:end_index]))
    
        result_df = pd.DataFrame(result_list)
        result_df.columns = ['symbolname', 'underlyingValue','lot_size', 'atm_strike', 'pe_price','ce_price','percent_premium']
        result_df = result_df.sort_values('percent_premium',ascending=False).reset_index(drop=True)
        st.table(result_df.style.set_precision(2))
        result_df.to_csv('temp.tsv',sep='\t',index=False)
        num_val_df = pd.DataFrame([end_index])
        num_val_df['columns'] = ['num_vals']
        num_val_df.to_csv('temp1.tsv',sep='\t',index=False)

    if st.sidebar.button("Load more"):
        result_df = pd.read_csv('temp.tsv',sep='\t')
        num_vals = int((pd.read_csv('temp1.tsv',sep='\t').values)[0][0])
        #st.write(len(result_df))
        result_list = result_df.values
        #st.write(result_list)
        start_index = num_vals
        end_index = start_index+step_size
        if end_index < len(fno_stocks):
            new_result = np.array(load_stocks(fno_stocks[start_index:end_index]))
            #st.write(new_result)
            result_list = np.r_[result_list,new_result]
    
        result_df = pd.DataFrame(result_list)
        result_df.columns = ['symbolname', 'underlyingValue','lot_size', 'atm_strike', 'pe_price','ce_price','percent_premium']
        result_df['percent_premium'] = result_df['percent_premium'].astype(float)
        result_df = result_df.sort_values('percent_premium',ascending=False).reset_index(drop=True)
        result_df.to_csv('temp.tsv',sep='\t',index=False)
        st.table(result_df.style.set_precision(2))
        num_val_df = pd.DataFrame([end_index])
        num_val_df['columns'] = ['num_vals']
        num_val_df.to_csv('temp1.tsv',sep='\t',index=False)


if __name__ == "__main__":
    main()
