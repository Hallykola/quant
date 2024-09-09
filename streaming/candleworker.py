import threading
from queue import Queue
import datetime as dt
import time

from constants import defs
from models.trade_decision import TradeDecision
from streaming.technical_analysis import process_candles

class CandleWorker(threading.Thread):
    def __init__(self,api,pair,trade_settings,candle_queue:Queue,trade_work_queue:Queue,granularity,log_message):
        super().__init__()
        self.trade_settings= trade_settings
        self.candle_queue= candle_queue
        self.granularity= granularity
        self.log_message= log_message
        self.pair= pair
        self.api= api
        self.trade_work_queue = trade_work_queue

    def get_trade_decision(self,candles_df):
        try:
            last_row = process_candles(
                candles_df, 
                self.trade_settings.pair,
                self.trade_settings,
                self.log_message
            )
            if last_row is None:
                self.log_message("process_candles failed", "error")
                return
            
            print(f"CandleWorker {self.trade_settings.pair} SIGNAL", last_row.SIGNAL)

            if last_row.SIGNAL != defs.NONE:
                td: TradeDecision = TradeDecision(last_row)
                print(f"CandleWorker {self.trade_settings.pair} TradeDecision", td)
                self.log_message(f"CandleWorker {self.trade_settings.pair} TradeDecision {td}", self.trade_settings.pair)
                self.trade_work_queue.put(td)
            
        except Exception as error:
            self.log_message(f"Exception in get trade decision: {error}", "error")
        

    def run_analysis(self,expected_time:dt.datetime):
        attempts = 0
        tries = 10
        try:
            while attempts < tries:
                candles_df = self.api.get_candles_df(self.pair,granularity=self.granularity,count=50)
                if candles_df.shape[0] == 0:
                    self.log_message('No candles',"error")
                    print("NO CANDLES")
                elif candles_df.iloc[-1].time != expected_time:
                    print("NO NEW CANDLE")
                    self.log_message('No new candles',"error")
                    time.sleep(0.5)
                    
                else:
                    self.get_trade_decision(candles_df)
                    break
                tries +=1
        except Exception as error:
            self.log_message(f"Exception in run_analysis: {error}", "error")
        # print("check time",candles_df.iloc[-1].time)
        # print("expected time",expected_time)
        # print("are they the same",candles_df.iloc[-1].time != expected_time)
        # print('I broke out')


    def run(self):
        while True:
            last_candle_time:dt.datetime = self.candle_queue.get()
            print(f"CandleWorker new candle : {last_candle_time} {self.trade_settings.pair}")
            self.run_analysis(last_candle_time)