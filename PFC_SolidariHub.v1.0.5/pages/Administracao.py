import streamlit as st
from ONG import listar_ongs, atualizar_status_ong, atualizar_status_verificacao_ong, excluir_ong
from Doador import listar_doadores, atualizar_status_doador, excluir_doador

# Oculta a sidebar visualmente
st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="stSidebarContent"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# Configuração da página
st.set_page_config(page_title="Administração | SolidariHub", page_icon="🛠️", layout="wide")

# Garante que a página ativa seja "Administracao"
if "pagina" not in st.session_state or st.session_state.pagina != "Administracao":
    st.session_state.pagina = "Administracao"

st.title("🛠️ Painel Administrativo")
st.markdown("---")

# Botões de navegação
col_nav1, col_nav2 = st.columns([1, 1])
with col_nav1:
    if st.button("🏠 Voltar à Home", key="btn_voltar_home"):
        st.markdown('<meta http-equiv="refresh" content="0; url=Home">', unsafe_allow_html=True)
        st.stop()
with col_nav2:
    if st.button("🔄 Recarregar Dados", key="btn_recarregar_dados"):
        st.rerun()

st.markdown("---")

# Seção de ONGs
st.subheader("📋 ONGs cadastradas")
ongs = listar_ongs()
for idx, ong in enumerate(ongs):
    with st.expander(f"🏢 {ong['nome']} ({ong['email']})", expanded=False):
        st.write(f"CNPJ: {str(ong['CNPJ_ID'])}")

        status_map = {0: "⏳ Pendente", 1: "✅ Aprovada", 2: "❌ Recusada"}
        status_verificacao = status_map.get(ong.get("status_verificacao", 0), "❓ Desconhecido")
        status_conta = "🟢 Ativa" if ong.get("status_conta") else "🔴 Inativa"

        st.write(f"Status Verificação: {status_verificacao}")
        st.write(f"Status Conta: {status_conta}")

        st.markdown("**🔧 Atualizar Verificação:**")
        col_ver1, col_ver2, col_ver3 = st.columns(3)
        with col_ver1:
            if st.button("✅ Aprovar", key=f"btn_ver_aprovar_{idx}"):
                sucesso, msg = atualizar_status_verificacao_ong(ong['CNPJ_ID'], 1)
                st.toast(str(msg)) if sucesso else st.toast(str(msg), icon="⚠️")
                st.rerun()
        with col_ver2:
            if st.button("⏳ Pendente", key=f"btn_ver_pendente_{idx}"):
                sucesso, msg = atualizar_status_verificacao_ong(ong['CNPJ_ID'], 0)
                st.toast(str(msg)) if sucesso else st.toast(str(msg), icon="⚠️")
                st.rerun()
        with col_ver3:
            if st.button("❌ Recusar", key=f"btn_ver_recusar_{idx}"):
                sucesso, msg = atualizar_status_verificacao_ong(ong['CNPJ_ID'], 2)
                st.toast(str(msg)) if sucesso else st.toast(str(msg), icon="⚠️")
                st.rerun()

        st.markdown("**⚙️ Atualizar Status da Conta:**")
        col_conta1, col_conta2 = st.columns(2)
        with col_conta1:
            if st.button("🟢 Ativar Conta", key=f"btn_conta_ativar_{idx}"):
                sucesso, msg = atualizar_status_ong(ong['CNPJ_ID'], True)
                st.toast(str(msg)) if sucesso else st.toast(str(msg), icon="⚠️")
                st.rerun()
        with col_conta2:
            if st.button("🔴 Desativar Conta", key=f"btn_conta_desativar_{idx}"):
                sucesso, msg = atualizar_status_ong(ong['CNPJ_ID'], False)
                st.toast(str(msg)) if sucesso else st.toast(str(msg), icon="⚠️")
                st.rerun()

        st.markdown("**🗑️ Exclusão permanente (LGPD):**")
        if st.button("🗑️ Excluir ONG permanentemente", key=f"btn_excluir_ong_{idx}"):
            sucesso, msg = excluir_ong(ong['CNPJ_ID'])
            st.toast(str(msg)) if sucesso else st.toast(str(msg), icon="⚠️")
            st.rerun()

st.markdown("---")

# Seção de Doadores
st.subheader("👤 Doadores cadastrados")
doadores = listar_doadores()
for idx, doador in enumerate(doadores):
    with st.expander(f"👤 {doador['nome']} ({doador['email']})", expanded=False):
        st.write(f"CPF: {str(doador['CPF_ID'])}")
        status_conta = "🟢 Ativa" if doador.get("status_conta") else "🔴 Inativa"
        st.write(f"Status Conta: {status_conta}")

        col_doador1, col_doador2 = st.columns(2)
        with col_doador1:
            if st.button("✅ Ativar", key=f"btn_doador_ativar_{idx}"):
                sucesso, msg = atualizar_status_doador(doador['CPF_ID'], True)
                st.toast(str(msg)) if sucesso else st.toast(str(msg), icon="⚠️")
                st.rerun()
        with col_doador2:
            if st.button("❌ Desativar", key=f"btn_doador_desativar_{idx}"):
                sucesso, msg = atualizar_status_doador(doador['CPF_ID'], False)
                st.toast(str(msg)) if sucesso else st.toast(str(msg), icon="⚠️")
                st.rerun()

        st.markdown("**🗑️ Exclusão permanente (LGPD):**")
        if st.button("🗑️ Excluir Doador permanentemente", key=f"btn_excluir_doador_{idx}"):
            sucesso, msg = excluir_doador(doador['CPF_ID'])
            st.toast(str(msg)) if sucesso else st.toast(str(msg), icon="⚠️")
            st.rerun()
