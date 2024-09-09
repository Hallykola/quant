import json
import sys

from infrastructure.logger import LogWrapper
from models.tradesettings import TradeSettings
sys.path.append('../')
from api.oanda import OandaApi 
class Bot():
    def __init__(self):
        self.api  = OandaApi

        self.logfiles= {}
        self.tradeSettings = {}

        self.loadSettings()
        self.setUpLogging()


    def loadSettings(self):
        with open("./bot/settings.json","r") as f:
            self.settings = json.loads(f.read())
            self.tradeSettings  = {k:TradeSettings(k,v) for k,v in self.settings['trading_pairs'].items()}
            self.trade_risk  = self.settings['trade_risk']
            # print(self.settings.keys())
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
        

    def run(self):
        pass