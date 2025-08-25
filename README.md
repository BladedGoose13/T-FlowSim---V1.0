# ThermoFlow

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-app-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Made with Love](https://img.shields.io/badge/Made%20with-%E2%9D%A4-red.svg)]()

ThermoFlow is a Python-based simulation software for thermodynamic processes, designed for industrial systems.  
It can handle steam tables, retrieve interpolated property data, and features a **Streamlit-based UI**.

---

## 🚀 Features (V1.0)
- Reads and interpolates **predefined steam tables** (saturation by T and P, superheated/compressed).
- Enforces the **state postulate** (two intensive properties define the state, no more than two property inputs allowed).
- Computes state properties:
  - **Specific volume**: *v, vf, vg*
  - **Specific internal energy**: *u, uf, ug, ufg*
  - **Specific enthalpy**: *h, hf, hg, hfg*
  - **Specific entropy**: *s, sf, sg, sfg*
---
<img src="ThermoFlow%20(V1.0).png" alt="ThermoFlow UI" width="600">
---

## 🗺️ Roadmap

### SHORT TERM (Third semester)
- **V2.0** → Add thermodynamic diagrams (P–v, T–s) with matplotlib + cycle simulations with efficiency & irreversibility calculations (Rankine, refrigeration, heat pumps).

- **V3.0** → Exergy calculations & laws of efficiency  
  - Calculation and visualization of thermodynamic length

### MEDIUM TERM (Fourth semester)
- **V4.0** → Custom material & configuration:  
  - Varying working fluids  
  - Asymmetric compression/expansion ratios  
  - Multi-stage cycles or regenerative variations  
  - Real process data input  

- **V5.0** → Inferential statistics analysis  
  - Degradation detection  
  - Inferential analysis for efficiency (regression, p-values, ML-ready)  

### LONG TERM (Junior year)
- **V6.0** → Plot of exergy destruction vs cycle degradation  
  - Monte Carlo simulations (e.g. vary T, P, flow rate ±5%)  
  - Sobol sensitivity index  
  - Spider plots or tornado plots for visualization
    
- **V7.0** → Thermodynamic geometry of discrete processes (FEM-style modeling)  
  - Dynamic matplotlib plotting (sliders, animations, updates)  
  - Animated cycle simulation  

---
> **Note:** AI tools were used as part of the development process for optimization, debugging and documentation.
---
## ⚡ Installation
```bash
git clone https://github.com/BladedGoose13/ThermoFlow---V1.0.git
cd ThermoFlow---V1.0
pip install -r requirements.txt
streamlit run frontend/app.py
