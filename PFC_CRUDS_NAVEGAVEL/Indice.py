import streamlit as st

# Configuração da página inicial
st.set_page_config(page_title="SolidariHub", page_icon="🤝", layout="wide")

# Redirecionamento automático para a página Home
st.markdown("""
    <meta http-equiv="refresh" content="0; url=./Home">
""", unsafe_allow_html=True)

# Navegação personalizada 

pg = st.navigation([
    st.page("pages/Home.py", title="🏠 Início"),
    st.page("pages/Doador.py", title="👤 Cadastro de Doador"),
    st.page("pages/ONG.py", title="🏢 Cadastro de Instituição"),
    st.page("pages/Itens.py", title="📦 Gerenciar Itens"),
    st.page("pages/Listas.py", title="📝 Gerenciar Listas"),
    st.page("pages/ItensLista.py", title="📋 Itens de uma Lista"),
    st.page("pages/Intencao_de_Doacao.py", title="🎯 Intenção de Doação"),
    st.page("pages/Pedidos.py", title="📨 Gerenciar Pedidos"),
    st.page("pages/ItensPedido.py", title="📦 Itens do Pedido"),
])
pg.run()
