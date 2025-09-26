import streamlit as st
from ONG import listar_ongs
from Doador import listar_doadores

# Oculta a sidebar visualmente
st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="stSidebarContent"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Recuperar Senha", page_icon="🔑", layout="centered")

st.title("🔑 Recuperar Senha")
st.write("Informe seu email para iniciar o processo de recuperação.")
st.markdown("---")

tipo = st.radio("Tipo de Conta", ["Doador", "ONG"])
email = st.text_input("Email")
feedback = st.empty()

if st.button("Verificar"):
    usuarios = listar_doadores() if tipo == "Doador" else listar_ongs()
    usuario = next((u for u in usuarios if u["email"] == email), None)
    if usuario:
        feedback.success("✅ Email localizado. Entre em contato com o administrador para redefinir sua senha.")
    else:
        feedback.error("❌ Email não encontrado.")
