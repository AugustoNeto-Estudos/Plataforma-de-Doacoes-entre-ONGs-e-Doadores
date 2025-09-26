import streamlit as st
import bcrypt
from Doador import listar_doadores, cadastrar_doador, doador_esta_ativo
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
st.set_page_config(page_title="Login Doador | SolidariHub", page_icon="👤", layout="centered")

# Garante que a página ativa seja "LoginDoador"
if "pagina" not in st.session_state or st.session_state.pagina != "LoginDoador":
    st.session_state.pagina = "LoginDoador"

st.title("👤 Login de Doadores")
st.markdown("---")

def verificar_senha(senha_digitada, senha_hash):
    try:
        senha_hash = str(senha_hash).strip().replace("\n", "").replace(" ", "")
        return bcrypt.checkpw(senha_digitada.encode(), senha_hash.encode())
    except Exception:
        return False

def hash_senha(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode("utf-8").strip()

if "modo" not in st.session_state:
    st.session_state.modo = "login"

if st.session_state.modo == "login":
    st.subheader("🔐 Acesse sua conta de doador")
    feedback_login = st.empty()

    with st.form("form_login_doador"):
        email = st.text_input("Email").strip().lower()
        senha = st.text_input("Senha", type="password")
        submit_login = st.form_submit_button("Entrar")

    if submit_login:
        if not email or not senha:
            feedback_login.warning("⚠️ Email e senha são obrigatórios.")
        else:
            try:
                # Login de administrador via doador
                if email == "admin@admin" and senha == "senhaadmin":
                    feedback_login.success("✅ Login de administrador reconhecido!")
                    st.markdown('<meta http-equiv="refresh" content="0; url=Administracao">', unsafe_allow_html=True)
                    st.stop()

                usuarios = listar_doadores()
                usuario = next((u for u in usuarios if u.get("email", "").strip().lower() == email), None)

                if usuario and verificar_senha(senha, usuario.get("senha", "")):
                    if not doador_esta_ativo(email):
                        feedback_login.warning("⚠️ Sua conta ainda não está ativa. Aguarde aprovação do administrador.")
                    else:
                        nome_exibido = usuario.get("nome") or usuario.get("email")
                        feedback_login.success(f"✅ Login bem-sucedido! Bem-vindo, {nome_exibido}")
                else:
                    feedback_login.error("❌ Credenciais inválidas ou conta não encontrada.")
            except Exception as e:
                feedback_login.error(f"Erro inesperado: {str(e)[:200]}")

    st.markdown("---")
    st.write("🔑 Esqueceu sua senha?")
    st.markdown('<a href="RecuperarSenha" target="_self"><button style="width:100%">🔑 Recuperar Senha</button></a>', unsafe_allow_html=True)

    st.markdown("---")
    st.write("Ainda não tem conta?")
    if st.button("📝 Cadastrar-se como Doador"):
        st.session_state.modo = "cadastro"
        st.rerun()

elif st.session_state.modo == "cadastro":
    st.subheader("📝 Cadastro de Doador")
    feedback_cadastro = st.empty()

    with st.form("form_cadastro_doador"):
        cpf = st.text_input("CPF").strip()
        nome = st.text_input("Nome").strip()
        email = st.text_input("Email").strip().lower()
        contato = st.text_input("Contato").strip()
        senha = st.text_input("Senha", type="password")
        submit_cadastro = st.form_submit_button("Cadastrar")

    if submit_cadastro:
        if not cpf or not nome or not email or not senha:
            feedback_cadastro.warning("⚠️ CPF, Nome, Email e Senha são obrigatórios.")
        else:
            senha_hash = hash_senha(senha)
            sucesso, mensagem = cadastrar_doador(cpf, nome, email, contato, senha_hash, status_conta=False)
            mensagem = str(mensagem)[:200]
            if sucesso:
                feedback_cadastro.success("✅ Cadastro realizado com sucesso! Agora você pode fazer login.")
                time.sleep(3)  # espera 3 segundos
                st.session_state.modo = "login"
                st.rerun()
            else:
                feedback_cadastro.error(mensagem)

    st.markdown("---")
    if st.button("🔙 Já tenho conta (Voltar para Login)"):
        st.session_state.modo = "login"
        st.rerun()
