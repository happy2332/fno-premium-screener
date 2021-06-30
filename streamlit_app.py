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
	st.write('Most active FnO')
	st.table(most_active_fno)

if __name__ == "__main__":
    main()