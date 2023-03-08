import asyncio
import json
import time
import pandas as pd
import pandas_ta as ta
import websockets
import ccxt.async_support as ccxt
from asyncio import run, gather
account_ftx = ccxt.ftx({
    "apiKey": '',
    "secret": '',
    "enableRateLimit": False,
    'options': {
        'defaultType': 'future'
    }
})
timeframe = "5m"
symbol = "ETH-PERP"
url = "wss://ftx.com/ws"
limit = 50

async def rsi():
    global rsiKontrol,smaKontrol,emaKontrol2,macdKontrol, bollingerKontrol
    while True:
        try:
            while True:
                try:
                    since = None
                    fast = 12
                    slow = 26
                    signal = 9

                    num_bars = 1000

                    ohlcvMACD = await account_ftx.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=num_bars)
                    if len(ohlcvMACD):
                        dfMACD = pd.DataFrame(ohlcvMACD, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                        macd = dfMACD.ta.macd(fast=fast, slow=slow, signal=signal)
                        dfMACD = pd.concat([dfMACD, macd], axis=1)
                        dfMACD.loc[dfMACD["MACD_12_26_9"] > dfMACD["MACDs_12_26_9"], "sig"] = "buy"
                        dfMACD.loc[dfMACD["MACD_12_26_9"] < dfMACD["MACDs_12_26_9"], "sig"] = "sell"
                        macdKontrol = dfMACD[ "sig"][999]
                        await asyncio.sleep(3)

                        bars = await account_ftx.fetch_ohlcv(symbol, timeframe=timeframe, limit=num_bars)
                        df_d = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
                        df_d["timestamp"] = pd.to_datetime(df_d["timestamp"], unit="ms")

                        df_d["sma30"] = df_d.close.rolling(30).mean()
                        df_d["sma100"] = df_d.close.rolling(100).mean()
                        df_d.loc[df_d["sma30"] > df_d["sma100"], "sig"] = "buy"
                        df_d.loc[df_d["sma30"] < df_d["sma100"], "sig"] = "sell"
                        smaKontrol = df_d["sig"][999]
                        await asyncio.sleep(3)

                        ohlcvBollinger = await account_ftx.fetch_ohlcv(symbol, timeframe, limit=50)
                        if len(ohlcvBollinger):
                            dfbol = pd.DataFrame(ohlcvBollinger,
                                                 columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                            dfbol['time'] = pd.to_datetime(dfbol['time'], unit='ms')
                            dfbol = pd.concat([dfbol, ta.bbands(dfbol["close"],length=20, std=2)], axis=1)
                            dfbol.loc[dfbol["BBL_20_2.0"] > dfbol["close"], "sig"] = "buy"
                            dfbol.loc[dfbol["BBU_20_2.0"] < dfbol["close"], "sig"] = "sell"
                            bollingerKontrol = dfbol["sig"][49]
                            print(dfbol)

                        print("macd : ",macdKontrol,"sma kontrol :",smaKontrol,"bollinger: ",bollingerKontrol)
                        await asyncio.sleep(3)

                        # print("ema = :" ,emaKontrol)
                        # print("ema2= :",emaKontrol2)
                        # print(type(rsiKontrol))
                        # if rsiKontrol == "1499":
                        #     print("rsi Patladı baştan başlatılıyor")
                        #     break
                except Exception as e:
                    print(e)
                    continue

        except Exception as e:
            print(e)
            continue

async def main():
    global ethFiyatBid,ethFiyatAsk
    Alim = True
    longKapat = False
    shortKapat = False
    while True :
      try:
        async with websockets.connect(url, ping_interval = None) as wsocket:
            await wsocket.send(
                '{"op": "subscribe", "channel": "ticker", "market": "ETH-PERP"}')

            while True:
             try:
                msg = await wsocket.recv()
                msgDict = json.loads(msg)
                ethFiyatAsk = msgDict["data"]["ask"]
                ethFiyatBid = msgDict["data"]["bid"]


                if Alim == True and    macdKontrol == "buy" and smaKontrol == "buy" and bollingerKontrol == "buy" : # 107,91
                    await account_ftx.create_order("ETH-PERP", "market", "buy", 0.02, None)
                    await asyncio.sleep(0.5)
                    d = await account_ftx.fetch_positions(["ETH-PERP"])
                    fiyat = float(d[0]["entryPrice"])
                    print(fiyat)
                    Alim = False
                    longKapat = True
                elif Alim == True and  macdKontrol == "sell" and smaKontrol == "sell" and bollingerKontrol == "sell" :
                    await account_ftx.create_order("ETH-PERP", "market", "sell", 0.02, None)
                    await asyncio.sleep(0.5)
                    d = await account_ftx.fetch_positions(["ETH-PERP"])
                    fiyat = float(d[0]["entryPrice"])
                    print(fiyat)
                    Alim = False
                    shortKapat = True
                elif Alim == False and longKapat == True and ((macdKontrol == "sell" or smaKontrol == "sell") and bollingerKontrol == "sell"):
                    await account_ftx.create_order("ETH-PERP", "market", "sell", 0.02, None,{"reduceOnly":True})
                    print("fiyat bu ollarak kapatıldı",ethFiyatBid)
                    Alim=True
                    longKapat = False
                    print("kapatıldı")
                elif Alim == False and shortKapat == True and  ((macdKontrol == "buy" or smaKontrol == "buy") and bollingerKontrol == "buy" ) :
                    await account_ftx.create_order("ETH-PERP", "market", "buy", 0.02, None,{"reduceOnly":True})
                    print("fiyat bu ollarak kapatıldı",ethFiyatAsk)
                    Alim=True
                    shortKapat = False
                    print("kapatıldı")

                # print(msgDict)
                # if msgDict["market"]=="ETH-PERP":
                #     ethFiyat=msgDict["data"]["bid"]
                # elif msgDict["market"]=="BCH-PERP":
                #     bchFiyat = msgDict["data"]["bid"]
                # elif msgDict["market"]=="ADA-PERP":
                #     adaFiyat = msgDict["data"]["bid"]
                # elif msgDict["market"]=="BNB-PERP":
                #     bnbFiyat = msgDict["data"]["bid"]
                # elif msgDict["market"]=="XRP-PERP":
                #     xrpFiyat = msgDict["data"]["bid"]
                #print("xrpBid",xrpFiyat)



             except Exception as e:

                 print(e)
                 if str(e) == "no close frame received or sent":
                        break
                 continue

      except Exception as e:
        print(e)
        continue
    await account_ftx.close()


async def cagirAll():
    task_1 = asyncio.create_task(main())
    task_2 = asyncio.create_task(rsi())
    #task_3 = asyncio.create_task(orderKontrol())
    await gather (*[task_1,task_2])

run(cagirAll())