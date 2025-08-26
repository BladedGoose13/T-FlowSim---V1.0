import pandas as pd
from tables import Read_Tables, Quality_Equation
from utils import _get_if_present

class State:
    def __init__(self, Material, m, V = None, P=None, T=None, x=None, v=None, u=None, h=None, s=None, Velocity=None, Height=None):
        self.Material = Material
        self._data = None
        self.m = m
        self._V = V
        self.P = P
        self.T = T
        self.x = x
        self.given_v = v 
        self.given_u = u
        self.given_h = h
        self.given_s = s
        self.Velocity = Velocity
        self.Height = Height           
        if m is None: raise ValueError('Need value for mass')
    
    @property
    def Data(self):
        if self._data is None:
            self._data = Read_Tables(
                Material=self.Material, T=self.T, P=self.P,
                x=self.x, v=self.given_v, u=self.given_u, h=self.given_h, s=self.given_s
            )
        return self._data
    
    def set_T(self, T):
        self.T = T
        self._data = None

    def set_P(self, P):
        self.P = P
        self._data = None
       
    # Get values of specific intensive properties from table
  
    @property
    def v(self):  return _get_if_present(self.Data, 'Specific Volume (m^3/kg)')
    @property
    def vf(self): return _get_if_present(self.Data, 'Specific Volume Liquid (m^3/kg)')
    @property
    def vg(self): return _get_if_present(self.Data, 'Specific Volume Vapor (m^3/kg)')
    @property
    def h(self):  return _get_if_present(self.Data, 'Enthalpy (kJ/kg)')
    @property
    def hf(self): return _get_if_present(self.Data, 'Enthalpy Liquid (kJ/kg)')
    @property
    def hg(self): return _get_if_present(self.Data, 'Enthalpy Vapor (kJ/kg)')
    @property
    def hfg(self): return _get_if_present(self.Data, 'Enthalpy of Vaporization (kJ/kg)')
    @property
    def u(self):  return _get_if_present(self.Data, 'Internal Energy (kJ/kg)')
    @property
    def uf(self): return _get_if_present(self.Data, 'Internal Energy Liquid (kJ/kg)')
    @property
    def ug(self): return _get_if_present(self.Data, 'Internal Energy Vapor (kJ/kg)')
    @property
    def ufg(self): return _get_if_present(self.Data, 'Internal Energy of Vaporization (kJ/kg)')
    @property
    def s(self):  return _get_if_present(self.Data, 'Entropy [kJ/(kg K)]')
    @property
    def sf(self): return _get_if_present(self.Data, 'Entropy Liquid [kJ/(kg K)]') 
    @property
    def sg(self): return _get_if_present(self.Data, 'Entropy Vapor [kJ/(kg K)]')
    @property
    def sfg(self): return _get_if_present(self.Data, 'Entropy of Vaporization [kJ/(kg K)]')
    @property
    def phase(self): return _get_if_present(self.Data, 'Phase')
    @property
    def P_(self): 
        if self.P is not None:
            return self.P
        else:
            return self.Data['P (MPa)'].iloc[0]
    @property
    def T_(self):
        if self.T is not None:
            return self.T
        else:
            return self.Data['T (°C)'].iloc[0]
        
    # Get absolute values derived from specific ones
    
    @property
    def V(self):
        if self._V is not None:
            return self._V
        else:
            return self.m * self.v
    @V.setter
    def V(self, value):
        self._V = value
    @property
    def U(self): return None if self.u is None else self.m * self.u
    @property
    def H(self): return None if self.h is None else self.m * self.h
    @property
    def S(self): return None if self.s is None else self.m * self.s

    def Data_Frame(self):
        v, u, h, s = self.v, self.u, self.h, self.s
        vf, vg = self.vf, self.vg
        uf, ug = self.uf, self.ug
        hf, hg = self.hf, self.hg
        sf, sg = self.sf, self.sg
    
        x_local = self.x

        if x_local is None and 'x' in self.Data.columns and pd.notna(self.Data['x'].iloc[0]):
            x_local = float(self.Data['x'].iloc[0])

        if x_local is None:
            if h is not None and hf is not None and hg is not None:
                x_local = Quality_Equation(x=None, val_f=hf, val_g=hg, val=h)
            elif u is not None and uf is not None and ug is not None:
                x_local = Quality_Equation(x=None, val_f=uf, val_g=ug, val=u)
            elif v is not None and vf is not None and vg is not None:
                x_local = Quality_Equation(x=None, val_f=vf, val_g=vg, val=v)
            elif s is not None and sf is not None and sg is not None:
                x_local = Quality_Equation(x=None, val_f=sf, val_g=sg, val=s)

        if x_local is not None:
            if v  is None and vf is not None and vg is not None: v  = Quality_Equation(x=x_local, val_f=vf, val_g=vg)
            if u  is None and uf is not None and ug is not None: u  = Quality_Equation(x=x_local, val_f=uf, val_g=ug)
            if h  is None and hf is not None and hg is not None: h  = Quality_Equation(x=x_local, val_f=hf, val_g=hg)
            if s  is None and sf is not None and sg is not None: s  = Quality_Equation(x=x_local, val_f=sf, val_g=sg)

        if self.x is not None:
            if v  is None and vf is not None and vg is not None: v  = Quality_Equation(x=self.x, val_f=vf, val_g=vg)
            if u  is None and uf is not None and ug is not None: u  = Quality_Equation(x=self.x, val_f=uf, val_g=ug)
            if h  is None and hf is not None and hg is not None: h  = Quality_Equation(x=self.x, val_f=hf, val_g=hg)
            if s  is None and sf is not None and sg is not None: s  = Quality_Equation(x=self.x, val_f=sf, val_g=sg)
        
        _State_data = {
            "Material": self.Material,
            "Phase": self.phase,
            "m (kg)": self.m,
            "T (°C)": self.T_,
            "P (MPa)": self.P_,
            "x": x_local,
            "v (m³/kg)": v,
            "vf (m³/kg)": self.vf,
            "vg (m³/kg)": self.vg,
            "u (kJ/kg)": u,
            "uf (kJ/kg)": self.uf,
            "ug (kJ/kg)": self.ug,
            "ufg (kJ/kg)": self.ufg,
            "h (kJ/kg)": h,
            "hf (kJ/kg)": self.hf,
            "hg (kJ/kg)": self.hg,
            "hfg (kJ/kg)": self.hfg,
            "s (kJ/(kg·K))": s,
            "sf (kJ/(kg·K))": self.sf,
            "sg (kJ/(kg·K))": self.sg,
            "sfg (kJ/(kg·K))": self.sfg
        }
        return pd.DataFrame([_State_data])
    
    def __str__(self):
        return self.Data_Frame().to_string(index=False)

def Print_State_Properties(State):
    df = State.Data_Frame()
    print(df)
