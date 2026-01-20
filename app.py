import streamlit as st
import pandas as pd

# 1. Configuração visual da página
st.set_page_config(page_title="HidroCE - Cálculo de Vazão", layout="wide")

# 2. Função para carregar o banco de dados dos 184 municípios
@st.cache_data
def carregar_dados():
    try:
        # Lê o arquivo CSV que você criou no repositório
        return pd.read_csv('municipios.csv')
    except Exception as e:
        st.error(f"Erro ao carregar 'municipios.csv': {e}")
        return None

df = carregar_dados()

# 3. Cabeçalho do Programa
st.title("🌊 Calculadora de Vazão - Estado do Ceará")
st.markdown("### Método Racional com Equações IDF (Batista, 2018)")

if df is not None:
    # 4. Interface Lateral (Parâmetros de Entrada)
    with st.sidebar:
        st.header("⚙️ Parâmetros do Projeto")
        
        # Correção aqui: nomeamos como 'cidade' para coincidir com o cálculo abaixo
        cidade = st.selectbox("1. Selecione o Município:", sorted(df['municipio'].unique()))
        
        area = st.number_input("2. Área da Bacia (Hectares - ha):", min_value=0.0, step=0.1)
        c_esc = st.number_input("3. Coeficiente de Escoamento (C):", min_value=0.0, max_value=1.0, step=0.01)
        tr = st.number_input("4. Tempo de Retorno (Anos):", min_value=1, value=10)
        tc = st.number_input("5. Tempo de Concentração (min):", min_value=2, value=15)

    # 5. Lógica de Cálculo e Exibição
    if area > 0 and c_esc > 0:
        # Busca os parâmetros K, a, b, c da cidade selecionada
        p = df[df['municipio'] == cidade].iloc[0]
        
        # Cálculo da Intensidade (i) em mm/min (Equação IDF)
        i_min = (p['K'] * (tr ** p['a'])) / ((tc + p['b']) ** p['c'])
        
        # Conversão para mm/h para usar no Método Racional
        i_hora = i_min * 60
        
        # Cálculo da Vazão Q (m³/s) -> Fórmula: Q = (C * i * A) / 360
        q_m3s = (c_esc * i_hora * area) / 360
        q_ls = q_m3s * 1000

        # Exibição dos Resultados em cartões destacados
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Intensidade (i)", f"{i_hora:.2f} mm/h")
        with col2:
            st.metric("Vazão de Pico (Q)", f"{q_
