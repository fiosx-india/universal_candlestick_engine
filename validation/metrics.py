import numpy as np

def classification_metrics(returns, threshold=0.002):
    a=np.asarray(returns,float)
    return {
        "samples":int(len(a)),
        "bullish_rate":float((a>threshold).mean()) if len(a) else 0,
        "bearish_rate":float((a<-threshold).mean()) if len(a) else 0,
        "sideways_rate":float((np.abs(a)<=threshold).mean()) if len(a) else 0,
        "mean_return":float(a.mean()) if len(a) else 0,
        "median_return":float(np.median(a)) if len(a) else 0,
    }
