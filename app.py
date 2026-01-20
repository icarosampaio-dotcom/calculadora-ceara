{\rtf1\ansi\ansicpg1252\cocoartf2706
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
\
# Configura\'e7\'e3o visual da p\'e1gina\
st.set_page_config(page_title="HidroCE - C\'e1lculo de Vaz\'e3o", layout="wide")\
\
# Fun\'e7\'e3o para carregar o banco de dados dos 184 munic\'edpios\
@st.cache_data\
def carregar_dados():\
    try:\
        # L\'ea o arquivo CSV que criamos com os dados do PDF\
        return pd.read_csv('municipios.csv')\
    except:\
        st.error("Erro: O arquivo 'municipios.csv' n\'e3o foi encontrado!")\
        return None\
\
df = carregar_dados()\
\
# Cabe\'e7alho do Programa\
st.title("\uc0\u55356 \u57098  Calculadora de Vaz\'e3o - Estado do Cear\'e1")\
st.markdown("### M\'e9todo Racional com Equa\'e7\'f5es IDF (Batista, 2018)")\
st.write("Esta ferramenta calcula a vaz\'e3o de pico utilizando as equa\'e7\'f5es espec\'edficas para cada um dos 184 munic\'edpios cearenses.")\
\
if df is not None:\
    # Interface Lateral (Barra de ferramentas)\
    with st.sidebar:\
        st.header("\uc0\u9881 \u65039  Par\'e2metros do Projeto")\
        \
        # Lista de munic\'edpios extra\'edda do CSV\
        municipio = st.selectbox("1. Selecione o Munic\'edpio:", sorted(df['municipio'].unique()))\
        \
        # Entradas num\'e9ricas\
        area = st.number_input("2. \'c1rea da Bacia (Hectares - ha):", min_value=0.0, step=0.1, help="\'c1rea total que contribui para o escoamento.")\
        c_esc = st.number_input("3. Coeficiente de Escoamento (C):", min_value=0.0, max_value=1.0, step=0.01, help="Depende do tipo de solo e ocupa\'e7\'e3o.")\
        tr = st.number_input("4. Tempo de Retorno (Anos):", min_value=1, value=10, help="Per\'edodo de recorr\'eancia da chuva.")\
        tc = st.number_input("5. Tempo de Concentra\'e7\'e3o (min):", min_value=2, value=15, help="Tempo que a \'e1gua leva para percorrer da parte mais distante at\'e9 a sa\'edda.")\
\
    # L\'f3gica de C\'e1lculo\
    if area > 0 and c_esc > 0:\
        # Busca os par\'e2metros K, a, b, c da cidade selecionada\
        p = df[df['municipio'] == cidade].iloc[0]\
        \
        # 1. C\'e1lculo da Intensidade (i) em mm/min (conforme f\'f3rmula da disserta\'e7\'e3o)\
        # i = (K * Tr^a) / (tc + b)^c\
        i_min = (p['K'] * (tr ** p['a'])) / ((tc + p['b']) ** p['c'])\
        \
        # 2. Convers\'e3o para mm/h (necess\'e1rio para o M\'e9todo Racional padr\'e3o)\
        i_hora = i_min * 60\
        \
        # 3. C\'e1lculo da Vaz\'e3o Q (m\'b3/s) -> Q = (C * i * A) / 360\
        q_m3s = (c_esc * i_hora * area) / 360\
        q_ls = q_m3s * 1000\
\
        # Exibi\'e7\'e3o dos Resultados em cart\'f5es\
        st.divider()\
        col1, col2, col3 = st.columns(3)\
        \
        with col1:\
            st.metric("Intensidade da Chuva (i)", f"\{i_hora:.2f\} mm/h")\
        with col2:\
            st.metric("Vaz\'e3o de Pico (Q)", f"\{q_m3s:.4f\} m\'b3/s")\
        with col3:\
            st.metric("Vaz\'e3o em Litros", f"\{q_ls:.2f\} L/s")\
\
        # Se\'e7\'e3o de Mem\'f3ria de C\'e1lculo para o Projetista\
        with st.expander("\uc0\u55357 \u56516  Ver Detalhes e Mem\'f3ria de C\'e1lculo"):\
            st.write(f"**Munic\'edpio Selecionado:** \{cidade\}")\
            st.write(f"**Par\'e2metros IDF extra\'eddos:** K=\{p['K']\}, a=\{p['a']\}, b=\{p['b']\}, c=\{p['c']\}")\
            st.latex(r"i = \\frac\{" + f"\{p['K']\}" + r"\\cdot Tr^\{" + f"\{p['a']\}" + r"\}\}\{(tc + " + f"\{p['b']\}" + r")^\{" + f"\{p['c']\}" + r"\}\}")\
            st.write(f"Resultando em: **\{i_hora:.2f\} mm/h**")\
            st.markdown("---")\
            st.write("**F\'f3rmula do M\'e9todo Racional Aplicada:**")\
            st.latex(r"Q = \\frac\{C \\cdot i \\cdot A\}\{360\}")\
            st.write(f"Onde: C=\{c_esc\}, i=\{i_hora:.2f\} mm/h, A=\{area\} ha")\
\
        # Gr\'e1fico din\'e2mico da Curva IDF para o munic\'edpio\
        st.subheader(f"\uc0\u55357 \u56522  Curva IDF - \{cidade\} (TR = \{tr\} anos)")\
        tempos = list(range(5, 121, 5))\
        intensidades = [(p['K'] * (}