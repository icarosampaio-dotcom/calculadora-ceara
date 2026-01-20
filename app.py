import streamlit as st
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="Calculadora de Vazão - Cagece", layout="wide")

# 2. Carregamento dos dados
@st.cache_data
def carregar_dados():
    try:
        return pd.read_csv('municipios.csv')
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")
        return None

df = carregar_dados()

# 3. Cabeçalho com Logo da Cagece (Link estável)
st.image("https://upload.wikimedia.org/wikipedia/pt/2/23/Logo_Cagece.png", width=250)

st.title("Calculadora de Vazão - Estado do Ceará")
st.markdown("### Método Racional com Equações IDF (Batista, 2018)")

if df is not None:
    # 4. Barra Lateral de Parâmetros
    with st.sidebar:
        st.header("⚙️ Parâmetros do Projeto")
        cidade = st.selectbox("1. Município:", sorted(df['municipio'].unique()))
        area = st.number_input("2. Área da Bacia (ha):", min_value=0.0, step=0.1)
        c_esc = st.number_input("3. Coeficiente de Escoamento (C):", min_value=0.0, max_value=1.0, step=0.01)
        tr = st.number_input("4. Tempo de Retorno (Anos):", min_value=1, value=10)
        tc = st.number_input("5. Tempo de Concentração (min):", min_value=2, value=15)

    # 5. Lógica de Cálculo
    if area > 0 and c_esc > 0:
        p = df[df['municipio'] == cidade].iloc[0]
        
        # Coeficientes da cidade
        K, a, b, c_coef = p['K'], p['a'], p['b'], p['c']
        
        # Cálculo da Intensidade (i)
        i_min = (K * (tr ** a)) / ((tc + b) ** c_coef)
        i_hora = i_min * 60
        
        # Cálculo da Vazão Q
        q_m3s = (c_esc * i_hora * area) / 360
        q_ls = q_m3s * 1000

        # 6. Exibição dos Resultados Principais
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Intensidade (i)", f"{i_hora:.2f} mm/h")
        with c2:
            st.metric("Vazão de Pico (Q)", f"{q_m3s:.4f} m³/s")
        with c3:
            st.metric("Vazão em Litros", f"{q_ls:.2f} L/s")

        # 7. Memória de Cálculo Detalhada
        st.subheader("📄 Memória de Cálculo Detalhada")
        with st.expander("Clique para expandir o passo a passo técnico"):
            st.markdown(f"#### 1. Equação IDF para {cidade}")
            st.write("A equação de intensidade-duração-frequência utilizada é:")
            st.latex(r"i = \frac{K \cdot Tr^{a}}{(tc + b)^{c}}")
            
            st.markdown("**Parâmetros aplicados:**")
            st.write(f"- K = {K}")
            st.write(f"- a = {a}")
            st.write(f"- b = {b}")
            st.write(f"- c = {c_coef}")
            
            st.markdown("**Substituição:**")
            st.latex(r"i = \frac{" + str(K) + r"\cdot " + str(tr) + r"^{" + str(a) + r"}}{( " + str(tc) + r" + " + str(b) + r" )^{" + str(c_coef) + r"}}")
            st.write(f"Resultado: i = {i_min:.4f} mm/min ou **{i_hora:.2f} mm/h**")
            
            st.divider()
            
            st.markdown("#### 2. Cálculo da Vazão (Método Racional)")
            st.latex(r"Q = \frac{C \cdot i \cdot A}{360}")
            st.write(f"Onde: C = {c_esc}, i = {i_hora:.2f} mm/h, A = {area} ha")
            st.latex(r"Q = \frac{" + str(c_esc) + r" \cdot " + f"{i_hora:.2f}" + r" \cdot " + str(area) + r"}{360}")
            st.write(f"Vazão Calculada: **{q_m3s:.4f} m³/s**")
            st.write(f"Convertendo para Litros: {q_m3s:.4f} * 1000 = **{q_ls:.2f} L/s**")

        # 8. Gráfico da Curva IDF
        st.subheader(f"📊 Curva IDF - {cidade}")
        minutos = list(range(5, 121, 5))
        intensidades = [(K * (tr ** a)) / ((m + b) ** c_coef) * 60 for m in minutos]
        st.line_chart(pd.DataFrame({"Duração (min)": minutos, "i (mm/h)": intensidades}).set_index("Duração (min)"))
        
    else:
        st.warning("⚠️ Ajuste a **Área** e o **Coeficiente C** na barra lateral para calcular.")

st.markdown("---")
st.caption("Ferramenta técnica desenvolvida com base na Dissertação de Mestrado de Tatiane Lima Batista (UFC/2018).")
