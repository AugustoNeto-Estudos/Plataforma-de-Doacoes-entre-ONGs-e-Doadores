import streamlit as st

# Oculta a sidebar visualmente
st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="stSidebarContent"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# Configuração da página
st.set_page_config(page_title="SolidariHub", page_icon="🤝", layout="wide")

# Título e subtítulo
st.title("🤝 SolidariHub")
st.subheader("Conectando Doadores e Instituições de forma simples e rápida.")
st.markdown("---")

# Seção explicativa
col1, col2 = st.columns(2)

with col1:
    st.header("💡 O que é a SolidariHub?")
    st.write("""
    A **SolidariHub** é uma plataforma que conecta **ONGs** e **Doadores** em um só lugar.
    
    - Cadastre sua instituição em minutos  
    - Divulgue suas listas de doações  
    - Receba apoio de doadores de todo o Brasil
    """)

with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/1041/1041883.png", width=300)

st.markdown("---")

# Seção de login
st.header("🚀 Acesse sua conta")
st.write("Escolha abaixo como deseja entrar:")

# Estilo dos botões
st.markdown("""
    <style>
    .button-container {
        display: flex;
        gap: 20px;
        margin-top: 20px;
    }
    .big-button-link {
        flex: 1;
        display: block;
        padding: 20px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        background-color: #4CAF50;
        color: white !important;
        border-radius: 8px;
        text-decoration: none !important;
        transition: background-color 0.3s ease;
    }
    .big-button-link:hover {
        background-color: #45a049;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Botões com redirecionamento direto
st.markdown("""
    <div class="button-container">
        <a href="LoginDoador" target="_self" class="big-button-link">👤 Login Doador</a>
        <a href="LoginONG" target="_self" class="big-button-link">🏢 Login ONG</a>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")
