import ccxt
import time
import datetime
import pandas as pd
import larry
import math


api_key = "2xc04G17wowEe1MWORfWDE4YSztgs75gTha3RVsNaYzCrMDikX7AzsoTHPB1VPZT"
secret = "H5Q8BgllV4uqBPfQqLWGv4O6rI6JZWIrWZ4b3VX5oLmJKk4AgIrAv4V7zwfmKHVX"

# binance 객체 생성
binance = ccxt.binance(config={
    'apiKey' : api_key,
    'secret' : secret,
    'enableratelimit' : True,
    'options' : {'defaultType' : 'future'}
})

symbol = "BTC/USDT"
long_target, short_target = larry.cal_target(binance, symbol)

# 잔고
balance = binance.fetch_balance()
usdt = balance['total']['USDT']

position = {
    "type": None,
    "amount": 0
}
op_mode = False


while True:
    # time
    now = datetime.datetime.now()
    
    #포지션 종료
    if now.hour ==8 and now.minute == 50 and (0<= now.second < 10):
       if op_mode and position['type'] is not None:
           larry.exit_position(binance, symbol, position)
           op_mode = False
        
    
    # 목표가 갱신
    if now.hour ==9 and now.minute == 0 and (20<= now.second < 30):
        long_target, short_target = larry.cal_target(binance, symbol)
        balance = binance.fetch_balance()
        usdt = balance['total']['USDT']
        op_mode = True
        time.sleep(10)
        
    # 현재가, 구매가능 수량 (10%)
    btc = binance.fetch_ticker(symbol=symbol)
    cur_price = btc['last']
    amount = larry.cal_amount(usdt, cur_price)
    
    if op_mode and position['type'] is None:
        larry.enter_position(binance, symbol, cur_price, long_target, short_target, amount, position)
        
   
    time.sleep(1)



   
    
    

    
