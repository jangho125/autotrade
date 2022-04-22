import ccxt
import larrybybit
import time
import datetime
import bestk



api_key = "gjNFGc1OwP5s8LOaZR"
secret = "h9IwB4c07TOh8dT9hMB1nDhOSJH3ntGuvvtk"


# binance 객체 생성
bybit = ccxt.bybit(config={
    'apiKey' : api_key,
    'secret' : secret,
    'enableratelimit' : True,
    'options' : {'defaultType' : 'future'}
})




symbol = "BTC/USDT"
timeframe = '4h'
fees = 0.0007
leverage = 3


balance = bybit.fetch_balance()
usdt_balance = balance['total']['USDT']
buy_average = larrybybit.get_avg_price(bybit, symbol)
long_crr = bestk.get_best_long_crr(symbol, fees)
short_crr = bestk.get_best_short_crr(symbol, fees)
highest_value = larrybybit.highest_value(bybit, symbol)
lowest_value = larrybybit.lowest_value(bybit, symbol)

print(usdt_balance)

position = {
    "type": None,
    "amount": 0
}


while True:
    
    start_time = larrybybit.get_start_time(bybit, symbol, timeframe) 
    now = datetime.datetime.now() 
    end_time = start_time + datetime.timedelta(minutes=240) - datetime.timedelta(seconds=20) # 매매 시작
    time.sleep(1)
    print(start_time)
    print(now)
    print(end_time)    
        
    if start_time < now < end_time:
        long_target, short_target = larrybybit.cal_target(bybit, symbol)
        
        
        
        i = 0
        while i < 4:
            now = datetime.datetime.now()
            btc = bybit.fetch_ticker(symbol)
            cur_price = btc['last']
            amount = larrybybit.cal_amount(usdt_balance, cur_price, leverage)
            time.sleep(1)
            
           
            print("script is running")
            
            
            
            # 1차 매수
            
            if i == 0 and (long_target -100) <= cur_price < (long_target + 100) and long_crr > 1:
                position['type'] = 'long'
                position['amount'] = amount
                bybit.create_market_buy_order(symbol, amount * 0.25)
                time.sleep(1)
                buy_average = larrybybit.get_avg_price(bybit, symbol)
                i += 1
                print("1차 LONG 매수 성공")
            elif i == 0 and (short_target - 100) <= cur_price < (short_target + 100) and short_crr > 1:
                position['type'] = 'short'
                position['amount'] = amount
                bybit.create_market_sell_order(symbol, amount * 0.25)
                time.sleep(1)
                buy_average = larrybybit.get_avg_price(bybit, symbol)
                i += 1
                print("1차 SHORT 매수 성공")
                
            
            # 2차 매수    
            
            if i == 1 and cur_price < float(buy_average) * 0.94:
                position['type'] = 'long'
                position['amount'] = amount
                bybit.create_market_buy_order(symbol, amount * 0.25)
                time.sleep(1)
                buy_average = larrybybit.get_avg_price(bybit, symbol)
                i += 1
                print("2차 LONG 매수 성공")
            elif i == 1 and cur_price > float(buy_average) * 1.06:
                position['type'] = 'short'
                position['amount'] = amount
                bybit.create_market_sell_order(symbol, amount * 0.25)
                time.sleep(1)
                buy_average = larrybybit.get_avg_price(bybit, symbol)
                i += 1
                print("2차 SHORT 매수 성공")
                
                
            # 3차 매수
            
            if i == 2 and cur_price < float(buy_average) * 0.94:
                position['type'] = 'long'
                position['amount'] = amount
                bybit.create_market_buy_order(symbol, amount * 0.5)
                time.sleep(1)
                buy_average = larrybybit.get_avg_price(bybit, symbol)
                i += 1
                print("3차 LONG 매수 성공")
            elif i == 2 and cur_price > float(buy_average) * 1.06:
                position['type'] = 'short'
                position['amount'] = amount
                bybit.create_market_sell_order(symbol, amount * 0.5)
                time.sleep(1)
                buy_average = larrybybit.get_avg_price(bybit, symbol)
                i += 1  
                print("3차 SHORT 매수 성공")
                
            
            # 매도 조건
            
            if i == 3 and cur_price < float(buy_average) * 0.95:
                if position['type'] == 'long':
                    bybit.create_market_sell_order(symbol, amount)
                    time.sleep(1)
                    position['type'] == None
                    print("3차 LONG 매수 후 5% 손절")
                
            elif i == 3 and cur_price > float(buy_average) * 1.05:
                if position['type'] == 'short':
                    bybit.create_market_buy_order(symbol, amount)
                    time.sleep(1)
                    position['type'] == None
                    print("3차 SHORT매수 후 5% 손절")
            
            if cur_price > float(buy_average) * 1.06:
                if i == 0:
                    amount = position['amount'] * 0.25
                elif i == 1:
                    amount = position['amount'] * 0.5
                elif i == 2:
                    amount = position['amount'] 
                elif i == 3:
                    amount = position['amount'] 
                    
                price = highest_value * 0.97
                if position['type'] == 'long':
                    bybit.create_limit_sell_order(symbol, amount, price)
                    time.sleep(1)
                    position['type'] == None
                    print("LONG 익절")
                    
            elif cur_price < float(buy_average) * 0.94:
                if i == 0:
                    amount = position['amount'] * 0.25
                elif i == 1:
                    amount = position['amount'] * 0.5
                elif i == 2:
                    amount = position['amount'] 
                elif i == 3:
                    amount = position['amount']    
                
                price = lowest_value * 1.03
                if position['type'] == 'short':
                    bybit.create_limit_buy_order(symbol, amount, price)
                    time.sleep(1)
                    position['type'] == None
                    print("SHORT 익절")
            
            # 매매 종료
            
            if now > end_time:
                if i == 0:
                    amount = position['amount'] * 0.25
                elif i == 1:
                    amount = position['amount'] * 0.5
                elif i == 2:
                    amount = position['amount'] 
                elif i == 3:
                    amount = position['amount']
                    
                if position['type'] == 'long':
                    bybit.create_market_sell_order(symbol, amount)
                    time.sleep(1)
                    position['type'] == None
                    print("4시간 후 LONG 매도")
                    
                    break 
                
                elif position['type'] == 'short':
                    bybit.create_market_buy_order(symbol, amount)
                    time.sleep(1)
                    position['type'] == None
                    print("4시간 후 SHORT 매도")
                    
                    break
            
    
   
        

   
    
    

    
