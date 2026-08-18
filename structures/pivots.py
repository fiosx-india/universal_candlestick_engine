import numpy as np

def local_extrema(df, window=3):
    highs, lows = [], []
    h, l = df["High"].to_numpy(), df["Low"].to_numpy()
    for i in range(window, len(df)-window):
        if h[i] == np.max(h[i-window:i+window+1]): highs.append(i)
        if l[i] == np.min(l[i-window:i+window+1]): lows.append(i)
    return highs, lows

def linear_slope(values):
    if len(values) < 2: return 0.0
    x = np.arange(len(values))
    return float(np.polyfit(x, values, 1)[0])
