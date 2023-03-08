import asyncio
import json
import websockets
from asyncio import run, gather

coinListFTX = ['{"op": "subscribe", "channel": "ticker", "market": "ETH-PERP"}','{"op": "subscribe", "channel": "ticker", "market": "ADA-PERP"}','{"op": "subscribe", "channel": "ticker", "market": "XRP-PERP"}','{"op": "subscribe", "channel": "ticker", "market": "BNB-PERP"}','{"op": "subscribe", "channel": "ticker", "market": "BCH-PERP"}']
coinListBinance = ['{"method": "SUBSCRIBE", "params": ["ethusdt@bookTicker","bnbusdt@bookTicker","adausdt@bookTicker","bchusdt@bookTicker","xrpusdt@bookTicker"] }']
async def listen():

    '''
    Websocket listener function and main loop
    Parses messages, and prints biggest 5 trades per minute
    '''
    urlBinance = "wss://fstream.binance.com/ws/"
    urlDeneme= "wss://fstream.binance.com/stream?streams=ethusdt@bookTicker/adausdt@bookTicker/bnbusdt@bookTicker/bchusdt@bookTicker/xrpusdt@bookTicker"

    i = 0
    url = "wss://ftx.com/ws/"

    while True:
        try:
            async with websockets.connect(url) as wsocket, websockets.connect(urlDeneme) as wsocketBinance:

                    await gather (*[ wsocket.send(
                        '{"op": "subscribe", "channel": "ticker", "market": "ETH-PERP"}'),
                    wsocket.send(
                        '{"op": "subscribe", "channel": "ticker", "market": "XRP-PERP"}'),
                    wsocket.send(
                        '{"op": "subscribe", "channel": "ticker", "market": "ADA-PERP"}'),
                    wsocket.send(
                        '{"op": "subscribe", "channel": "ticker", "market": "BCH-PERP"}'),
                    wsocket.send(
                        '{"op": "subscribe", "channel": "ticker", "market": "BNB-PERP"}')])
                    while True:

                         try:
                             msg = await wsocket.recv()
                             msgBinance = await wsocketBinance.recv()
                             async for msgBinance in wsocketBinance:

                                 msgDictBinance = json.loads(msgBinance)
                                 # msg = await wsocket.recv()  # FTX için
                                 # msgDict = json.loads(msg)
                                 #print(msgDictBinance)
                                 msgDict = json.loads(msg)

                                 #print(msgDict["data"]["bids"][0][0])
                                 # if msgDict["market"] == "ETH-PERP":



                                 # if msgDictBinance["data"]["s"] == "ETHUSDT":
                                 #     binanceBidETH = float(msgDictBinance["data"]["b"])
                                 #     binanceAskETH = float(msgDictBinance["data"]["a"])
                                 # elif msgDictBinance["data"]["s"] == "ADAUSDT":
                                 #     binanceBidADA = float(msgDictBinance["data"]["b"])
                                 #     binanceAskADA = float(msgDictBinance["data"]["a"])
                                 # elif msgDictBinance["data"]["s"] == "BCHUSDT":
                                 #     binanceBidBCH = float(msgDictBinance["data"]["b"])
                                 #     binanceAskBCH = float(msgDictBinance["data"]["a"])
                                 # elif msgDictBinance["data"]["s"] == "BNBUSDT":
                                 #     binanceBidBNB = float(msgDictBinance["data"]["b"])
                                 #     binanceAskBNB = float(msgDictBinance["data"]["a"])
                                 # else:
                                 #     binanceBidXRP = float(msgDictBinance["data"]["b"])
                                 #     binanceAskXRP = float(msgDictBinance["data"]["a"])
                                 # print("eth BİD",binanceBidETH,"eth ASK",binanceAskETH)


                         except Exception as e:
                            print(e)
                            break
                            print("bağlantı tekrar kurulacak")


        except Exception as e:
            print(e)



asyncio.run(listen())