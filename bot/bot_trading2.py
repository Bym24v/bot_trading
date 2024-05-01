import numpy, time, telebot
from math import *
import threading
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from pymexc import spot

# Server IP --> 64.23.211.147

# Demo Keys
api_key = "mx0vglIVNeUoeMNiak"
api_secret = "2764b404e0ba4e509a9552900092e475"

# SPOT V3
spot_client = spot.HTTP(api_key = api_key, api_secret = api_secret)

# Telegram bot
bot = telebot.TeleBot("6043605591:AAG0IToSiVhG0KQxhUw2Yk0Ie76iPELmyfk")

_symbol ='LINKUSDT'
maxPerOperation = 5.0
period_argre = 15
gap = 0.013

backTest = True
isGetData = False
isSendTelegram = True
isLoop = True
totalFee = 0
totalFeeUSDT = 0

amout = 0
totalDiff = 0
listBuys = []
totalBuys = []
totalSells = []

countBuys = 0
countSells = 0
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
actualPriceCoin = 0

status = "running"
mode = 'simulation'
timeFrame = '1m'
lastKlineBuy = 0
maxAmout = 50
dateBuy = 0
totalMins = 0
toDay = False

def StartBot():

    global status
    global mode
    global amout
    global backTest
    global totalDiff
    global _symbol
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
    global isLoop
    global actualPriceCoin
    global totalFee
    global totalFeeUSDT
    global isSendTelegram
    global lastKlineBuy
    global gap
    global maxAmout
    global maxPerOperation
    global dateBuy
    global totalMins
    global toDay
    
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
        
        brokerFee = 0.001
        totalFee = 0.0
         
        totalMins += 1
        if totalMins == 1440:
            toDay = True
        
        if toDay:
            
            toDay = False
            totalMins = 0
            
            bot.send_message('-4116577296', "Symbol: LINK/USDT" \
                        + "\nStatus: {0}".format(status) \
                        + "\nMode: {0}".format(mode) \
                        + "\nTimeFrame: {0}".format(timeFrame) \
                        + "\nMax Amount: {0}".format(maxAmout) \
                        + "\nMax P. Operation: {0}".format(maxPerOperation) \
                        + "\nLINK Fee: {0}".format(totalFee) \
                        + "\nUSDT Fee: {0}".format(totalFeeUSDT) \
                        + "\nU. GAP: {0}".format(gap) \
                        + "\nP. Argre: {0}".format(period_argre) \
                        + "\nA. Price: {0}".format(actualPriceCoin) \
                        + "\nL. Buys: {0}".format(len(listBuys)) \
                        + "\nT. Buys: {0}".format(countBuys) \
                        + "\nT. Sells: {0}".format(countSells) \
                        + "\nT. Diff: {0}".format(totalDiff))
        
        # Pandas Frame
        df = pd.DataFrame(columns=['Open_time', 'Open', 'High', 'Low', 'Close'])
            
        # kLines Spot
        klines = spot_client.klines(symbol='LINKUSDT', interval=timeFrame, limit=100)
        
        #account_info = spot_client.account_information()
        
        actualPriceCoin = float(klines[len(klines)-1][4])
        
        # Calculate Fee Broker cost link
        totalFee = "{0:.3f}".format((brokerFee * maxPerOperation))
        #print(totalFee)
        
        # Calculate estimate fee usdt
        totalFeeUSDT = "{0:.3f}".format((actualPriceCoin * float(totalFee)))
        #print(totalFeeUSDT)
        
        if backTest:
            
            for kline in klines:
                timeP.append(float(kline[0]))
                #openP.append(float(kline[1]))
                #highP.append(float(kline[2]))
                #lowP.append(float(kline[3]))
                closeP.append(float(kline[4]))
                
            # Set data to pandas 
            df["Open_time"] = pd.Series(timeP)
            #df["Open"] = pd.Series(openP)
            #df["High"] = pd.Series(highP)
            #df["Low"] = pd.Series(lowP)
            df["Close"] = pd.Series(closeP)

            if isGetData == False:
                isGetData = True
                
                # Get Actual Date
                lastKlineBuy = pd.to_datetime(df['Open_time'][len(df['Open_time'])-1], unit='ms', utc=True)
                print("Date Copy: {0}".format(lastKlineBuy.tz_convert('Europe/Berlin')))
                print("Starting Bot Argre LINK/USDT")
            
            # Argrelextrema
            #df['Min'] = df.iloc[argrelextrema(df['Close'].values, np.less_equal, order=period_argre)[0]]['Close']
            #df['Max'] = df.iloc[argrelextrema(df['Close'].values, np.greater_equal, order=period_argre)[0]]['Close']
            
            mins = argrelextrema(df['Close'].values, np.less_equal, order=period_argre)[0]
            maxs = argrelextrema(df['Close'].values, np.greater_equal, order=period_argre)[0]
            
            # Signals Buys
            if mins[len(mins)-1] == 99:
                
                print("Signal Buy")
                if amout < maxAmout:
                    
                    priceBuy =  df['Close'][len(df['Close'])-1]
                    dateBuy =  pd.to_datetime(df['Open_time'][len(df['Open_time'])-1], unit='ms', utc=True)
                    #print(lastKlineBuy < dateBuy.tz_convert('Europe/Berlin'))
                    
                    if lastKlineBuy < dateBuy.tz_convert('Europe/Berlin'):
                        lastKlineBuy = dateBuy.tz_convert('Europe/Berlin')
                        
                        #print("Entra lista")
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
                                        + "\nLINK. Fee: {0:.3f}€".format(float(totalFee)) \
                                        + "\nU. O. Fee: {0:.3f}€".format(float(totalFeeUSDT)) \
                                        + "\nU. Buy. Cost: {0:.2f}€".format(priceBuy * maxPerOperation) \
                                        + "\nDate: {0}".format(dateBuy.tz_convert('Europe/Berlin')))        
                        else:
                            
                            #print("Primera Compra")
                            print("Price Buy: {0}".format(priceBuy))

                            amout += maxPerOperation
                    
                            listBuys.append(priceBuy)
                            countBuys += 1
                        
                            if isSendTelegram: 
                                bot.send_message('-4116577296', "Symbol: LINK/USDT" \
                                        + "\nSignal Buy" \
                                        + "\nAmout: {0}".format(maxPerOperation) \
                                        + "\nPrice: {0}".format(priceBuy) \
                                        + "\nLINK. Fee: {0:.3f}€".format(float(totalFee)) \
                                        + "\nU. O. Fee: {0:.3f}€".format(float(totalFeeUSDT)) \
                                        + "\nU. Buy. Cost: {0:.2f}€".format(priceBuy * maxPerOperation) \
                                        + "\nDate: {0}".format(dateBuy.tz_convert('Europe/Berlin')))
            
            # Signals Sells
            if maxs[len(maxs)-1] == 99:
                
                print('Signal Sell')    
                for buy in listBuys:
                    
                    idealSell = buy + ((float(totalFee) + gap) * 2)
                    print("Ideal Sell: {0:.3f}".format(idealSell))
                    
                    
                    if df['Close'][len(df['Close'])-1] >= idealSell:
                        
                        print("Price Sell: {0} diff: {1:.02f}".format(idealSell, (idealSell - buy)))
                        
                        totalDiff += (idealSell - buy) * maxPerOperation
                        
                        totalDiff -= float(totalFee) * 2
                        
                        amout -= maxPerOperation
                        countSells += 1
                        listBuys.remove(buy)
                            
                        dateSell = pd.to_datetime(df['Open_time'][len(df['Open_time'])-1], unit='ms', utc=True)
                        
                        if isSendTelegram:
                            bot.send_message('-4116577296', "Symbol: LINK/USDT" \
                                        + "\nSignal Sell" \
                                        + "\nAmout: {0}".format(maxPerOperation) \
                                        + "\nPrice: {0}".format(idealSell) \
                                        + "\nLINK. Fee: {0:.3f}€".format(float(totalFee)) \
                                        + "\nU. O. Fee: {0:.3f}€".format(float(totalFeeUSDT)) \
                                        + "\nU. Sell: {0:.2f}€".format(idealSell * maxPerOperation) \
                                        + "\nT. Diff: {0:.2f}€".format(totalDiff) \
                                        + "\nDate: {0}".format(dateSell.tz_convert('Europe/Berlin')))
            
                     
            #print("Init Amount: {0:.02f}€".format(initialAmout))
            #print("Max Amount: {0} LINK/USDT".format(maxAmout))
            #print("Max Operation: {0}".format(maxPerOperation))
            #print("Actual Price: {0:.03f}".format(actualPriceCoin))
            #print("Actual Amount: {0}".format(amout))
            #print("Total Fee: {0}".format(totalFee))
            #print("USDT Fee: {0}€".format(totalFeeUSDT))
            #print("List Buys: {0}".format(len(listBuys)))
            #print(listBuys)
            #print("Total Buy: {0}".format(countBuys))
            #print("Total Sell: {0}".format(countSells))
            
            #finalDiffAmout =  ((initialAmout + totalDiff) / initialAmout) * 100
            #print("Total Perc: {0:.02f} %".format(finalDiffAmout - 100))
            #print("Total Diff: {0:.02f} €\n".format(totalDiff))
        
        time.sleep(15) # 60 = 1min
    
    status = 'stop'
          
# @bot.message_handler(commands=['start', 'stop', 'status'])
# def start(message):
    
#     global isLoop
#     global status
#     global listBuys
#     global countBuys
#     global countSells
#     global actualPriceCoin
#     global totalFee
#     global totalFeeUSDT
#     global timeFrame
#     global gap
#     global period_argre
#     global maxAmout
#     global maxPerOperation
    
#     if isLoop:
#         status = "running"
#     else:
#         status = 'stop'
        
#     if message.text == '/start':
#         if message.chat.id == -4116577296 or message.chat.id == 179291648 or message.chat.id == 1690564747:
#             bot.send_message(message.chat.id, "Start Bot!!\nstatus: {0}\nmode:{1}".format(status, mode))
#         else:
#             bot.send_message(message.chat.id, "Este bot es para uso privado.")
            
#     if message.text == '/stop':
#         if message.chat.id == -4116577296 or message.chat.id == 179291648 or message.chat.id == 1690564747:
#             isLoop = False
#             bot.send_message(message.chat.id, "Stop Bot!!\nstatus: {0}\nmode:{1}".format(status, mode))
#         else:
#             bot.send_message(message.chat.id, "Este bot es para uso privado.")
        
        
        
#     if message.text == '/status':
#         if message.chat.id == -4116577296 or message.chat.id == 179291648 or message.chat.id == 1690564747:
#             bot.send_message(message.chat.id, "Symbol: LINK/USDT" \
#                         + "\nStatus: {0}".format(status) \
#                         + "\nMode: {0}".format(mode) \
#                         + "\nTimeFrame: {0}".format(timeFrame) \
#                         + "\nMax Amount: {0}".format(maxAmout) \
#                         + "\nMax P. Operation: {0}".format(maxPerOperation) \
#                         + "\nLINK Fee: {0}".format(totalFee) \
#                         + "\nUSDT Fee: {0}".format(totalFeeUSDT) \
#                         + "\nU. GAP: {0}".format(gap) \
#                         + "\nP. Argre: {0}".format(period_argre) \
#                         + "\nA. Price: {0}".format(actualPriceCoin) \
#                         + "\nL. Buys: {0}".format(len(listBuys)) \
#                         + "\nT. Buys: {0}".format(countBuys) \
#                         + "\nT. Sells: {0}".format(countSells) \
#                         + "\nT. Diff: {0}".format(totalDiff))
#         else:
#             bot.send_message(message.chat.id, "Este bot es para uso privado.")
            
# def LoopTelegram():
    
#     try:
#         bot.polling(none_stop=True)
#     except:
#         print("[!] Error Loop Telegram")

if __name__ == "__main__":
    
    # Thread Bot Mexc
    t1 = threading.Thread(target=StartBot)
    t1.start()
    
    # Thread Bot Telegram
    #t2 = threading.Thread(target=LoopTelegram)
    #t2.start()
