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
