import pandas as pd
import sys

from constants import defs
from technicals.indicators import BollingerBands
sys.path.append("../")
from models.tradesettings import TradeSettings
pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)

def apply_SL(row,trade_settings: TradeSettings ):
    if row.SIGNAL == defs.BUY:
        return row.mid_c - (row.GAIN/trade_settings.riskreward)
    if row.SIGNAL == defs.SELL:
        return row.mid_c + (row.GAIN/trade_settings.riskreward)
    return 0.0

def apply_TP(row):
    if row.SIGNAL == defs.BUY:
        return row.mid_c + row.GAIN
    if row.SIGNAL == defs.SELL:
        return row.mid_c - row.GAIN
    return 0.0
def apply_signal(row, tradeSettings:TradeSettings):
    if row.SPREAD <= tradeSettings.maxspread and row.GAIN >= tradeSettings.mingain:
        if row.mid_c > row.BB_UP and row.mid_o < row.BB_UP:
            return defs.SELL
        elif row.mid_c < row.BB_LW and row.mid_o > row.BB_LW:
            return defs.BUY
    return defs.NONE

    # if row.GAIN >= tradeSettings.mingain and row.spread <= tradeSettings.maxspread:
    #     if row.mid_c > row.BB_UP and row.mid_o < row.BB_UP:
    #         return defs.SELL
    #     if row.mid_o > row.BB_LW and row.mid_c < row.BB_LW:
    #         return defs.BUY
    # return defs.NONE
 
def process_candles(df: pd.DataFrame, pair, trade_settings: TradeSettings, log_message):
    df_an = df.copy()
    df_an.reset_index(drop=True, inplace=True)
    df_an["PAIR"] = pair
    df_an["SPREAD"] = df_an.ask_c -df_an.bid_c
    df_an = BollingerBands(df_an,trade_settings.n_ma,trade_settings.n_std)
    df_an["GAIN"] =    (df_an.mid_c - df_an.BB_MA)*0.6 #df_an.mid_c - df_an.BB_MA
    df_an['SIGNAL'] = df_an.apply(apply_signal, axis=1,  args=(trade_settings,))
    df_an["SL"] = df_an.apply(apply_SL, axis=1, args=(trade_settings,))
    df_an["TP"] = df_an.apply(apply_TP,axis=1)
    df_an["LOSS"] = abs(df_an.mid_c - df_an.SL)

    log_cols = ['PAIR', 'time', 'mid_c', 'mid_o','BB_UP' ,'BB_MA','BB_LW','SL', 'TP', 'SPREAD', 'GAIN', 'LOSS', 'SIGNAL']

    # log_cols = ['PAIR', 'time', 'mid_c', 'mid_o', 'SL', 'TP', 'SPREAD', 'GAIN', 'LOSS', 'SIGNAL']
    log_message(f"process_candles:\n{df_an[log_cols].tail()}", pair)

    return df_an[log_cols].iloc[-1]
