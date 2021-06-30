import streamlit as st
from nsepython import *
import pandas as pd
from time import strptime
from datetime import datetime, timedelta

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
	    print(symbolname)
	    option_chain_json = nse_optionchain_scrapper(symbolname)
	    data = option_chain_json['filtered']['data']
	    atm_strike = get_atm_strike_from_data(data)
	#     print(atm_strike)
	    lot_size = nse_get_fno_lot_sizes(symbolname)
	    month_low,month_high = get_30_days_low_high(symbolname)
	    underlying_value = get_underlying_from_data(data)
	    pe_price,ce_price = get_pe_ce_price_from_data(data, atm_strike)
	    percent_premium = (pe_price+ce_price)/underlying_value*100
	    result_list.append([symbolname,underlying_value,lot_size,month_low,month_high,atm_strike,pe_price,ce_price, percent_premium])
	result_df = pd.DataFrame(result_list)
	result_df.columns = ['symbolname', 'underlyingValue','lot_size','month_low','month_high', 'atm_strike', 'pe_price','ce_price','percent_premium']
	result_df = result_df.sort_values('percent_premium',ascending=False)
	st.table(result_df)

if __name__ == "__main__":
    main()