
import nest_asyncio

import threading
nest_asyncio.apply()  # Running event hatası almamak icin asenkron loopu tekrar baslatır
import asyncio
import ccxt.async_support as ccxt
from asyncio import run, gather
import json
import websockets

coinListFTX = ['{"op": "subscribe", "channel": "ticker", "market": "ETH-PERP"}','{"op": "subscribe", "channel": "ticker", "market": "ADA-PERP"}','{"op": "subscribe", "channel": "ticker", "market": "XRP-PERP"}','{"op": "subscribe", "channel": "ticker", "market": "BNB-PERP"}','{"op": "subscribe", "channel": "ticker", "market": "BCH-PERP"}']
url = "wss://ftx.com/ws"

urlDeneme = "wss://fstream.binance.com/stream?streams=ethusdt@bookTicker/adausdt@bookTicker/bnbusdt@bookTicker/bchusdt@bookTicker/xrpusdt@bookTicker"
async def main():


    while True:
        try:
            async with websockets.connect(urlDeneme, ping_interval = 500,ping_timeout = 100) as wsocketBinance:



                while True:
                    try:
                            msgBinance = await wsocketBinance.recv()
                            msgDictBinance = json.loads(msgBinance)
                            if msgDictBinance["data"]["s"] == "ETHUSDT":
                                binanceBidETH = float(msgDictBinance["data"]["b"])
                                binanceAskETH = float(msgDictBinance["data"]["a"])



                            print("binance ask" , binanceAskETH, "binance bid", binanceBidETH)
                    except Exception as e:
                            if str(e) == "no close frame received or sent":
                                print("webSocket bağlandı.")
                                break

                            continue
        except Exception as e:
            print(e)
            continue

async def main2():
    while True:
        try:
            async with websockets.connect(url, ping_interval=500, ping_timeout=100) as wsocket:
                for i in coinListFTX:
                    await wsocket.send(i)
                while True:
                    try:
                        msg = await wsocket.recv()
                        msgDict = json.loads(msg)
                        if msgDict["market"] == "ETH-PERP":
                            ftxBidETH = msgDict["data"]["bid"]
                            ftxAskETH = msgDict["data"]["ask"]

                        print("FTX ask", ftxAskETH, "FTX bid", ftxBidETH)
                    except Exception as e:
                        if str(e) == "no close frame received or sent":
                            print("webSocket Connected.")
                            break

                        continue
        except Exception as e:
            print(e)
            continue



async def main3():
    task_1 = asyncio.create_task(main2())
    task_2 = asyncio.create_task(main())
    await asyncio.wait([task_1, task_2])

run(main3())