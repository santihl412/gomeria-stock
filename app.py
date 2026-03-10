import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gomería Control Pro", page_icon="🛞", layout="wide")

# Estilos visuales
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 5px 5px 0px 0px; padding: 10px; }
    .stTabs [aria-selected="true"] { background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# Archivos de base de datos
DB_FILE = "inventario_gomeria.csv"
VENTAS_FILE = "ventas_gomeria.csv"

# Funciones de carga de datos
def cargar_datos():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce').fillna(0).astype(int)
        df['Precio_Venta'] = pd.to_numeric(df['Precio_Venta'], errors='coerce').fillna(0)
        return df
    return pd.DataFrame(columns=["Rodado", "Marca", "Modelo", "Cantidad", "Precio_Venta"])

def cargar_ventas():
    if os.path.exists(VENTAS_FILE):
        dfv = pd.read_csv(VENTAS_FILE)
        dfv['Total'] = pd.to_numeric(dfv['Total'], errors='coerce').fillna(0)
        return dfv
    return pd.DataFrame(columns=["Fecha", "Producto", "Cantidad", "Total"])

# --- BARRA LATERAL (ACCIONES) ---
st.sidebar.title("🚀 Panel de Control")
df = cargar_datos()

# A. AGREGAR STOCK
with st.sidebar.expander("➕ Cargar Nuevo Stock"):
    r_a = st.selectbox("Rodado", ["13", "14", "15", "16", "17", "18", "19", "20"], key="r_a")
    m_a = st.text_input("Marca", key="m_a")
    mo_a = st.text_input("Modelo", key="mo_a")
    c_a = st.number_input("Cantidad", min_value=1, step=1, key="c_a")
    p_a = st.number_input("Precio ($)", min_value=0, key="p_a")
    if st.sidebar.button("Registrar Ingreso"):
        if m_a and mo_a:
            nueva = pd.DataFrame([[r_a, m_a, mo_a, c_a, p_a]], columns=df.columns)
            df = pd.concat([df, nueva], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

# B. EDITAR
with st.sidebar.expander("📝 Editar Datos"):
    if not df.empty:
        op_ed = df.apply(lambda x: f"{x['Marca']} {x['Modelo']} (R{x['Rodado']})", axis=1).tolist()
        sel_ed = st.selectbox("Elegir neumático", op_ed, key="sel_ed")
        idx_ed = op_ed.index(sel_ed)
        ed_marca = st.text_input("Marca", value=df.iloc[idx_ed]['Marca'], key="ed_m")
        ed_precio = st.number_input("Precio ($)", value=float(df.iloc[idx_ed]['Precio_Venta']), key="ed_p")
        ed_cant = st.number_input("Cantidad Total", value=int(df.iloc[idx_ed]['Cantidad']), key="ed_c")
        if st.button("Actualizar Producto"):
            df.at[idx_ed, 'Marca'] = ed_marca
            df.at[idx_ed, 'Precio_Venta'] = ed_precio
            df.at[idx_ed, 'Cantidad'] = ed_cant
            df.to_csv(DB_FILE, index=False)
            st.rerun()

# C. VENTA (RESTAR)
with st.sidebar.expander("💸 Registrar Venta"):
    df_s = df[df['Cantidad'] > 0]
    if not df_s.empty:
        op_v = df_s.apply(lambda x: f"{x['Marca']} {x['Modelo']} (R{x['Rodado']})", axis=1).tolist()
        sel_v = st.selectbox("Seleccionar venta", op_v, key="sel_v")
        idx_v = df_s.index[op_v.index(sel_v)]
        max_v = int(df.iloc[idx_v]['Cantidad'])
        c_v = st.number_input("Cant. vendida", min_value=1, max_value=max_v, step=1)
        if st.button("Confirmar Venta"):
            df.at[idx_v, 'Cantidad'] -= c_v
            df.to_csv(DB_FILE, index=False)
            # Guardar venta en historial
            tot = c_v * df.iloc[idx_v]['Precio_Venta']
            n_v = {"Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"), "Producto": sel_v, "Cantidad": c_v, "Total": tot}
            df_v = cargar_ventas()
            df_v = pd.concat([df_v, pd.DataFrame([n_v])], ignore_index=True)
            df_v.to_csv(VENTAS_FILE, index=False)
            st.balloons()
            st.rerun()

# D. ELIMINAR
with st.sidebar.expander("🗑️ Borrar Producto"):
    if not df.empty:
        op_e = df.apply(lambda x: f"{x['Marca']} {x['Modelo']} (R{x['Rodado']})", axis=1).tolist()
        sel_e = st.selectbox("Eliminar permanentemente", op_e, key="sel_e")
        idx_e = op_e.index(sel_e)
        if st.button("ELIMINAR AHORA"):
            df = df.drop(df.index[idx_e])
            df.to_csv(DB_FILE, index=False)
            st.rerun()

# --- CUERPO PRINCIPAL ---
st.title("🛞 Gestión de Gomería")
tab1, tab2 = st.tabs(["📋 Inventario de Stock", "💰 Caja e Historial"])

with tab1:
    df_act = cargar_datos()
    busq = st.text_input("🔍 Buscar por Marca, Modelo o Rodado...")
    if not df_act.empty:
        mask = df_act.apply(lambda r: busq.lower() in str(r).lower(), axis=1)
        st.dataframe(df_act[mask], use_container_width=True, height=500)
    else:
        st.info("No hay stock cargado.")

with tab2:
    st.subheader("Ventas del Periodo")
    df_v = cargar_ventas()
    if not df_v.empty:
        st.metric("Total Recaudado", f"${df_v['Total'].sum():,.2f}")
        st.dataframe(df_v.iloc[::-1], use_container_width=True) # Lo último arriba
        if st.button("Limpiar todo el historial"):
            if os.path.exists(VENTAS_FILE): os.remove(VENTAS_FILE)
            st.rerun()
    else:
        st.info("Todavía no hay ventas registradas.")