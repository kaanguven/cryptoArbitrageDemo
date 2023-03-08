# @title
import logging
import time
import nest_asyncio
nest_asyncio.apply()  # Running event hatası almamak icin asenkron loopu tekrar baslatır
import asyncio
import ccxt.async_support as ccxt
from asyncio import run, gather
import json
import websockets


# makas_max = 0.0047 # İŞLEM AÇMASI İÇİN GEREKEN MAKAS
makasETH = 0.0038 # ETH işlem açması için gereken makas
makasBNB = 0.0038  # BNB işlem açması için gereken makas
makasBCH = 0.0038  # BCH işlem açması için gereken makas
makasXRP = 0.0040  # XRP işlem açması için gereken makas
makasADA = 0.0038  # ADA işlem açması için gereken makas
makas_min = 0.0008  # işlem kapatması için gereken makas tüm hepsini ortak bir makasta kapatır.

# HER BORSADAN FUTURE OLARAK YANİ VADELİ OLARAK ÇEKİLMEK ZORUNDA ANLIK FİYATLAR ! ! !!!!!!!!!!!!!!!!
symbolETH = "ETH/USDT"  # Binance için
symbolADA = "ADA/USDT"  # Binance için
symbolBCH = "BCH/USDT"  # Binance için
symbolBNB = "BNB/USDT"  # Binance için
symbolXRP = "XRP/USDT"  # Binance için
amountETH = 0.02  # alım satım yapılacak coin miktarı
amountADA = 100
amountBCH = 0.2
amountBNB = 0.2
amountXRP = 100
account_ftx = ccxt.ftx({
    "apiKey": '',
    "secret": '',
    "enableRateLimit": False,
    'options': {
        'defaultType': 'future'
    }
})
account_binance = ccxt.binance({
    "apiKey": '',
    "secret": '',
    "enableRateLimit": False,
    'options': {
        'defaultType': 'future'
    }
})



url = "wss://ftx.com/ws"
urlBinance = "wss://fstream.binance.com/ws"
urlDeneme = "wss://fstream.binance.com/stream?streams=ethusdt@bookTicker/adausdt@bookTicker/bnbusdt@bookTicker/bchusdt@bookTicker/xrpusdt@bookTicker"

coinListFTX = ['{"op": "subscribe", "channel": "ticker", "market": "ETH-PERP"}','{"op": "subscribe", "channel": "ticker", "market": "ADA-PERP"}','{"op": "subscribe", "channel": "ticker", "market": "XRP-PERP"}','{"op": "subscribe", "channel": "ticker", "market": "BNB-PERP"}','{"op": "subscribe", "channel": "ticker", "market": "BCH-PERP"}']

async def main():

    await gather(*[
        account_binance.load_markets(),
        account_ftx.load_markets(),
    ])
    # Switch ve parametreler [ bought_(LongGirilenBorsa)(ShortGirilenBorsa) şeklinde tanımlandı.]
    bought_binanceETH = True  # bu switchler alıma izin olduğunu yani LONG girilecek olanı gösterir.
    bought_ftxETH = True
    bought_binanceADA = True
    bought_ftxADA = True
    bought_binanceBNB = True
    bought_ftxBNB = True
    bought_binanceXRP = True
    bought_ftxXRP = True
    bought_binanceBCH = True
    bought_ftxBCH = True
    closeBinanceETH = False  # kapatış izni açık
    closeBinanceADA = False
    closeBinanceXRP = False
    closeBinanceBNB = False
    closeBinanceBCH = False
    closeFtxETH = False
    closeFtxADA = False
    closeFtxBNB = False
    closeFtxBCH = False
    closeFtxXRP = False

    params = {"reduceOnly": True}
    # params_huobi_open = {"offset": "open","lever_rate":2}  # kaldıraç katsayısı için "lever_rate" = 1 gibi
    # params_huobi_close = {"offset": "close","reduce_only": 1}
    await gather(*[
        account_binance.set_leverage(10, symbolETH),  # KALDIRAÇ DEĞERİ BINANCE
        account_binance.set_leverage(10, symbolADA),
        account_binance.set_leverage(10, symbolBNB),
        account_binance.set_leverage(10, symbolXRP),
        account_binance.set_leverage(10, symbolBCH),
        account_ftx.set_leverage(10, "ETH-PERP"),  # KALDIRAÇ DEĞERİ FTX
        account_ftx.set_leverage(10, "BNB-PERP"),
        account_ftx.set_leverage(10, "ADA-PERP"),
        account_ftx.set_leverage(10, "BCH-PERP"),
        account_ftx.set_leverage(10, "XRP-PERP")
    ])
    binanceBakiye = await account_binance.fetch_balance()
    ftxBakiye = await account_ftx.privateGetAccount()
    while True:
        try:
            async with websockets.connect(url,ping_interval = 500,ping_timeout = 100) as wsocket ,websockets.connect(urlDeneme, ping_interval = 500,ping_timeout = 100) as wsocketBinance:
                for i in coinListFTX:
                    await wsocket.send(i)


                while True:
                    try:
                            msgBinance = await asyncio.wait_for(wsocketBinance.recv(), 0.1)
                            msgDictBinance = json.loads(msgBinance)
                            msg = await asyncio.wait_for(wsocket.recv(), 0.015)  # FTX için
                            # FTX için

                            msgDict = json.loads(msg)

                            if msgDict["market"] =="ETH-PERP":
                                ftxBidETH = msgDict["data"]["bid"]
                                ftxAskETH = msgDict["data"]["ask"]
                            elif msgDict["market"] =="BCH-PERP":
                                ftxBidBCH = msgDict["data"]["bid"]
                                ftxAskBCH = msgDict["data"]["ask"]
                            elif msgDict["market"] =="ADA-PERP":
                                ftxBidADA = msgDict["data"]["bid"]
                                ftxAskADA = msgDict["data"]["ask"]
                            elif msgDict["market"] =="BNB-PERP":
                                ftxBidBNB = msgDict["data"]["bid"]
                                ftxAskBNB = msgDict["data"]["ask"]
                            elif msgDict["market"] =="XRP-PERP":
                                ftxBidXRP = msgDict["data"]["bid"]
                                ftxAskXRP = msgDict["data"]["ask"]



                            if msgDictBinance["data"]["s"] =="ETHUSDT":
                                binanceBidETH = float(msgDictBinance["data"]["b"])
                                binanceAskETH = float(msgDictBinance["data"]["a"])
                            elif msgDictBinance["data"]["s"] =="ADAUSDT":
                                binanceBidADA = float(msgDictBinance["data"]["b"])
                                binanceAskADA = float(msgDictBinance["data"]["a"])
                            elif msgDictBinance["data"]["s"] =="BCHUSDT":
                                binanceBidBCH = float(msgDictBinance["data"]["b"])
                                binanceAskBCH = float(msgDictBinance["data"]["a"])
                            elif msgDictBinance["data"]["s"] =="BNBUSDT":
                                binanceBidBNB = float(msgDictBinance["data"]["b"])
                                binanceAskBNB = float(msgDictBinance["data"]["a"])
                            else:
                                binanceBidXRP = float(msgDictBinance["data"]["b"])
                                binanceAskXRP = float(msgDictBinance["data"]["a"])
                            # print("FTX ",ftxBidETH,ftxAskETH)
                            # print("xrp ask ",binanceAskXRP,"Ask",binanceAskETH)

                            farkAETH = (binanceBidETH - ftxAskETH) / binanceBidETH  # ilkine long girilecek yani FTX
                            farkBETH = (ftxBidETH - binanceAskETH) / (ftxBidETH)
                            farkAADA = (binanceBidADA - ftxAskADA) / binanceBidADA  # ilkine long girilecek yani FTX
                            farkBADA = (ftxBidADA - binanceAskADA) / (ftxBidADA)
                            farkABNB = (binanceBidBNB - ftxAskBNB) / binanceBidBNB  # ilkine long girilecek yani FTX
                            farkBBNB = (ftxBidBNB - binanceAskBNB) / (ftxBidBNB)
                            farkAXRP = (binanceBidXRP - ftxAskXRP) / binanceBidXRP  # ilkine long girilecek yani FTX
                            farkBXRP = (ftxBidXRP - binanceAskXRP) / (ftxBidXRP)
                            farkABCH = (binanceBidBCH - ftxAskBCH) / binanceBidBCH  # ilkine long girilecek yani FTX
                            farkBBCH = (ftxBidBCH - binanceAskBCH) / (ftxBidBCH)
                    except Exception as e:
                            if str(e) == "no close frame received or sent":
                                print("webSocket bağlandı.")
                                break

                            continue

                    if farkAETH >= makasETH and bought_ftxETH == True:
                        await account_binance.create_order(symbolETH, "market", "sell", amountETH, None)
                        await account_ftx.create_order("ETH-PERP", "market", "buy", amountETH, None)
                        print(farkAETH)
                        print(f"Binance için Short order oluşturuldu Coin:ETH {binanceAskETH}")
                        print(f"FTX için Long order oluşturuldu Coin:ETH {ftxBidETH}")
                        closeFtxETH = True
                        bought_ftxETH = False
                        bought_binanceETH = False
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])

                        # Eğer huobi binance ' dan büyükse işlemlerini kapatma
                    elif farkAETH <= makas_min and bought_ftxETH == False and closeFtxETH == True:
                        await account_binance.create_order(symbolETH, "market", "buy", amountETH, None, params)
                        await account_ftx.create_order("ETH-PERP", "market", "sell", amountETH, None, params)
                        print(f"Binance Short kapatıldı Coin:ETH {binanceBidETH}")
                        print(f"ftxi Long kapatıldı Coin:ETH {ftxAskETH}")
                        print(farkAETH)
                        bought_ftxETH = True
                        closeFtxETH = False
                        bought_binanceETH = True
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])




                    # Eğer Binance huobi'den büyükse
                    elif farkBETH >= makasETH and bought_binanceETH == True:
                        await account_binance.create_order(symbolETH, "market", "buy", amountETH, None)
                        await account_ftx.create_order("ETH-PERP", "market", "sell", amountETH, None)
                        print("Binance için Long order oluşturuldu Coin:ETH ")
                        print("FTX için Short order oluşturuldu Coin:ETH ")
                        print(farkBETH)
                        # Sell kontrolü açılıyor
                        bought_ftxETH = False
                        closeBinanceETH = True
                        bought_binanceETH = False
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])



                    # Eğer Binance huobi 'den büyükse işlemleri KAPATMA

                    elif farkBETH <= makas_min and bought_binanceETH == False and closeBinanceETH == True:
                        await account_binance.create_order(symbolETH, "market", "sell", amountETH, None, params)
                        await account_ftx.create_order("ETH-PERP", "market", "buy", amountETH, None, params)
                        print("Binance Long kapatıldı Coin:ETH")
                        print("FTX Short kapatıldı Coin:ETH ")
                        print(farkBETH)
                        bought_ftxETH = True
                        closeBinanceETH = False
                        bought_binanceETH = True
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])

                    elif farkAADA >= makasADA and bought_ftxADA == True:
                        await account_binance.create_order(symbolADA, "market", "sell", amountADA, None)
                        await account_ftx.create_order("ADA-PERP", "market", "buy", amountADA, None)
                        print(farkAADA)
                        print("Binance için Short order oluşturuldu Coin:ADA ")
                        print("FTX için Long order oluşturuldu Coin:ADA ")
                        bought_ftxADA = False
                        closeFtxADA = True
                        bought_binanceADA = False
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])

                        # Eğer huobi binance ' dan büyükse işlemlerini kapatma
                    elif farkAADA <= makas_min and bought_ftxADA == False and closeFtxADA == True:
                        await account_binance.create_order(symbolADA, "market", "buy", amountADA, None, params)
                        await account_ftx.create_order("ADA-PERP", "market", "sell", amountADA, None, params)
                        print("Binance Short kapatıldı Coin:ADA")
                        print("ftxi Long kapatıldı Coin:ADA")
                        print(farkAADA)
                        bought_ftxADA = True
                        closeFtxADA = False
                        bought_binanceADA = True
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])


                    # Eğer Binance huobi'den büyükse
                    elif farkBADA >= makasADA and bought_binanceADA == True:
                        await account_binance.create_order(symbolADA, "market", "buy", amountADA, None)
                        await account_ftx.create_order("ADA-PERP", "market", "sell", amountADA, None)
                        print("Binance için Long order oluşturuldu Coin:ADA ")
                        print("FTX için Short order oluşturuldu Coin:ADA ")
                        print(farkBADA)
                        # Sell kontrolü açılıyor
                        bought_ftxADA = False
                        closeBinanceADA = True
                        bought_binanceADA = False
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])

                    # Eğer Binance huobi 'den büyükse işlemleri KAPATMA

                    elif farkBADA <= makas_min and bought_binanceADA == False and closeBinanceADA == True:
                        await account_binance.create_order(symbolADA, "market", "sell", amountADA, None, params)
                        await account_ftx.create_order("ADA-PERP", "market", "buy", amountADA, None, params)
                        print("Binance Long kapatıldı Coin:ADA")
                        print("FTX Short kapatıldı Coin:ADA ")
                        print(farkBADA)
                        bought_ftxADA = True
                        closeBinanceADA = False
                        bought_binanceADA = True
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])

                    elif farkABNB >= makasBNB and bought_ftxBNB == True:
                        await account_binance.create_order(symbolBNB, "market", "sell", amountBNB, None)
                        await account_ftx.create_order("BNB-PERP", "market", "buy", amountBNB, None)
                        print(farkABNB)
                        print("Binance için Short order oluşturuldu Coin:BNB ")
                        print("FTX için Long order oluşturuldu Coin:BNB ")
                        bought_ftxBNB = False
                        closeFtxBNB = True
                        bought_binanceBNB = False
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])

                        # Eğer huobi binance ' dan büyükse işlemlerini kapatma
                    elif farkABNB <= makas_min and bought_ftxBNB == False and closeFtxBNB == True:
                        await account_binance.create_order(symbolBNB, "market", "buy", amountBNB, None, params)
                        await account_ftx.create_order("BNB-PERP", "market", "sell", amountBNB, None, params)
                        print("Binance Short kapatıldı Coin:BNB")
                        print("ftxi Long kapatıldı Coin:BNB")
                        print(farkABNB)
                        bought_ftxBNB = True
                        closeFtxBNB = False
                        bought_binanceBNB = True
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])




                    # Eğer Binance huobi'den büyükse
                    elif farkBBNB >= makasBNB and bought_binanceBNB == True:
                        await account_binance.create_order(symbolBNB, "market", "buy", amountBNB, None)
                        await account_ftx.create_order("BNB-PERP", "market", "sell", amountBNB, None)
                        print("Binance için Long order oluşturuldu Coin:BNB ")
                        print("FTX için Short order oluşturuldu Coin:BNB ")
                        print(farkBBNB)
                        # Sell kontrolü açılıyor
                        bought_ftxBNB = False
                        closeBinanceBNB = True
                        bought_binanceBNB = False
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])



                    # Eğer Binance huobi 'den büyükse işlemleri KAPATMA

                    elif farkBBNB <= makas_min and bought_binanceBNB == False and closeBinanceBNB == True:
                        await account_binance.create_order(symbolBNB, "market", "sell", amountBNB, None, params)
                        await account_ftx.create_order("BNB-PERP", "market", "buy", amountBNB, None, params)
                        print("Binance Long kapatıldı Coin:BNB")
                        print("FTX Short kapatıldı Coin:BNB ")
                        print(farkBBNB)
                        bought_ftxBNB = True
                        closeBinanceBNB = False
                        bought_binanceBNB = True
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])

                    elif farkABCH >= makasBCH and bought_ftxBCH == True:
                        await account_binance.create_order(symbolBCH, "market", "sell", amountBCH, None)
                        await account_ftx.create_order("BCH-PERP", "market", "buy", amountBCH, None)
                        print(farkABCH)
                        print(f"Binance için Short order oluşturuldu Coin:BCH {binanceAskBCH} ")
                        print(f"FTX için Long order oluşturuldu Coin:BCH {ftxBidBCH}")
                        bought_ftxBCH = False
                        closeFtxBCH = True
                        bought_binanceBCH = False
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])

                        # Eğer huobi binance ' dan büyükse işlemlerini kapatma
                    elif farkABCH <= makas_min and bought_ftxBCH == False and closeFtxBCH == True:
                        await account_binance.create_order(symbolBCH, "market", "buy", amountBCH, None, params)
                        await account_ftx.create_order("BCH-PERP", "market", "sell", amountBCH, None, params)
                        print("Binance Short kapatıldı Coin:BCH")
                        print("ftxi Long kapatıldı Coin:BCH")
                        print(farkABCH)
                        bought_ftxBCH = True
                        closeFtxBCH = False
                        bought_binanceBCH = True
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])


                    # Eğer Binance huobi'den büyükse
                    elif farkBBCH >= makasBCH and bought_binanceBCH == True:
                        await account_binance.create_order(symbolBCH, "market", "buy", amountBCH, None)
                        await account_ftx.create_order("BCH-PERP", "market", "sell", amountBCH, None)
                        print(f"Binance için Long order oluşturuldu Coin:BCH {binanceBidBCH}")
                        print(f"FTX için Short order oluşturuldu Coin:BCH {ftxAskBCH}")
                        print(farkBBCH)
                        # Sell kontrolü açılıyor
                        bought_ftxBCH = False
                        closeBinanceBCH = True
                        bought_binanceBCH = False
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])

                    # Eğer Binance huobi 'den büyükse işlemleri KAPATMA

                    elif farkBBCH <= makas_min and bought_binanceBCH == False and closeBinanceBCH == True:
                        await account_binance.create_order(symbolBCH, "market", "sell", amountBCH, None, params)
                        await account_ftx.create_order("BCH-PERP", "market", "buy", amountBCH, None, params)
                        print(f"Binance Long kapatıldı Coin:BCH {binanceAskBCH}")
                        print(f"FTX Short kapatıldı Coin:BCH {ftxBidBCH}")
                        print(farkBBCH)
                        bought_ftxBCH = True
                        closeBinanceBCH = False
                        bought_binanceBCH = True
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])

                    elif farkAXRP >= makasXRP and bought_ftxXRP == True:
                        await account_binance.create_order(symbolXRP, "market", "sell", amountXRP, None)
                        await account_ftx.create_order("XRP-PERP", "market", "buy", amountXRP, None)
                        print(farkAXRP)
                        print("Binance için Short order oluşturuldu Coin:XRP ")
                        print("FTX için Long order oluşturuldu Coin:XRP ")
                        bought_ftxXRP = False
                        closeFtxXRP = True
                        bought_binanceXRP = False
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])

                        # Eğer huobi binance ' dan büyükse işlemlerini kapatma
                    elif farkAXRP <= makas_min and bought_ftxXRP == False and closeFtxXRP == True:
                        await account_binance.create_order(symbolXRP, "market", "buy", amountXRP, None, params)
                        await account_ftx.create_order("XRP-PERP", "market", "sell", amountXRP, None, params)
                        print("Binance Short kapatıldı Coin:XRP")
                        print("ftxi Long kapatıldı Coin:XRP")
                        print(farkAXRP)
                        bought_ftxXRP = True
                        closeFtxXRP = False
                        bought_binanceXRP = True
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])


                    # Eğer Binance huobi'den büyükse
                    elif farkBXRP >= makasXRP and bought_binanceXRP == True:
                        await account_binance.create_order(symbolXRP, "market", "buy", amountXRP, None)
                        await account_ftx.create_order("XRP-PERP", "market", "sell", amountXRP, None)
                        print("Binance için Long order oluşturuldu Coin:XRP ")
                        print("FTX için Short order oluşturuldu Coin:XRP ")
                        print(farkBXRP)
                        # Sell kontrolü açılıyor
                        bought_ftxXRP = False
                        closeBinanceXRP = True
                        bought_binanceXRP = False
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                              ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                              ftxBakiye["result"]["collateral"])



                    # Eğer Binance huobi 'den büyükse işlemleri KAPATMA

                    elif farkBXRP <= makas_min and bought_binanceXRP == False and closeBinanceXRP == True:
                        await account_binance.create_order(symbolXRP, "market", "sell", amountXRP, None, params)
                        await account_ftx.create_order("XRP-PERP", "market", "buy", amountXRP, None, params)
                        print("Binance Long kapatıldı Coin:XRP")
                        print("FTX Short kapatıldı Coin:XRP")
                        print(farkBXRP)
                        bought_ftxXRP = True
                        closeBinanceXRP = False
                        bought_binanceXRP = True
                        binanceBakiyeGuncel = await account_binance.fetch_balance()
                        ftxBakiyeGuncel = await account_ftx.privateGetAccount()
                        print("Binance Bakiye: ", binanceBakiyeGuncel["info"]["totalWalletBalance"],
                              "(Başlangıç:)", binanceBakiye["info"]["totalWalletBalance"], "Ftx Bakiye :  ",
                          ftxBakiyeGuncel["result"]["collateral"], "(Başlangıç :)",
                          ftxBakiye["result"]["collateral"])






        except Exception as e:
            print(e)
            continue

            await account_ftx.close()
            await account_binance.close()





run(main())
