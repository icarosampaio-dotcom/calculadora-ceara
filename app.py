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

# 3. Título Principal
st.title("🌊 Calculadora de Vazão - Estado do Ceará")
st.markdown("### Método Racional com Equações IDF (Batista, 2018)")

if df is not None:
    # 4. Barra Lateral de Parâmetros
    with st.sidebar:
        st.header("⚙️ Parâmetros")
        # Definindo a variável 'cidade' corretamente
        cidade = st.selectbox("1. Município:", sorted(df['municipio'].unique()))
        area = st.number_input("2. Área (ha):", min_value=0.0, step=0.1)
        c_esc = st.number_input("3. Coeficiente C:", min_value=0.0, max_value=1.0, step=0.01)
        tr = st.number_input("4. TR (Anos):", min_value=1, value=10)
        tc = st.number_input("5. Tc (min):", min_value=2, value=15)

    # 5. Lógica de Cálculo (Só executa se Área e C forem maiores que zero)
    if area > 0 and c_esc > 0:
        # Busca os coeficientes K, a, b, c da cidade selecionada
        p = df[df['municipio'] == cidade].iloc[0]
        
        # Intensidade i (mm/h) = [(K * Tr^a) / (tc + b)^c] * 60
        i_min = (p['K'] * (tr ** p['a'])) / ((tc + p['b']) ** p['c'])
        i_hora = i_min * 60
        
        # Vazão Q (m³/s) = (C * i * A) / 360
        q_m3s = (c_esc * i_hora * area) / 360
        q_ls = q_m3s * 1000

        # 6. Exibição dos Resultados na Tela
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Intensidade (i)", f"{i_hora:.2f} mm/h")
        c2.metric("Vazão de Pico (Q)", f"{q_m3s:.4f} m³/s")
        c3.metric("Vazão em Litros", f"{q_ls:.2f} L/s")

        # Seção de Memória de Cálculo
        with st.expander("📄 Ver Detalhes do Cálculo"):
            st.write(f"**Dados de {cidade}:** K={p['K']}, a={p['a']}, b={p['b']}, c={p['c']}")
            st.latex(r"Q = \frac{C \cdot i \cdot A}{360}")
            st.info(f"O cálculo foi realizado com sucesso para uma área de {area} ha.")

        # Gráfico IDF
        st.subheader(f"📊 Curva IDF - {cidade}")
        minutos = list(range(5, 121, 5))
        intensidades = [(p['K'] * (tr ** p['a'])) / ((m + p['b']) ** p['c']) * 60 for m in minutos]
        st.line_chart(pd.DataFrame({"Duração (min)": minutos, "i (mm/h)": intensidades}).set_index("Duração (min)"))
    else:
        st.warning("⚠️ Por favor, ajuste a **Área** e o **Coeficiente C** na barra lateral para ver o cálculo.")

st.markdown("---")
st.caption("Desenvolvido para fins de engenharia com base em dados da UFC.")
