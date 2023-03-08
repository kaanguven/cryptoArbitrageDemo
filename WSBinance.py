import asyncio
import json
import websockets

async def listen():

    '''
    Websocket listener function and main loop
    Parses messages, and prints biggest 5 trades per minute
    '''
    urlBinance = "wss://fstream.binance.com/ws/"
    urlDeneme = "wss://fstream.binance.com/stream?streams=ethusdt@bookTicker"
    url = "wss://ftx.com/ws/"

    while True:
        try:
            async with websockets.connect(urlDeneme,max_queue= 16) as wsocketBinance:


                    while True:

                         try:
                             msgBinance = await wsocketBinance.recv()  # binance icin
                             msgDictBinance = json.loads(msgBinance)
                             #print(msgDictBinance)
                             if msgDictBinance["data"]['s'] == "ETHUSDT":
                                 print(msgDictBinance["data"]["a"])





                         except Exception as e:
                            print(e)
                            print("bağlantı tekrar kurulacak")

        except Exception as e:
            print(e)



asyncio.run(listen())