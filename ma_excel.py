import pandas as pd

def create_excel(df_ma_res, df_ma_trades,granularity):
    filename  =f"ma_sim_{granularity}.xlsx"
    writer = pd.ExcelWriter(filename, engine="xlsxwriter")

    writer.close()
if __name__ == "__main__":

    create_excel(df_ma_res, df_ma_trades,granularity)
    create_excel(df_ma_res, df_ma_trades,granularity)
