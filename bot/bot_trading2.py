import time, os
from math import *
from decimal import Decimal
from datetime import datetime
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import argrelextrema
import numpy

from datetime import datetime
#from binance.client import Client
#from binance.enums import  *
#from binance.exceptions import *

from pymexc import spot, futures

api_key = "mx0vglIVNeUoeMNiak"
api_secret = "2764b404e0ba4e509a9552900092e475"

import telebot


# SPOT V3
spot_client = spot.HTTP(api_key = api_key, api_secret = api_secret)

# initialize WebSocket client
ws_spot_client = spot.WebSocket(api_key = api_key, api_secret = api_secret)

# initialize HTTP client
futures_client = futures.HTTP(api_key = api_key, api_secret = api_secret)

# Telegram bot
bot = telebot.TeleBot("6043605591:AAG0IToSiVhG0KQxhUw2Yk0Ie76iPELmyfk")

#table = ['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_volume', 'Trades', 'Taker_base', 'Taker_quote', 'Ignore']

_symbol ='LINKUSDT'
period_argre = 31
gap = 0.25

backTest = True
isGetData = False
sendCap = False
isSendTelegram = True
isUI = False
isLoop = True
totalFee = 0
totalFeeUSDT = 0

amout = 0
totalDiff = 0
listBuys = []
totalBuys = []
totalSells = []

isLong = False
isStopLoss = False

countKline = 0
count = 0
oldMax = 0
buySell = 0
countBuys = 0
countSells = 0
table = []
isOpen = False
timeP = []
openP = []
highP = []
lowP = []
closeP = []
openTimes = 0
closePrices = 0
lastMin = 0
lastMax = 0
totalDiff = 0
priceBuy = 0
priceSell = 0
    
totalDay = 0
totalYears = 0
day = 0
cday = 0
years = 0
actualPriceCoin = 0

#fig = plt.figure(figsize=(12,6), facecolor='#DEDEDE')
#fig, ax = plt.subplots(figsize=(12, 6)) # nrows=2,
fig = ''
ax = ''
anin = None
backTest_interval = 5000
status = "running"
mode = 'simulation'
timeFrame = '1d'
lastKlineBuy = ''
maxAmout = 15

def StartBot():

    global status
    global mode
    global amout
    global backTest
    global totalDiff
    global isLong
    global count
    global countKline
    global buySell
    global table
    global _symbol
    global isOpen
    global isStopLoss
    global isGetData
    global priceBuy
    global priceSell
    global countBuys
    global countSells
    global openTimes
    global closePrices
    global lastMin
    global lastMax
    global listBuys
    global totalBuys
    global totalSells
    global totalDiff
    global totalDay
    global totalYears
    global day
    global cday
    global years
    global sendCap
    global backTest_interval  
    global ax
    global fig
    global isUI
    global isLoop
    global actualPriceCoin
    global totalFee
    global totalFeeUSDT
    global isSendTelegram
    global lastKlineBuy
    global gap
    global maxAmout
    
    while isLoop:
        
        status = "running"
        klines = []
        timeP = []
        openP = []
        highP = []
        lowP = []
        closeP = []
        
        mins = []
        maxs = []
        
        initialAmout = 500
        maxPerOperation = 5.0
        brokerFee = 0.001
        totalFee = 0.0
        
        df = pd.DataFrame(columns=['Open_time', 'Open', 'High', 'Low', 'Close'])
        
        #if isGetData == False:
            
        # kLines
        klines = spot_client.klines(symbol='LINKUSDT', interval=timeFrame, limit=100)
        #orderBook = spot_client.order_book(symbol='LINKUSDT', limit=5)
        #df = pd.DataFrame(columns=['Open_time','Close'])
        
        #account_info = spot_client.account_information()
        
        actualPriceCoin = float(klines[len(klines)-1][4])
        
        # Calculate Fee Broker cost link
        totalFee = "{0:.3f}".format((brokerFee * maxPerOperation))
        #print(totalFee)
        
        # Calculate estimate fee usdt
        totalFeeUSDT = "{0:.3f}".format((actualPriceCoin * float(totalFee)))
        #print(totalFeeUSDT)
        
        #print(totalFee)
        
        #isGetData = True
        #backTest = True
        
        #if os.path.exists("captura.png"):
        #    os.remove("captura.png")
        
        #bot.send_photo(179291648, photo=open('foo.png', 'rb'))
        
        if backTest:
            
            for kline in klines:
                timeP.append(float(kline[0]))
                openP.append(float(kline[1]))
                highP.append(float(kline[2]))
                lowP.append(float(kline[3]))
                closeP.append(float(kline[4]))
                
            # Set data to pandas 
            df["Open_time"] = pd.Series(timeP)
            df["Open"] = pd.Series(openP)
            df["High"] = pd.Series(highP)
            df["Low"] = pd.Series(lowP)
            df["Close"] = pd.Series(closeP)

            if isGetData == False:
                lastKlineBuy = pd.to_datetime(df['Open_time'][len(df['Open_time'])-1], unit='ms', utc=True)
                print("Date Copy: {0}".format(lastKlineBuy.tz_convert('Europe/Berlin')))
                #listBuys.append(14.686)
                isGetData = True
            
            # Argrelextrema
            df['Min'] = df.iloc[argrelextrema(df['Close'].values, np.less_equal, order=period_argre)[0]]['Close']
            df['Max'] = df.iloc[argrelextrema(df['Close'].values, np.greater_equal, order=period_argre)[0]]['Close']
            
            df["SMA_5"] = df["Close"].rolling(window=5).mean()
            df["SMA_200"] = df["Close"].rolling(window=200).mean()
            
            mins = argrelextrema(df['Close'].values, np.less_equal, order=period_argre)[0]
            maxs = argrelextrema(df['Close'].values, np.greater_equal, order=period_argre)[0]
            
            if mins[len(mins)-1] == 99:
                
                if amout < maxAmout:
                    
                    priceBuy =  df['Close'][len(df['Close'])-1]
                    dateBuy =  pd.to_datetime(df['Open_time'][len(df['Open_time'])-1], unit='ms', utc=True)
                    
                    if lastKlineBuy < dateBuy.tz_convert('Europe/Berlin'):
                        lastKlineBuy = dateBuy.tz_convert('Europe/Berlin')
                        
                        if len(listBuys) > 0:
                            
                            found = numpy.isclose(priceBuy, listBuys, rtol=1e-05, atol=1e-08, equal_nan=False)
                            
                            #print("Buy List")
                            #print(priceBuy)
                            #print(found[0])
                            
                            if found[0]:
                                    print("Existe")
                            else:
                                print("Price Buy: {0}".format(priceBuy))
                            
                                amout += maxPerOperation
                            
                                listBuys.append(priceBuy)
                                countBuys += 1
                                
                                if isSendTelegram:
                                    bot.send_message('-4116577296', "Symbol: LINK/USDT" \
                                        + "\nSignal Buy" \
                                        + "\nAmout: {0}".format(maxPerOperation) \
                                        + "\nPrice: {0}".format(priceBuy) \
                                        + "\nU. O. Fee: {0:.3f}€".format(float(totalFeeUSDT)) \
                                        + "\nU. Buy. Cost: {0:.2f}€".format(priceBuy * maxPerOperation) \
                                        + "\nDate: {0}".format(dateBuy.tz_convert('Europe/Berlin')))        
                        else:
                            print("Price Buy: {0}".format(priceBuy))

                            amout += maxPerOperation
                    
                            listBuys.append(priceBuy)
                            countBuys += 1
                        
                            if isSendTelegram: 
                                bot.send_message('-4116577296', "Symbol: LINK/USDT" \
                                        + "\nSignal Buy" \
                                        + "\nAmout: {0}".format(maxPerOperation) \
                                        + "\nPrice: {0}".format(priceBuy) \
                                        + "\nU. O. Fee: {0:.3f}€".format(float(totalFeeUSDT)) \
                                        + "\nU. Buy. Cost: {0:.2f}€".format(priceBuy * maxPerOperation) \
                                        + "\nDate: {0}".format(dateBuy.tz_convert('Europe/Berlin')))
            
            if maxs[len(maxs)-1] == 99:
                
                print('Signal Sell')    
                for buy in listBuys:
                    
                    idealSell = buy + ((float(totalFeeUSDT) + gap) * 2)
                    print("Ideal Sell: {0:.3f}".format(idealSell))
                    
                    
                    if df['Close'][len(df['Close'])-1] >= idealSell:
                        
                        print("Price Sell: {0} diff: {1:.02f}".format(idealSell, (idealSell - buy)))
                        
                        totalDiff += (idealSell - buy) * maxPerOperation
                        
                        totalDiff -= float(totalFeeUSDT) * 2
                        
                        amout -= maxPerOperation
                        countSells += 1
                        listBuys.remove(buy)
                            
                        dateSell = pd.to_datetime(df['Open_time'][len(df['Open_time'])-1], unit='ms', utc=True)
                        
                        if isSendTelegram:
                            bot.send_message('-4116577296', "Symbol: LINK/USDT" \
                                        + "\nSignal Sell" \
                                        + "\nAmout: {0}".format(maxPerOperation) \
                                        + "\nPrice: {0}".format(idealSell) \
                                        + "\nU. O. Fee: {0:.3f}€".format(float(totalFeeUSDT)) \
                                        + "\nU. Sell: {0:.2f}€".format(idealSell * maxPerOperation) \
                                        + "\nT. Diff: {0:.2f}€".format(totalDiff) \
                                        + "\nDate: {0}".format(dateSell.tz_convert('Europe/Berlin')))
                                    
            print("Init Amount: {0:.02f}€".format(initialAmout))
            print("Max Amount: {0} LINK/USDT".format(maxAmout))
            print("Max Operation: {0}".format(maxPerOperation))
            print("Actual Price: {0:.03f}".format(actualPriceCoin))
            print("Actual Amount: {0}".format(amout))
            print("Total Fee: {0}".format(totalFee))
            print("USDT Fee: {0}€".format(totalFeeUSDT))
            print("List Buys: {0}".format(len(listBuys)))
            print(listBuys)
            print("Total Buy: {0}".format(countBuys))
            print("Total Sell: {0}".format(countSells))
            
            finalDiffAmout =  ((initialAmout + totalDiff) / initialAmout) * 100
            print("Total Perc: {0:.02f} %".format(finalDiffAmout - 100))
            print("Total Diff: {0:.02f} €\n".format(totalDiff))
                
        if isUI:
            ax.cla()
            width=0.9
            width2=0.1
            pricesup=df[df['Close']>=df['Open']]
            pricesdown=df[df['Close']<df['Open']]
            ax.bar(pricesup.index,pricesup.Close-pricesup.Open,width,bottom=pricesup.Open,color='g')
            ax.bar(pricesup.index,pricesup.High-pricesup.Close,width2,bottom=pricesup.Close,color='g')
            ax.bar(pricesup.index,pricesup.Low-pricesup.Open,width2,bottom=pricesup.Open,color='g')
            ax.bar(pricesdown.index,pricesdown.Close-pricesdown.Open,width,bottom=pricesdown.Open,color='r')
            ax.bar(pricesdown.index,pricesdown.High-pricesdown.Open,width2,bottom=pricesdown.Open,color='r')
            ax.bar(pricesdown.index,pricesdown.Low-pricesdown.Close,width2, bottom=pricesdown.Close,color='r')
            
            #ax.cla()
            ax.scatter(df.Open_time.index, df['Min'], c='g', marker='^')
            ax.scatter(df.Open_time.index, df['Max'], c='r', marker='v')
            #ax.plot(df.index, df['SMA_5'], c='r')
            #ax.plot(df.index, df['SMA_200'], c='b')
            #ax.plot(df.index, df['Close'], c='k')
            ax.grid(alpha=0.2)
            #plt.show()
            fig.show()
            
            #facecolors = ['green' if y > 0 else 'red' for y in df['Close']]
            #edgecolors = facecolors
            
            # Normalize y values to get distinct face alpha values.
            #abs_y = [abs(y) for y in df['Close']]
            #face_alphas = [n / max(abs_y) for n in abs_y]
            #edge_alphas = [1 - alpha for alpha in face_alphas]
            #
            #colors_with_alphas = list(zip(facecolors, face_alphas))
            #edgecolors_with_alphas = list(zip(edgecolors, edge_alphas))
            #ax[1].bar(df.index, df['Close'], color=colors_with_alphas, edgecolor=edgecolors_with_alphas)
            
            #ax[1].set_title('Normalized alphas for\neach bar and each edge')
            #ax[1, 0].hist(df['Close'], density=True, histtype='barstacked', rwidth=0.8)
            #ax[1, 0].hist(df['Open_time'], density=True, histtype='barstacked', rwidth=0.8)
            #ax[1, 0].set_title('barstacked')
            
            #plt.gcf().autofmt_xdate()
        
        time.sleep(20)
    
    status = 'stop'
          
@bot.message_handler(commands=['start', 'stop', 'status'])
def start(message):
    
    global isLoop
    global status
    global listBuys
    global countBuys
    global countSells
    global actualPriceCoin
    global totalFee
    global totalFeeUSDT
    global timeFrame
    global gap
    global period_argre
    global maxAmout
    
    if isLoop:
        status = "running"
    else:
        status = 'stop'
        
    if message.text == '/start':
        if message.chat.id == -4116577296 or message.chat.id == 179291648:
            bot.send_message(message.chat.id, "Start Bot!!\nstatus: {0}\nmode:{1}".format(status, mode))
        else:
            bot.send_message(message.chat.id, "Este bot es para uso privado.")
            
    if message.text == '/stop':
        isLoop = False
        bot.send_message(message.chat.id, "Stop Bot!!\nstatus: {0}\nmode:{1}".format(status, mode))
        
    if message.text == '/status':
        bot.send_message(message.chat.id, "Symbol: LINK/USDT" \
                        + "\nStatus: {0}".format(status) \
                        + "\nMode: {0}".format(mode) \
                        + "\nTimeFrame: {0}".format(timeFrame) \
                        + "\nMax Amount: {0}".format(maxAmout) \
                        + "\nMax P. Operation: {0}".format(5) \
                        + "\nLINK Fee: {0}".format(totalFee) \
                        + "\nUSDT Fee: {0}".format(totalFeeUSDT) \
                        + "\nU. GAP: {0}".format(gap) \
                        + "\nP. Argre: {0}".format(period_argre) \
                        + "\nA. Price: {0}".format(actualPriceCoin) \
                        + "\nL. Buys: {0}".format(len(listBuys)) \
                        + "\nT. Buys: {0}".format(countBuys) \
                        + "\nT. Sells: {0}".format(countSells) \
                        + "\nT. Diff: {0}".format(totalDiff))
    
    #if message.text == '/buy':
    #    bot.send_message(message.chat.id, "Symbol: LINK/USDT" \
    #                    + "\nAmout: {0}".format(5) \
    #                    + "\nPrice: {0}".format('14.78') \
    #                    + "\nDate: {0}".format('date'))

def LoopTelegram():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    
    t1 = threading.Thread(target=StartBot)
    t1.start()
    
    # Loop Bot
    t2 = threading.Thread(target=LoopTelegram)
    t2.start()
    
    # Loop Telegram
    #bot.polling(none_stop=True)
    
    #while True:
    #    bot.polling(none_stop=True)
    #    
    #    StartBot()
    #    
    #    time.sleep(5)
    
    #anin = FuncAnimation(plt.gcf(), StartBot, frames=1000, interval=backTest_interval, repeat=False)
    #fig.tight_layout()
    #plt.show()
