import numpy as np
from ..models import PatternResult
from .pivots import linear_slope

def _result(name, direction, tf, score, **d):
    return PatternResult(name, direction, "FORMING", score, score, tf, d)

def detect_structure_patterns(df, timeframe="") -> list[PatternResult]:
    if len(df) < 30: return []
    c=df["Close"].to_numpy(); h=df["High"].to_numpy(); l=df["Low"].to_numpy()
    out=[]
    n=min(60,len(df)); cc=c[-n:]; hh=h[-n:]; ll=l[-n:]

    # W / M based on two separated extrema with a neckline in between.
    lo1=np.argmin(ll[:n//2]); lo2=n//2+np.argmin(ll[n//2:])
    if abs(ll[lo1]-ll[lo2])/max(abs(ll[lo1]),1e-12) < .03:
        out.append(_result("W Pattern","BULLISH",timeframe,.68, first_bottom=float(ll[lo1]), second_bottom=float(ll[lo2])))
    hi1=np.argmax(hh[:n//2]); hi2=n//2+np.argmax(hh[n//2:])
    if abs(hh[hi1]-hh[hi2])/max(abs(hh[hi1]),1e-12) < .03:
        out.append(_result("M Pattern","BEARISH",timeframe,.68, first_top=float(hh[hi1]), second_top=float(hh[hi2])))

    # V reversal
    k=int(np.argmin(cc))
    if 5 <= k <= n-6 and (cc[0]-cc[k])/cc[0] > .03 and (cc[-1]-cc[k])/cc[k] > .03:
        out.append(_result("V Reversal","BULLISH",timeframe,.70))
    k=int(np.argmax(cc))
    if 5 <= k <= n-6 and (cc[k]-cc[0])/cc[0] > .03 and (cc[k]-cc[-1])/cc[k] > .03:
        out.append(_result("V Reversal","BEARISH",timeframe,.70))

    hs=linear_slope(hh); ls=linear_slope(ll)
    if hs < 0 and ls > 0:
        out.append(_result("Symmetrical Triangle","SIDEWAYS",timeframe,.62, high_slope=hs, low_slope=ls))
    if hs > 0 and ls > 0 and hs < ls:
        out.append(_result("Rising Wedge","BEARISH",timeframe,.61))
    if hs < 0 and ls < 0 and hs > ls:
        out.append(_result("Falling Wedge","BULLISH",timeframe,.61))
    if abs(hs) < max(np.mean(hh)*.0005,1e-9) and ls > 0:
        out.append(_result("Ascending Triangle","BULLISH",timeframe,.60))
    if hs < 0 and abs(ls) < max(np.mean(ll)*.0005,1e-9):
        out.append(_result("Descending Triangle","BEARISH",timeframe,.60))

    # Broadening
    if hs > 0 and ls < 0:
        out.append(_result("Broadening Formation","SIDEWAYS",timeframe,.58))

    # Rounding bottom / cup-like structure
    if n >= 50:
        mid=np.mean(cc[n//2-5:n//2+5]); left=np.mean(cc[:8]); right=np.mean(cc[-8:])
        if mid < left and mid < right and abs(left-right)/max(left,1e-12)<.10:
            out.append(_result("Rounding Bottom","BULLISH",timeframe,.64))
        if abs(left-right)/max(left,1e-12)<.08 and mid < left*.95:
            out.append(_result("Cup & Handle","BULLISH",timeframe,.60))
    return out
