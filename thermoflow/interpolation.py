import numpy as np
import pandas as pd

def _interp_row_1d(df, xcol, x):
    if df is None or df.empty:
        raise ValueError(f"Table not found: {xcol}")
    df2 = df.copy()
    # Ensure numeric type and order
    df2[xcol] = pd.to_numeric(df2[xcol], errors="coerce")
    df2 = df2.dropna(subset=[xcol]).sort_values(xcol).reset_index(drop=True)

    xs = df2[xcol].to_numpy(dtype=float)

    if len(xs) == 1 or np.isclose(xs[0], xs[-1]):
        out = df2.iloc[[0]].copy(); out[xcol] = float(x); return out
    if x <= xs[0]:
        out = df2.iloc[[0]].copy(); out[xcol] = float(x); return out
    if x >= xs[-1]:
        out = df2.iloc[[-1]].copy(); out[xcol] = float(x); return out

    pos = np.searchsorted(xs, x, side="left")
    lo, hi = pos-1, pos
    x_lo, x_hi = xs[lo], xs[hi]
    if np.isclose(x_hi - x_lo, 0.0):
        out = df2.iloc[[lo]].copy(); out[xcol] = float(x); return out

    w = (x - x_lo) / (x_hi - x_lo)
    num_cols = df2.select_dtypes(include=[np.number]).columns
    out = df2.iloc[[lo]].copy()
    out[num_cols] = out[num_cols] + w*(df2.iloc[hi][num_cols].to_numpy() - out[num_cols].to_numpy())
    out[xcol] = float(x)
    return out


def _bilinear_superheated(df_sc, T, P):
    Ps = np.sort(df_sc['P (MPa)'].unique())
    if P <= Ps[0]: P_lo = P_hi = Ps[0]
    elif P >= Ps[-1]: P_lo = P_hi = Ps[-1]
    else:
        idx = np.searchsorted(Ps, P, side='left')
        P_lo, P_hi = Ps[idx-1], Ps[idx]

    df_lo = df_sc[df_sc['P (MPa)'] == P_lo]
    df_hi = df_sc[df_sc['P (MPa)'] == P_hi]

    row_loT = _interp_row_1d(df_lo, 'T (°C)', T)
    row_hiT = _interp_row_1d(df_hi, 'T (°C)', T)

    if P_lo == P_hi:
        out = row_loT.copy()
        out['P (MPa)'] = P; out['T (°C)'] = T
        return out

    wP = (P - P_lo) / (P_hi - P_lo)
    num_cols = df_sc.select_dtypes(include=[np.number]).columns
    out = row_loT.copy()
    out[num_cols] = out[num_cols] + wP*(row_hiT[num_cols].iloc[0] - out[num_cols].iloc[0])
    out['P (MPa)'] = P; out['T (°C)'] = T
    return out
