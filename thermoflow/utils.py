import numpy as np
import pandas as pd

def Quality_Equation(x=None, val_f=None, val_g=None, val=None):
    if val_f is None or val_g is None:
        raise ValueError('Error in retrieving data from steam tables')
    if x is None and val is None:
        raise ValueError("Provide either x or value")
    if x is None:
        denom = (val_g - val_f)
        if denom == 0:
            raise ValueError('Cannot compute quality: fg difference is zero')
        x_calc = (val - val_f)/denom
        return float(np.clip(x_calc, 0.0, 1.0))
    return ((1 - x)*val_f) + (x*val_g)

def _get_if_present(df, col):
    if df is None or df.empty or col not in df.columns:
        return None
    val = df[col].iloc[0]
    return val if pd.notna(val) else None
