import streamlit as st
import bcrypt
from ONG import listar_ongs, cadastrar_ong
import time

# Oculta a sidebar visualmente
st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="stSidebarContent"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# Configuração da página
st.set_page_config(page_title="Login ONG | SolidariHub", page_icon="🏢", layout="centered")

# Garante que a página ativa seja "LoginONG"
if "pagina" not in st.session_state or st.session_state.pagina != "LoginONG":
    st.session_state.pagina = "LoginONG"

st.title("🏢 Login de ONGs")
st.markdown("---")

def verificar_senha(senha_digitada, senha_hash):
    try:
        senha_hash = str(senha_hash).strip().replace("\n", "").replace(" ", "")
        return bcrypt.checkpw(senha_digitada.encode(), senha_hash.encode())
    except Exception:
        return False

def hash_senha(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode("utf-8").strip()

if "modo_ong" not in st.session_state:
    st.session_state.modo_ong = "login"

if st.session_state.modo_ong == "login":
    st.subheader("🔐 Acesse sua conta de ONG")
    feedback_login = st.empty()

    with st.form("form_login_ong"):
        email = st.text_input("Email").strip().lower()
        senha = st.text_input("Senha", type="password")
        submit_login = st.form_submit_button("Entrar")

    if submit_login:
        if not email or not senha:
            feedback_login.warning("⚠️ Email e senha são obrigatórios.")
        else:
            try:
                # Login de administrador via ONG
                if email == "admin@admin" and senha == "senhaadmin":
                    feedback_login.success("✅ Login de administrador reconhecido!")
                    st.markdown('<meta http-equiv="refresh" content="0; url=Administracao">', unsafe_allow_html=True)
                    st.stop()

                ongs = listar_ongs()
                ong = next((u for u in ongs if u.get("email", "").strip().lower() == email), None)

                if ong and verificar_senha(senha, ong.get("senha", "")):
                    if not ong.get("status_conta"):
                        feedback_login.warning("⚠️ Sua conta está inativa. Aguarde liberação do administrador.")
                    elif ong.get("status_verificacao") != 1:
                        feedback_login.warning("⚠️ Sua ONG ainda não foi aprovada pelo administrador.")
                    else:
                        nome_exibido = ong.get("nome") or ong.get("email")
                        feedback_login.success(f"✅ Login bem-sucedido! Bem-vindo(a), {nome_exibido}")
                else:
                    feedback_login.error("❌ Credenciais inválidas ou conta não encontrada.")
            except Exception as e:
                feedback_login.error(f"Erro inesperado: {str(e)[:200]}")

    st.markdown("---")
    st.write("🔑 Esqueceu sua senha?")
    st.markdown('<a href="RecuperarSenha" target="_self"><button style="width:100%">🔑 Recuperar Senha</button></a>', unsafe_allow_html=True)

    st.markdown("---")
    st.write("Ainda não tem conta?")
    if st.button("📝 Cadastrar ONG"):
        st.session_state.modo_ong = "cadastro"
        st.rerun()

elif st.session_state.modo_ong == "cadastro":
    st.subheader("📝 Cadastro de ONG")
    feedback_cadastro = st.empty()

    with st.form("form_cadastro_ong"):
        cnpj = st.text_input("CNPJ").strip()
        nome = st.text_input("Nome da Instituição").strip()
        cep = st.text_input("CEP").strip()
        contato = st.text_input("Contato").strip()
        email = st.text_input("Email").strip().lower()
        senha = st.text_input("Senha", type="password")
        descricao = st.text_area("Descrição da Instituição").strip()
        submit_cadastro = st.form_submit_button("Cadastrar")

    if submit_cadastro:
        if not cnpj or not nome or not email or not senha:
            feedback_cadastro.warning("⚠️ CNPJ, Nome, Email e Senha são obrigatórios.")
        else:
            senha_hash = hash_senha(senha)
            sucesso, mensagem = cadastrar_ong(
                cnpj, nome, cep, contato, email, senha_hash,
                status_verificacao=0,
                status_conta=False,
                descricao=descricao
            )
            mensagem = str(mensagem)[:200]
            if sucesso:
                feedback_cadastro.success("✅ Cadastro realizado com sucesso! Aguarde aprovação do administrador.")
                st.session_state.modo_ong = "login"

                st.rerun()
            else:
                feedback_cadastro.error(mensagem)

    st.markdown("---")
    if st.button("🔙 Já tenho conta (Voltar para Login)"):
        st.session_state.modo_ong = "login"
        st.rerun()
