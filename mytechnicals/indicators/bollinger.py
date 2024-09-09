import pandas as pd

def Bollinger ( df: pd.DataFrame, s=2, n= 20 ):
    MOV_AVG = (df.mid_l + df.mid_c +df.mid_h)/3
    stdev =     MOV_AVG.rolling(window=n).std()
    df["BOL_UP"] = MOV_AVG + (s * stdev)
    df["BOL_LW"] = MOV_AVG - (s * stdev)
    df["BOL_MN"] =  MOV_AVG .rolling(window=n).mean()
    return df

