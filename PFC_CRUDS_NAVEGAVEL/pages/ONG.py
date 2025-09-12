import streamlit as st
from psycopg2 import Error
from conexao import criar_conexao

# ---------------------------
# CREATE - ONG
# ---------------------------
def cadastrar_ong(cnpj, nome, cep, contato, email, senha, status_verificacao, status_conta, descricao):
    conexao = None
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        sql = """
        INSERT INTO public."ong" 
        ("CNPJ_ID", nome, cep, contato, email, senha, status_verificacao, status_conta, descricao) 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        valores = (cnpj, nome, cep, contato, email, senha, status_verificacao, status_conta, descricao)
        cursor.execute(sql, valores)
        conexao.commit()
        return True, "✅ ONG cadastrada com sucesso!"
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

# ---------------------------
# READ - ONGs
# ---------------------------
def listar_ongs():
    conexao = None
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM public."ong"')
        registros = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        return [dict(zip(colunas, linha)) for linha in registros]
    except Error as erro:
        st.error(str(erro))
        return []
    finally:
        try:
            cursor.close()
            conexao.close()
        except:
            pass

# ---------------------------
# UPDATE - Todos os campos
# ---------------------------
def atualizar_ong(cnpj, nome, cep, contato, email, senha, status_verificacao, status_conta, descricao):
    conexao = None
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        sql = """
        UPDATE public."ong"
        SET nome=%s, cep=%s, contato=%s, email=%s, senha=%s,
            status_verificacao=%s, status_conta=%s, descricao=%s
        WHERE "CNPJ_ID" = %s
        """
        valores = (nome, cep, contato, email, senha, status_verificacao, status_conta, descricao, cnpj)
        cursor.execute(sql, valores)
        conexao.commit()
        return True, "✅ ONG atualizada com sucesso!"
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

# ---------------------------
# DELETE
# ---------------------------
def deletar_ong(cnpj):
    conexao = None
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        cursor.execute('DELETE FROM public."ong" WHERE "CNPJ_ID" = %s', (cnpj,))
        conexao.commit()
        if cursor.rowcount:
            return True, "✅ ONG deletada com sucesso!"
        else:
            return False, "⚠️ ONG não encontrada."
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

# ---------------------------
# Interface Streamlit
# ---------------------------
st.title("🏢 Gerenciar ONGs")

# Testar conexão
if st.button("🔌 Testar Conexão"):
    conexao = criar_conexao()
    if conexao:
        st.success("✅ Conexão estabelecida com sucesso!")
        conexao.close()
    else:
        st.error("❌ Erro ao conectar ao PostgreSQL.")

st.divider()

# CREATE
st.subheader("➕ Cadastrar nova ONG")
feedback_create = st.empty()
with st.form("form_inserir_ong"):
    cnpj = st.text_input("CNPJ")
    nome = st.text_input("Nome")
    cep = st.text_input("CEP")
    contato = st.text_input("Contato")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    status_verificacao = st.number_input("Status de Verificação (0=pendente, 1=verificado, 2=rejeitado)", min_value=0, max_value=2, step=1)
    status_conta = st.checkbox("Conta Ativa?")
    descricao = st.text_area("Descrição")
    submit_create = st.form_submit_button("Cadastrar")
if submit_create:
    if not cnpj or not nome or not email or not senha:
        feedback_create.warning("⚠️ Campos obrigatórios: CNPJ, Nome, Email e Senha.")
    else:
        sucesso, mensagem = cadastrar_ong(cnpj, nome, cep, contato, email, senha, status_verificacao, status_conta, descricao)
        mensagem = str(mensagem)
        if sucesso:
            feedback_create.success(mensagem)
        else:
            feedback_create.error(mensagem)

st.divider()

# READ
st.subheader("📋 Lista de ONGs")
if st.button("📥 Carregar ONGs"):
    dados = listar_ongs()
    if dados:
        st.table(dados)
    else:
        st.info("Nenhuma ONG encontrada ou banco indisponível.")

st.divider()

# UPDATE
st.subheader("🛠️ Atualizar dados da ONG")
feedback_update = st.empty()
with st.form("form_update_ong"):
    cnpj_upd = st.text_input("CNPJ da ONG para atualizar")
    nome_upd = st.text_input("Novo Nome")
    cep_upd = st.text_input("Novo CEP")
    contato_upd = st.text_input("Novo Contato")
    email_upd = st.text_input("Novo Email")
    senha_upd = st.text_input("Nova Senha")
    status_verificacao_upd = st.number_input("Novo Status de Verificação", min_value=0, max_value=2, step=1)
    status_conta_upd = st.checkbox("Conta Ativa?")
    descricao_upd = st.text_area("Nova Descrição")
    submit_update = st.form_submit_button("Atualizar")
if submit_update:
    if not cnpj_upd:
        feedback_update.warning("⚠️ O CNPJ é obrigatório para atualizar.")
    else:
        sucesso, mensagem = atualizar_ong(cnpj_upd, nome_upd, cep_upd, contato_upd, email_upd, senha_upd, status_verificacao_upd, status_conta_upd, descricao_upd)
        mensagem = str(mensagem)
        if sucesso:
            feedback_update.success(mensagem)
        else:
            feedback_update.error(mensagem)

st.divider()

# DELETE
st.subheader("🗑️ Deletar ONG")
feedback_delete = st.empty()
with st.form("form_delete_ong"):
    cnpj_delete = st.text_input("CNPJ da ONG para deletar")
    submit_delete = st.form_submit_button("Deletar")
if submit_delete:
    sucesso, mensagem = deletar_ong(cnpj_delete)
    mensagem = str(mensagem)
    if sucesso:
        feedback_delete.success(mensagem)
    else:
        feedback_delete.error(mensagem)
