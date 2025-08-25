import numpy as np
import pandas as pd
from .interpolation import _interp_row_1d, _bilinear_superheated
from .utils import Quality_Equation, _get_if_present


TemperatureTable = None
PressureTable = None
Superheated_CompressedTable = None
IndexTable = None

def set_tables(T, P, S_C, I):
    # Assigns tables
    global TemperatureTable, PressureTable, Superheated_CompressedTable, IndexTable
    TemperatureTable = pd.DataFrame(T).copy()
    PressureTable = pd.DataFrame(P).copy()
    Superheated_CompressedTable = pd.DataFrame(S_C).copy()
    IndexTable = pd.DataFrame(I).copy()


def Read_Tables(Material=None, T=None, P=None, x=None, v=None, u=None, h=None, s=None):
    if (Material or "").lower() != "water":
        raise ValueError("Only water accepted for now (V1.0)")

    if T is not None and P is None:
        rowT = _interp_row_1d(TemperatureTable, 'T (°C)', float(T)).iloc[0]

        if not any(arg is not None for arg in [x, v, u, h, s]):
            return pd.DataFrame([rowT])

        x_used = x
        if x_used is None:
            # --- h
            if x_used is None and h is not None and {'Enthalpy Liquid (kJ/kg)','Enthalpy Vapor (kJ/kg)'}.issubset(rowT.index):
                hf = float(rowT['Enthalpy Liquid (kJ/kg)']); hg = float(rowT['Enthalpy Vapor (kJ/kg)'])
                if not np.isclose(hg, hf): x_used = (float(h) - hf) / (hg - hf)
            # --- u
            if x_used is None and u is not None and {'Internal Energy Liquid (kJ/kg)','Internal Energy Vapor (kJ/kg)'}.issubset(rowT.index):
                uf = float(rowT['Internal Energy Liquid (kJ/kg)']); ug = float(rowT['Internal Energy Vapor (kJ/kg)'])
                if not np.isclose(ug, uf): x_used = (float(u) - uf) / (ug - uf)
            # --- v
            if x_used is None and v is not None and {'Specific Volume Liquid (m^3/kg)','Specific Volume Vapor (m^3/kg)'}.issubset(rowT.index):
                vf = float(rowT['Specific Volume Liquid (m^3/kg)']); vg = float(rowT['Specific Volume Vapor (m^3/kg)'])
                if not np.isclose(vg, vf): x_used = (float(v) - vf) / (vg - vf)
            # --- s
            if x_used is None and s is not None and {'Entropy Liquid [kJ/(kg K)]','Entropy Vapor [kJ/(kg K)]'}.issubset(rowT.index):
                sf = float(rowT['Entropy Liquid [kJ/(kg K)]']); sg = float(rowT['Entropy Vapor [kJ/(kg K)]'])
                if not np.isclose(sg, sf): x_used = (float(s) - sf) / (sg - sf)

        if x_used is not None:
            x_used = float(np.clip(x_used, 0.0, 1.0))

        out = {
            "T (°C)": float(rowT.get('T (°C)', T)),
            "P (MPa)": float(rowT.get('P (MPa)', np.nan)),
        }

        if 'Enthalpy Liquid (kJ/kg)' in rowT.index:  out['Enthalpy Liquid (kJ/kg)']        = float(rowT['Enthalpy Liquid (kJ/kg)'])
        if 'Enthalpy Vapor (kJ/kg)' in rowT.index:   out['Enthalpy Vapor (kJ/kg)']  = float(rowT['Enthalpy Vapor (kJ/kg)'])
        if 'Enthalpy Liquid (kJ/kg)' in out and 'Enthalpy Vapor (kJ/kg)' in out:
            out['Enthalpy of Vaporization (kJ/kg)'] = out['Enthalpy Vapor (kJ/kg)'] - out['Enthalpy Liquid (kJ/kg)']

        if x_used is not None:
            out['x'] = x_used

            # h mix
            if 'Enthalpy Liquid (kJ/kg)' in out and 'Enthalpy Vapor (kJ/kg)' in out:
                out['Enthalpy (kJ/kg)'] = (1 - x_used)*out['Enthalpy Liquid (kJ/kg)'] + x_used*out['Enthalpy Vapor (kJ/kg)']

            # u mix
            if {'Internal Energy Liquid (kJ/kg)','Internal Energy Vapor (kJ/kg)'}.issubset(rowT.index):
                uf = float(rowT['Internal Energy Liquid (kJ/kg)']); ug = float(rowT['Internal Energy Vapor (kJ/kg)'])
                out['Internal Energy Liquid (kJ/kg)'] = uf; out['Internal Energy Vapor (kJ/kg)'] = ug; out['Internal Energy of Vaporization (kJ/kg)'] = ug - uf
                out['Internal Energy (kJ/kg)'] = (1 - x_used)*uf + x_used*ug

            # v mix
            if {'Specific Volume Liquid (m^3/kg)','Specific Volume Vapor (m^3/kg)'}.issubset(rowT.index):
                vf = float(rowT['Specific Volume Liquid (m^3/kg)']); vg = float(rowT['Specific Volume Vapor (m^3/kg)'])
                out['Specific Volume Liquid (m^3/kg)'] = vf; out['Specific Volume Vapor (m^3/kg)'] = vg
                out['Specific Volume (m^3/kg)'] = (1 - x_used)*vf + x_used*vg

            # s mix
            if {'Entropy Liquid [kJ/(kg K)]','Entropy Vapor [kJ/(kg K)]'}.issubset(rowT.index):
                sf = float(rowT['Entropy Liquid [kJ/(kg K)]']); sg = float(rowT['Entropy Vapor [kJ/(kg K)]'])
                out['Entropy Liquid [kJ/(kg K)]'] = sf; out['Entropy Vapor [kJ/(kg K)]'] = sg; out['Entropy of Vaporization [kJ/(kg K)]'] = sg - sf
                out['Entropy [kJ/(kg K)]'] = (1 - x_used)*sf + x_used*sg

        else:
            if h is not None: out['Enthalpy (kJ/kg)'] = float(h)
            if u is not None: out['Internal Energy (kJ/kg)'] = float(u)
            if v is not None: out['Specific Volume (m^3/kg)'] = float(v)
            if s is not None: out['Entropy (kJ/(kg·K))'] = float(s)

        return pd.DataFrame([out])

    if P is not None and T is None:
        rowP = _interp_row_1d(PressureTable, 'P (MPa)', float(P)).iloc[0]

        if not any(arg is not None for arg in [x, v, u, h, s]):
            return pd.DataFrame([rowP])

        x_used = x
        if x_used is None:
            if x_used is None and h is not None and {'Enthalpy Liquid (kJ/kg)','Enthalpy Vapor (kJ/kg)'}.issubset(rowP.index):
                hf, hg = float(rowP['Enthalpy Liquid (kJ/kg)']), float(rowP['Enthalpy Vapor (kJ/kg)'])
                if not np.isclose(hg, hf): x_used = (float(h)-hf)/(hg-hf)
            if x_used is None and u is not None and {'Internal Energy Liquid (kJ/kg)','Internal Energy Vapor (kJ/kg)'}.issubset(rowP.index):
                uf, ug = float(rowP['Internal Energy Liquid (kJ/kg)']), float(rowP['Internal Energy Vapor (kJ/kg)'])
                if not np.isclose(ug, uf): x_used = (float(u)-uf)/(ug-uf)
            if x_used is None and v is not None and {'Specific Volume Liquid (m^3/kg)','Specific Volume Vapor (m^3/kg)'}.issubset(rowP.index):
                vf, vg = float(rowP['Specific Volume Liquid (m^3/kg)']), float(rowP['Specific Volume Vapor (m^3/kg)'])
                if not np.isclose(vg, vf): x_used = (float(v)-vf)/(vg-vf)
            if x_used is None and s is not None and {'Entropy Liquid [kJ/(kg K)]','Entropy Vapor [kJ/(kg K)]'}.issubset(rowP.index):
                sf, sg = float(rowP['Entropy Liquid [kJ/(kg K)]']), float(rowP['Entropy Vapor [kJ/(kg K)]'])
                if not np.isclose(sg, sf): x_used = (float(s)-sf)/(sg-sf)

        if x_used is not None:
            x_used = float(np.clip(x_used, 0.0, 1.0))

        out = {"T (°C)": float(rowP.get('T (°C)', np.nan)), "P (MPa)": float(rowP.get('P (MPa)', P))}
        if 'Enthalpy Liquid (kJ/kg)' in rowP.index: out['Enthalpy Liquid (kJ/kg)'] = float(rowP['Enthalpy Liquid (kJ/kg)'])
        if 'Enthalpy Vapor (kJ/kg)'  in rowP.index: out['Enthalpy Vapor (kJ/kg)'] = float(rowP['Enthalpy Vapor (kJ/kg)'])
        if 'Enthalpy Liquid (kJ/kg)' in out and 'Enthalpy Vapor (kJ/kg)' in out:
            out['Enthalpy of Vaporization (kJ/kg)'] = out['Enthalpy Vapor (kJ/kg)'] - out['Enthalpy Liquid (kJ/kg)']

        if x_used is not None:
            out['x'] = x_used
            if 'Enthalpy Liquid (kJ/kg)' in out and 'Enthalpy Vapor (kJ/kg)' in out:
                out['Enthalpy (kJ/kg)'] = (1-x_used)*out['Enthalpy Liquid (kJ/kg)'] + x_used*out['Enthalpy Vapor (kJ/kg)']
            if {'Internal Energy Liquid (kJ/kg)','Internal Energy Vapor (kJ/kg)'}.issubset(rowP.index):
                uf, ug = float(rowP['Internal Energy Liquid (kJ/kg)']), float(rowP['Internal Energy Vapor (kJ/kg)'])
                out['Internal Energy Liquid (kJ/kg)'] = uf; out['Internal Energy Vapor (kJ/kg)'] = ug; out['Internal Energy of Vaporization (kJ/kg)'] = ug - uf
                out['Internal Energy (kJ/kg)'] = (1-x_used)*uf + x_used*ug
            if {'Specific Volume Liquid (m^3/kg)','Specific Volume Vapor (m^3/kg)'}.issubset(rowP.index):
                vf, vg = float(rowP['Specific Volume Liquid (m^3/kg)']), float(rowP['Specific Volume Vapor (m^3/kg)'])
                out['Specific Volume Liquid (m^3/kg)']=vf; out['Specific Volume Vapor (m^3/kg)']=vg
                out['Specific Volume (m^3/kg)'] = (1-x_used)*vf + x_used*vg
            if {'Entropy Liquid [kJ/(kg K)]','Entropy Vapor [kJ/(kg K)]'}.issubset(rowP.index):
                sf, sg = float(rowP['Entropy Liquid [kJ/(kg K)]']), float(rowP['Entropy Vapor [kJ/(kg K)]'])
                out['Entropy Liquid [kJ/(kg K)]']=sf; out['Entropy Vapor [kJ/(kg K)]']=sg; out['Entropy of Vaporization [kJ/(kg K)]']=sg-sf
                out['Entropy [kJ/(kg K)]'] = (1-x_used)*sf + x_used*sg
        else:
            if h is not None: out['Enthalpy [kJ/kg]'] = float(h)
            if u is not None: out['Internal Energy [kJ/kg]'] = float(u)
            if v is not None: out['Specific Volume [m^3/kg]'] = float(v)
            if s is not None: out['Entropy [kJ/(kg·K)]'] = float(s)

        return pd.DataFrame([out])
        
    if T is None and P is None:
        raise ValueError("Please provide either Temperature or Pressure.")

    if T is not None and P is not None:
        sat_row_at_P = _interp_row_1d(PressureTable, 'P (MPa)', float(P))
        Tsat = float(sat_row_at_P['T (°C)'].iloc[0])

        if np.isclose(float(T), Tsat, atol=1e-3):
            return _interp_row_1d(TemperatureTable, 'T (°C)', float(T))

        mask = (
            np.isclose(Superheated_CompressedTable['T (°C)'].astype(float), float(T), atol=1e-9) &
            np.isclose(Superheated_CompressedTable['P (MPa)'].astype(float), float(P), atol=1e-12)
        )
        if mask.any():
            return Superheated_CompressedTable.loc[mask].iloc[[0]].copy()

        return _bilinear_superheated(Superheated_CompressedTable, float(T), float(P))

    raise ValueError("Not enough Data to calculate properties")
  
