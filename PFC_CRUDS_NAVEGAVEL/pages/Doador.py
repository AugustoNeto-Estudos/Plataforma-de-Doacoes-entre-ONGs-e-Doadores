import streamlit as st
from psycopg2 import Error
from conexao import criar_conexao

# ---------------------------
# CREATE - Doador
# ---------------------------
def cadastrar_doador(cpf, nome, email, contato, senha, status_conta):
    conexao = None
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        sql = """
        INSERT INTO public."doador" 
        ("CPF_ID", nome, email, contato, senha, status_conta) 
        VALUES (%s,%s,%s,%s,%s,%s)
        """
        valores = (cpf, nome, email, contato, senha, status_conta)
        cursor.execute(sql, valores)
        conexao.commit()
        return True, "✅ Doador cadastrado com sucesso!"
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

# ---------------------------
# READ - Doadores
# ---------------------------
def listar_doadores():
    conexao = None
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM public."doador"')
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
def atualizar_doador(cpf, nome, email, contato, senha, status_conta):
    conexao = None
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        sql = """
        UPDATE public."doador"
        SET nome=%s, email=%s, contato=%s, senha=%s, status_conta=%s
        WHERE "CPF_ID" = %s
        """
        valores = (nome, email, contato, senha, status_conta, cpf)
        cursor.execute(sql, valores)
        conexao.commit()
        return True, "✅ Doador atualizado com sucesso!"
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

# ---------------------------
# DELETE
# ---------------------------
def deletar_doador(cpf):
    conexao = None
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        cursor.execute('DELETE FROM public."doador" WHERE "CPF_ID" = %s', (cpf,))
        conexao.commit()
        if cursor.rowcount:
            return True, "✅ Doador deletado com sucesso!"
        else:
            return False, "⚠️ Doador não encontrado."
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

# ---------------------------
# Interface Streamlit
# ---------------------------
st.title("👤 Gerenciar Doadores")

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
st.subheader("➕ Cadastrar novo doador")
feedback_create = st.empty()
with st.form("form_inserir_doador"):
    cpf = st.text_input("CPF")
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    contato = st.text_input("Contato")
    senha = st.text_input("Senha", type="password")
    status_conta = st.checkbox("Conta Ativa?")
    submit_create = st.form_submit_button("Cadastrar")
if submit_create:
    if not cpf or not nome or not email or not senha:
        feedback_create.warning("⚠️ Campos obrigatórios: CPF, Nome, Email e Senha.")
    else:
        sucesso, mensagem = cadastrar_doador(cpf, nome, email, contato, senha, status_conta)
        mensagem = str(mensagem)
        if sucesso:
            feedback_create.success(mensagem)
        else:
            feedback_create.error(mensagem)

st.divider()

# READ
st.subheader("📋 Lista de doadores")
if st.button("📥 Carregar doadores"):
    dados = listar_doadores()
    if dados:
        st.table(dados)
    else:
        st.info("Nenhum doador encontrado ou banco indisponível.")

st.divider()

# UPDATE
st.subheader("🛠️ Atualizar dados do doador")
feedback_update = st.empty()
with st.form("form_update_doador"):
    cpf_upd = st.text_input("CPF do doador para atualizar")
    nome_upd = st.text_input("Novo Nome")
    email_upd = st.text_input("Novo Email")
    contato_upd = st.text_input("Novo Contato")
    senha_upd = st.text_input("Nova Senha")
    status_conta_upd = st.checkbox("Conta Ativa?")
    submit_update = st.form_submit_button("Atualizar")
if submit_update:
    if not cpf_upd:
        feedback_update.warning("⚠️ O CPF é obrigatório para atualizar.")
    else:
        sucesso, mensagem = atualizar_doador(cpf_upd, nome_upd, email_upd, contato_upd, senha_upd, status_conta_upd)
        mensagem = str(mensagem)
        if sucesso:
            feedback_update.success(mensagem)
        else:
            feedback_update.error(mensagem)

st.divider()

# DELETE
st.subheader("🗑️ Deletar doador")
feedback_delete = st.empty()
with st.form("form_delete_doador"):
    cpf_delete = st.text_input("CPF do doador para deletar")
    submit_delete = st.form_submit_button("Deletar")
if submit_delete:
    sucesso, mensagem = deletar_doador(cpf_delete)
    mensagem = str(mensagem)
    if sucesso:
        feedback_delete.success(mensagem)
    else:
        feedback_delete.error(mensagem)
