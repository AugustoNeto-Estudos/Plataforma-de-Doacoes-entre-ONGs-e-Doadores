import streamlit as st

# Configurações da página
st.set_page_config(
    page_title="SolidariHub | Plataforma de Doações",
    page_icon="🤝",
    layout="wide"
)


# ---- HEADER ----
st.title("🤝 SolidariHub")
st.subheader("Conectando Doadores e Instituições de forma simples e rápida.")
st.markdown("---")

# ---- HERO SECTION ----
col1, col2 = st.columns(2)

with col1:
    st.header("💡 O que é a SolidariHub?")
    st.write("""
    A **SolidariHub** é uma plataforma que conecta **ONGs** e **Doadores** em um só lugar.
    
    - Cadastre sua instituição em minutos  
    - Divulgue suas listas de doações  
    - Receba apoio de doadores de todo o Brasil
    """)

    if st.button("Quero Cadastrar minha Instituição"):
        st.switch_page("pages/ONG.py")

with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/1041/1041883.png", width=300)

st.markdown("---")

# ---- BENEFÍCIOS ----
st.header("✨ Benefícios")
col1, col2, col3 = st.columns(3)

with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2620/2620651.png", width=80)
    st.subheader("Rápido")
    st.write("Cadastre e publique pedidos de doação em poucos cliques.")

with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.subheader("Confiável")
    st.write("Instituições passam por aprovação do administrador.")

with col3:
    st.image("https://cdn-icons-png.flaticon.com/512/616/616408.png", width=80)
    st.subheader("Solidário")
    st.write("Mais visibilidade para sua ONG e impacto positivo na sociedade.")

st.markdown("---")

# ---- CALL TO ACTION ----
st.header("🚀 Pronto para começar?")
st.write("Cadastre sua instituição agora e comece a receber doações!")

col1, col2 = st.columns(2)

with col1:
    if st.button("👉 Criar Conta como Instituição"):
        st.switch_page("pages/ONG.py")

with col2:
    if st.button("🧑‍🤝‍🧑 Criar Conta como Doador"):
        st.switch_page("pages/Doador.py")
