import streamlit as st
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="HidroCE - Cálculo de Vazão", layout="wide")

# 2. Carregamento dos dados
@st.cache_data
def carregar_dados():
    try:
        return pd.read_csv('municipios.csv')
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")
        return None

df = carregar_dados()

# 3. Título
st.title("🌊 Calculadora de Vazão - Estado do Ceará")
st.markdown("### Método Racional com Equações IDF (Batista, 2018)")

if df is not None:
    # 4. Barra Lateral
    with st.sidebar:
        st.header("⚙️ Parâmetros")
        cidade = st.selectbox("1. Município:", sorted(df['municipio'].unique()))
        area = st.number_input("2. Área (ha):", min_value=0.0, step=0.1)
        c_esc = st.number_input("3. Coeficiente C:", min_value=0.0, max_value=1.0, step=0.01)
        tr = st.number_input("4. TR (Anos):", min_value=1, value=10)
        tc = st.number_input("5. Tc (min):", min_value=2, value=15)

    # 5. Cálculos
    if area > 0 and c_esc > 0:
        p = df[df['municipio'] == cidade].iloc[0]
        
        # Intensidade i = (K * Tr^a) / (tc + b)^c
        i_min = (p['K'] * (tr ** p['a'])) / ((tc + p['b']) ** p['c'])
        i_hora = i_min * 60
        
        # Vazão Q = (C * i * A) / 360
        q_m3s = (c_esc * i_hora * area) / 360
        q_ls = q_m3s * 1000

        #
