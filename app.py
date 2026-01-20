import streamlit as st
import pandas as pd

# Configuração visual da página
st.set_page_config(page_title="HidroCE - Cálculo de Vazão", layout="wide")

# Função para carregar o banco de dados dos 184 municípios
@st.cache_data
def carregar_dados():
    try:
        # Lê o arquivo CSV que criamos com os dados do PDF
        return pd.read_csv('municipios.csv')
    except:
        st.error("Erro: O arquivo 'municipios.csv' não foi encontrado!")
        return None

df = carregar_dados()

# Cabeçalho do Programa
st.title("🌊 Calculadora de Vazão - Estado do Ceará")
st.markdown("### Método Racional com Equações IDF (Batista, 2018)")
st.write("Esta ferramenta calcula a vazão de pico utilizando as equações específicas para cada um dos 184 municípios cearenses.")

if df is not None:
    # Interface Lateral (Barra de ferramentas)
    with st.sidebar:
        st.header("⚙️ Parâmetros do Projeto")
        
        # Lista de municípios extraída do CSV
        municipio = st.selectbox("1. Selecione o Município:", sorted(df['municipio'].unique()))
        
        # Entradas numéricas
        area = st.number_input("2. Área da Bacia (Hectares - ha):", min_value=0.0, step=0.1, help="Área total que contribui para o escoamento.")
        c_esc = st.number_input("3. Coeficiente de Escoamento (C):", min_value=0.0, max_value=1.0, step=0.01, help="Depende do tipo de solo e ocupação.")
        tr = st.number_input("4. Tempo de Retorno (Anos):", min_value=1, value=10, help="Período de recorrência da chuva.")
        tc = st.number_input("5. Tempo de Concentração (min):", min_value=2, value=15, help="Tempo que a água leva para percorrer da parte mais distante até a saída.")

    # Lógica de Cálculo
    if area > 0 and c_esc > 0:
        # Busca os parâmetros K, a, b, c da cidade selecionada
        p = df[df['municipio'] == cidade].iloc[0]
        
        # 1. Cálculo da Intensidade (i) em mm/min (conforme fórmula da dissertação)
        # i = (K * Tr^a) / (tc + b)^c
        i_min = (p['K'] * (tr ** p['a'])) / ((tc + p['b']) ** p['c'])
        
        # 2. Conversão para mm/h (necessário para o Método Racional padrão)
        i_hora = i_min * 60
        
        # 3. Cálculo da Vazão Q (m³/s) -> Q = (C * i * A) / 360
        q_m3s = (c_esc * i_hora * area) / 360
        q_ls = q_m3s * 1000

        # Exibição dos Resultados em cartões
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Intensidade da Chuva (i)", f"{i_hora:.2f} mm/h")
        with col2:
            st.metric("Vazão de Pico (Q)", f"{q_m3s:.4f} m³/s")
        with col3:
            st.metric("Vazão em Litros", f"{q_ls:.2f} L/s")

        # Seção de Memória de Cálculo para o Projetista
        with st.expander("📄 Ver Detalhes e Memória de Cálculo"):
            st.write(f"**Município Selecionado:** {cidade}")
            st.write(f"**Parâmetros IDF extraídos:** K={p['K']}, a={p['a']}, b={p['b']}, c={p['c']}")
            st.latex(r"i = \frac{" + f"{p['K']}" + r"\cdot Tr^{" + f"{p['a']}" + r"}}{(tc + " + f"{p['b']}" + r")^{" + f"{p['c']}" + r"}}")
            st.write(f"Resultando em: **{i_hora:.2f} mm/h**")
            st.markdown("---")
            st.write("**Fórmula do Método Racional Aplicada:**")
            st.latex(r"Q = \frac{C \cdot i \cdot A}{360}")
            st.write(f"Onde: C={c_esc}, i={i_hora:.2f} mm/h, A={area} ha")

        # Gráfico dinâmico da Curva IDF para o município
        st.subheader(f"📊 Curva IDF - {cidade} (TR = {tr} anos)")
        tempos = list(range(5, 121, 5))
        intensidades = [(p['K'] * (tr ** p['a'])) / ((t + p['b']) ** p['c']) * 60 for t in tempos]
        chart_data = pd.DataFrame({'Duração (min)': tempos, 'i (mm/h)': intensidades})
        st.line_chart(chart_data.set_index('Duração (min)'))

    else:
        st.info("💡 Por favor, insira a **Área** e o **Coeficiente C** na barra lateral para realizar o cálculo.")

# Rodapé informativo
st.markdown("---")
st.caption("Desenvolvido com base nos dados técnicos da Dissertação de Mestrado (UFC - 2018).")
