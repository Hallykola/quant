import json
import sys
import time
from queue import Queue

from api.oanda import OandaApi
from infrastructure.logger import LogWrapper
from models.tradesettings import TradeSettings
from streaming.candleworker import CandleWorker
from streaming.priceprocessor import PriceProcessor
from streaming.pricestreamer import PriceStreamer
from streaming.tradeworker import TradeWorker
sys.path.append('../')
import threading

class Bot:

    def __init__(self):
        self.tradeSettings = {}
        self.logfiles= {}
        self.loadSettings()
        self.setUpLogging()
        self.api = OandaApi()

    def setUpLogging(self):
        for trading_pair in self.tradeSettings.keys():
            logfile = LogWrapper(trading_pair)
            logfile.logger.info(trading_pair)
            self.logfiles[trading_pair]=logfile

        self.logfiles["main"] = LogWrapper("main")
        self.logfiles["error"] = LogWrapper("error")
        
        self.log_to_main("Done setting up logs")
    def log_message(self, mssg,key):
        self.logfiles[key].logger.debug(mssg)

    def log_to_error(self,mssg):
        self.log_message(mssg,"error")

    def log_to_main(self,mssg):
        self.log_message(mssg,"main")

    def loadSettings(self):
        with open("./bot/settings.json","r") as f:
            self.settings = json.loads(f.read())
            self.tradeSettings  = {k:TradeSettings(k,v) for k,v in self.settings['trading_pairs'].items()}
            self.trade_risk  = self.settings['trade_risk']
            self.granularity  = self.settings['granularity']
           
    def runStreamer(self):
        self.loadSettings()
        shared_prices  ={}
        shared_prices_event={}
        shared_prices_lock= threading.Lock()
        
        candle_queue = Queue()
        trade_work_queue = Queue()


        for pair in self.tradeSettings.keys():
            shared_prices_event[pair] = threading.Event()
            shared_prices[pair] = {}

        threads = []
        price_streamer_thread = PriceStreamer(shared_prices,shared_prices_event,shared_prices_lock,self.log_message)
        price_streamer_thread.daemon = True
        threads.append(price_streamer_thread)
        price_streamer_thread.start()

        for pair in self.tradeSettings.keys():
            price_processor_thread =  PriceProcessor(shared_prices,shared_prices_event,shared_prices_lock,pair,candle_queue,self.granularity,self.log_message)
            price_processor_thread.daemon=True
            threads.append(price_processor_thread)
            price_processor_thread.start()

        
        for pair in self.tradeSettings.keys():
            candle_worker_thread =  CandleWorker(self.api,pair,self.tradeSettings[pair],candle_queue,trade_work_queue,self.granularity,self.log_message)
            candle_worker_thread.daemon=True
            threads.append(candle_worker_thread)
            candle_worker_thread.start()


        trade_worker_thread = TradeWorker(self.api,trade_work_queue, self.trade_risk,self.log_message)
        trade_worker_thread.daemon = True
        threads.append(trade_worker_thread)
        trade_worker_thread.start()


        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("KeyboardInterrupt")

        print("ALL DONE")