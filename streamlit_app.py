import streamlit as st
from nsepython import *
import pandas as pd
from time import strptime
from datetime import datetime, timedelta
import json

def curl_nse_fetch(symbol):
    command = "curl 'https://www.nseindia.com/api/option-chain-equities?symbol=RELIANCE' \
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
    return json.loads(os.popen(command).read())

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

def main():
	st.title('FnO Premium Screener')
	most_active_fno = pd.read_csv('most_active_fno.tsv',sep='\t')

	fno_stocks = most_active_fno.symbolname.values
	result_list = []
	for symbolname in fno_stocks[:10]:
	    symbolname = symbolname.upper()
	    st.write(symbolname)
	#     option_chain_json = curl_nse_fetch(symbolname)
	#     if 'filtered' not in option_chain_json:
	#     	continue
	#     data = option_chain_json['filtered']['data']
	#     atm_strike = get_atm_strike_from_data(data)
	# #     print(atm_strike)
	#     lot_size = nse_get_fno_lot_sizes(symbolname)
	#     month_low,month_high = get_30_days_low_high(symbolname)
	#     underlying_value = get_underlying_from_data(data)
	#     pe_price,ce_price = get_pe_ce_price_from_data(data, atm_strike)
	#     percent_premium = (pe_price+ce_price)/underlying_value*100
	#     result_list.append([symbolname,underlying_value,lot_size,month_low,month_high,atm_strike,pe_price,ce_price, percent_premium])
	# result_df = pd.DataFrame(result_list)
	# result_df.columns = ['symbolname', 'underlyingValue','lot_size','month_low','month_high', 'atm_strike', 'pe_price','ce_price','percent_premium']
	# result_df = result_df.sort_values('percent_premium',ascending=False).reset_index(drop=True)
	# st.table(result_df)

if __name__ == "__main__":
    main()
