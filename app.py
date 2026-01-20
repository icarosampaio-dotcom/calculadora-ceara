import streamlit as st
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="Calculadora de Vazão - Cagece", layout="wide")

# 2. Carregamento dos dados
@st.cache_data
def carregar_dados():
    try:
        return pd.read_csv('municipios.csv')
    except:
        st.error("Erro: Arquivo 'municipios.csv' não encontrado.")
        return None

df = carregar_dados()

# 3. Logo da Cagece (Link público estável)
st.image("https://upload.wikimedia.org/wikipedia/pt/2/23/Logo_Cagece.png", width=250)

st.title("Calculadora de Vazão - Estado do Ceará")
st.markdown("---")

if df is not None:
    with st.sidebar:
        st.header("⚙️ Parâmetros de Projeto")
        cidade = st.selectbox("Selecione o Município:", sorted(df['municipio'].unique()))
        area = st.number_input("Área da Bacia (Hectares - ha):", min_value=0.0, step=0.1)
        c_esc = st.number_input("Coeficiente de Escoamento (C):", min_value=0.0, max_value=1.0, step=0.01)
        tr = st.number_input("Tempo de Retorno (Anos):", min_value=1, value=10)
        tc = st.number_input("Tempo de Concentração (min):", min_value=2, value=15)

    if area > 0 and c_esc > 0:
        p = df[df['municipio'] == cidade].iloc[0]
        K, a, b, c_coef = p['K'], p['a'], p['b'], p['c']
        
        i_min = (K * (tr ** a)) / ((tc + b) ** c_coef)
        i_hora = i_min * 60
        q_m3s = (c_esc * i_hora * area) / 360
        q_ls = q_m3s * 1000

        # Resultados Principais
        c1, c2, c3 = st.columns(3)
        c1.metric("Intensidade (i)", f"{i_hora:.2f} mm/h")
        c2.metric("Vazão de Pico (Q)", f"{q_m3s:.4f} m³/s")
        c3.metric("Vazão em Litros", f"{q_ls:.2f} L/s")

        # MEMÓRIA DE CÁLCULO DETALHADA
        st.subheader("📄 Memória de Cálculo Detalhada")
        with st.container():
            st.markdown(f"#### 1. Equação IDF para {cidade}")
            st.latex(r"i = \frac{K \cdot Tr^{a}}{(tc + b)^{c}}")
            
            st.write(f"**Parâmetros extraídos para {cidade}:**")
            st.write(f"K = {K} | a = {a} | b = {b} | c = {c_coef}")
            
            st.markdown("**Substituição dos valores:**")
            st.latex(r"i = \frac{" + f"{K}" + r"\cdot " + f"{tr}" + r"^{" + f"{a}" + r"}}{(" + f"{tc}" + r" + " + f"{b}" + r")^{" + f"{c_coef}" + r"}}")
            st.write(f"Resultado: **{i_hora:.2f} mm/h**")
            
            st.markdown("---")
            st.markdown("#### 2. Método Racional")
            st.latex(r"Q = \frac{C \cdot i \cdot A}{360}")
            st.write(f"C = {c_esc} | i = {i_hora:.2f} mm/h | A = {area} ha")
            st.latex(r"Q = \frac{" + f"{c_esc}" + r" \cdot " + f"{i_hora:.2f}" + r" \cdot " + f"{area}" + r"}{360}")
            st.success(f"Vazão Final: **{q_m3s:.4f} m³/s** ou **{q_ls:.2f} L/s**")

        st.subheader("📊 Curva IDF")
        durs = list(range(5, 121, 5))
        ints = [(K * (tr ** a)) / ((d + b) ** c_coef) * 60 for d in durs]
        st.line_chart(pd.DataFrame({"Duração (min)": durs, "i (mm/h)": ints}).set_index("Duração (min)"))

    else:
        st.info("Preencha a Área e o Coeficiente C para realizar o cálculo.")

st.markdown("---")
st.caption("Cagece - Gerência de Projetos")
