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
    st.page("pages/doador_BD.py", title="👤 Cadastro de Doador"),
    st.page("pages/ong_BD.py", title="🏢 Cadastro de Instituição"),
    st.page("pages/item_BD.py", title="📦 Gerenciar Itens"),
    st.page("pages/lista_BD.py", title="📝 Gerenciar Listas"),
    st.page("pages/lista_item.py", title="📋 Itens de uma Lista"),
    st.page("pages/item_catalogo_BD.py", title="📚 Catálogo de Itens"),
    st.page("pages/intencaodoacao_BD.py", title="🎯 Intenção de Doação"),
    st.page("pages/pedido_BD.py", title="📨 Gerenciar Pedidos"),
    st.page("pages/pedido_item.py", title="📦 Itens do Pedido"),
])
pg.run()
