import pandas as pd

def simple_forward_backtest(df, signal_col, horizon=5):
    rows=[]
    for i in range(len(df)-horizon):
        if bool(df[signal_col].iloc[i]):
            entry=float(df["Close"].iloc[i])
            exit_=float(df["Close"].iloc[i+horizon])
            rows.append({"index":df.index[i],"return":exit_/entry-1})
    return pd.DataFrame(rows)
