

from models.trade_decision import TradeDecision
from streaming.trade_risk_calculator import get_trade_units


def get_open_trades(api,pair):
    open_trades = api.get_open_trades()
    for ot in open_trades:
       if ot.instrument == pair:   #if ot['instrument'] == pair:
         return ot
    return None

def place_trade(api,trade_decision:TradeDecision,trade_risk,log_message):
    open_trade =  get_open_trades(api,trade_decision.pair)
    if open_trade != None:
        log_message(f"Failed to place trade {trade_decision}, already open: {open_trade}", trade_decision.pair)
        return None
    trade_units = get_trade_units(api, trade_decision.pair, trade_decision.signal, 
                            trade_decision.loss, trade_risk, log_message)

    ok,response = api.place_trade(
        trade_decision.pair, 
        trade_units,
        trade_decision.signal,
        trade_decision.sl,
        trade_decision.tp
    )
    
    if not ok:
        log_message(f"ERROR placing {trade_decision}..error:{response}",'error')
        log_message(f"ERROR placing {trade_decision}...error:{response}", trade_decision.pair)
    
       
    # if trade_id is None:
    #     log_message(f"ERROR placing {trade_decision}",'error')
    #     log_message(f"ERROR placing {trade_decision}", trade_decision.pair)
    else:
        trade_id = response
        log_message(f"placed trade_id:{trade_id} for {trade_decision}", trade_decision.pair)
        print(f"placed trade_id:{trade_id} for {trade_decision}")