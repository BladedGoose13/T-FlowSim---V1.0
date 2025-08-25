import streamlit as st 
import PROYECTO_PERSONAL as thermo
import pandas as pd
from pathlib import Path
from streamlit_option_menu import option_menu


def read_any(path):
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
 
    return pd.read_csv(path, encoding="utf-8") 

@st.cache_data
def Load_Tables(base: str | Path = None):
    base = Path(base) if base else Path(__file__).resolve().parent

    def read(name):
        
        return pd.read_csv(base / name, encoding="cp1252")

    T  = read("Tabla_Saturada_por_Temperatura.csv")
    P  = read("Saturated_by_Pressure.csv")
    SC = read("Cleaned_Filled_Compressed_Liquid_and_Superheated_Steam.csv")
    I  = read("Critical_Properties_Table__SI_.csv")
    return T, P, SC, I, str(base)

def main():
    st.title("ThermoFlow (V1.0)")
   
    Tval = None
    Pval = None
    
    Ttbl, Ptbl, Stbl, Itbl, loaded_from = Load_Tables()

    thermo.set_tables(T=Ttbl, P=Ptbl, S_C=Stbl, I=Itbl)

    st.caption(f"Tables loaded from: `{loaded_from}`")

    with st.expander("State Properties"):
        
        st.session_state["mi_key"] = None
        st.markdown("<div style='text-align: center;'><h2 style='font-size:20px;'>You can choose to use Temperature, Pressure or both.<br> Please leave unused properties empty</h2></div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center;'><h2 style='font-size:16px;'>Following the state postulate, only 2 intensive property inputs are allowed</h2></div>", unsafe_allow_html=True)
        col_T, col_P = st.columns(2)
        with col_T:
            mode_T = st.number_input("Saturation Temperature (C°)", min_value=-50.0, max_value=2000.0,value=None, step=0.01)
        with col_P:
            mode_P = st.number_input("Saturation Pressure (MPa)", min_value=0.001, max_value=1000.0, value=None, step=0.001)
        col1, col2 = st.columns(2)
        with col1: 
            Material = st.selectbox("Material", ["water"], index=0)
        with col2:
            m = st.number_input("Mass (KG)", min_value=0.0, value=1.0, step=0.1)
            
        TP_given = mode_T is not None and mode_P is not None
        disabled = TP_given
            
        if TP_given:
            # Borra valores previos de los intensivos
            for key in ["v_input", "u_input", "h_input", "s_input", "x_input"]:
                if key in st.session_state:
                    st.session_state[key] = None
        
        with st.expander("Intensive properties"):
            v = u = h = s = x = None
            selected = st.radio("Select the intensive property you want to input:", ["Specific volume (v)", "Internal energy (u)", "Enthalpy (h)", "Entropy (s)", "Quality (x)"], index=0, key="int_prop_radio", disabled=disabled)
            if selected == "Specific volume (v)":
                v = st.number_input("Specific volume (v)", min_value=0.0, value=None, step=0.01, disabled=disabled, key="v_input")
            elif selected == "Internal energy (u)":
                u = st.number_input("Internal energy (u)", min_value=0.0, value=None, step=0.01, disabled=disabled, key="u_input")
            elif selected == "Enthalpy (h)":
                h = st.number_input("Enthalpy (h)", min_value=0.0, value=None, step=0.01, disabled=disabled, key="h_input")
            elif selected == "Entropy (s)":
                s = st.number_input("Entropy (s)", min_value=0.0, value=None, step=0.01, disabled=disabled, key="s_input")
            elif selected == "Quality (x)":
                with st.columns(3)[1]:
                    if "x_input" not in st.session_state or st.session_state["x_input"] is None:
                        st.session_state["x_input"] = 0.0
                    st.slider("Quality (x)", min_value=0.0, max_value=1.0, value=st.session_state["x_input"],
                              step=0.01, key="x_input")
                    
        if mode_T is None and mode_P is None:
            Tval = None
            Pval = None
        elif mode_T is not None and mode_P is None:
            Tval = mode_T
            Pval = None
        elif mode_P is not None and mode_T is None:
            Pval = mode_P
            Tval = None
        elif mode_T is not None and mode_P is not None:
            Tval = mode_T
            Pval = mode_P
        if st.button("Calculate", type="primary"):
            try:
                st_state = thermo.State(Material=Material, m=m, T=Tval, P=Pval, x=x, v=v, u=u, h=h, s=s, Velocity=None, Height=None)
                df = st_state.Data_Frame()
                df_clean = df.T.dropna(how='all') 
                st.dataframe(df_clean, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")
                

    with st.expander("About this version"):
        st.markdown("<div style='text-align: center;'><h2 style='font-size:16px;'>ABOUT</h2></div>", unsafe_allow_html=True)
        st.markdown(
            "- ThermoFlow is a web application intended for analyzing thermodynamic processes on industrial systems.\n"
            "- Reads and interpolates tables based on input, giving the user the entirety of properties for the given information (These vary according to table needed according to data input: Temperature, Pressure & Superheated/Compressed)\n"
            "- Allows for quality input, calculating automatically the net specific values\n"
        )   
        st.markdown("<div style='text-align: center;'><h2 style='font-size:16px;'>LIMITATIONS</h2></div>", unsafe_allow_html=True)
        st.markdown(
            "- Only water accepted for now (V1.0)\n"
            "- Can only calculate state properties\n"
        )   
        st.markdown("<div style='text-align: center;'><h2 style='font-size:16px;'>INCOMING</h2></div>", unsafe_allow_html=True)
        st.markdown(
            "- Many future versions are planned, however, the next version will include cycles and it's related calculations; such as: work, heat transfer, etc.\n"
        )

if __name__ == "__main__":
    main()
