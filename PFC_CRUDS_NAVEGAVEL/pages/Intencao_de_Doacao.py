import streamlit as st
from psycopg2 import Error
from conexao import criar_conexao
from datetime import date

# ---------------------------
# Funções CRUD
# ---------------------------

def inserir_intencao(id_intencao, id_ong, id_doador, id_lista, status, data_criacao):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        sql = """
        INSERT INTO public."intencaodoacao" 
        ("ID_Intencao", "ID_ONG", "ID_Doador", "ID_Lista", status, data_criacao)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (id_intencao, id_ong, id_doador, id_lista, status, data_criacao)
        cursor.execute(sql, valores)
        conexao.commit()
        return True, "✅ Intenção inserida com sucesso!"
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

def listar_intencoes():
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM public."intencaodoacao" ORDER BY data_criacao DESC')
        registros = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        return [dict(zip(colunas, linha)) for linha in registros]
    except Error as erro:
        st.error(str(erro))
        return []
    finally:
        if conexao:
            cursor.close()
            conexao.close()

def atualizar_intencao(id_intencao, id_ong, id_doador, id_lista, status, data_criacao):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        sql = """
        UPDATE public."intencaodoacao"
        SET "ID_ONG" = %s,
            "ID_Doador" = %s,
            "ID_Lista" = %s,
            status = %s,
            data_criacao = %s
        WHERE "ID_Intencao" = %s
        """
        valores = (id_ong, id_doador, id_lista, status, data_criacao, id_intencao)
        cursor.execute(sql, valores)
        conexao.commit()
        return True, "✅ Intenção atualizada com sucesso!"
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

def atualizar_status(id_intencao, novo_status):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        sql = 'UPDATE public."intencaodoacao" SET status = %s WHERE "ID_Intencao" = %s'
        cursor.execute(sql, (novo_status, id_intencao))
        conexao.commit()
        return True, "✅ Status atualizado com sucesso!"
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

def deletar_intencao(id_intencao):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        cursor.execute('DELETE FROM public."intencaodoacao" WHERE "ID_Intencao" = %s', (id_intencao,))
        conexao.commit()
        if cursor.rowcount:
            return True, "✅ Intenção deletada com sucesso!"
        else:
            return False, "⚠️ Intenção não encontrada."
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

# ---------------------------
# Interface Streamlit
# ---------------------------
st.title("📦 Gerenciar Intenção de Doação")

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
st.subheader("➕ Cadastrar nova intenção")
feedback_create = st.empty()
with st.form("form_inserir"):
    id_intencao = st.text_input("ID Intenção")
    id_ong = st.text_input("ID ONG")
    id_doador = st.text_input("ID Doador")
    id_lista = st.text_input("ID Lista")
    status = st.number_input("Status (0=pendente, 1=aceito, 2=aberto, 3=convertido, 4=cancelado)", min_value=0, max_value=4, step=1)
    data_criacao = st.date_input("Data de Criação", value=date.today())
    submit_create = st.form_submit_button("Inserir")
if submit_create:
    if not id_intencao or not id_ong or not id_doador or not id_lista:
        feedback_create.warning("⚠️ Todos os campos são obrigatórios.")
    else:
        sucesso, mensagem = inserir_intencao(id_intencao, id_ong, id_doador, id_lista, status, data_criacao)
        mensagem = str(mensagem)
        feedback_create.success(mensagem) if sucesso else feedback_create.error(mensagem)

st.divider()

# READ
st.subheader("📋 Listar todas as intenções")
if st.button("📥 Carregar intenções"):
    dados = listar_intencoes()
    if dados:
        st.table(dados)
    else:
        st.info("Nenhuma intenção encontrada.")

st.divider()

# UPDATE - Todos os dados
st.subheader("🛠️ Atualizar todos os dados da intenção (Admin)")
feedback_update_all = st.empty()
with st.form("form_update_all"):
    id_intencao_upd = st.text_input("ID Intenção a atualizar")
    id_ong_upd = st.text_input("Novo ID ONG")
    id_doador_upd = st.text_input("Novo ID Doador")
    id_lista_upd = st.text_input("Novo ID Lista")
    status_upd = st.number_input("Novo Status", min_value=0, max_value=4, step=1)
    data_criacao_upd = st.date_input("Nova Data de Criação", value=date.today())
    submit_update_all = st.form_submit_button("Atualizar todos os dados")
if submit_update_all:
    if not id_intencao_upd or not id_ong_upd or not id_doador_upd or not id_lista_upd:
        feedback_update_all.warning("⚠️ Todos os campos são obrigatórios.")
    else:
        sucesso, mensagem = atualizar_intencao(
            id_intencao_upd,
            id_ong_upd,
            id_doador_upd,
            id_lista_upd,
            status_upd,
            data_criacao_upd
        )
        mensagem = str(mensagem)
        feedback_update_all.success(mensagem) if sucesso else feedback_update_all.error(mensagem)

st.divider()

# UPDATE - Apenas status
st.subheader("✏️ Atualizar status")
feedback_update_status = st.empty()
with st.form("form_update"):
    id_update = st.text_input("ID Intenção para atualizar")
    novo_status = st.number_input("Novo Status", min_value=0, max_value=4, step=1)
    submit_update = st.form_submit_button("Atualizar")
if submit_update:
    sucesso, mensagem = atualizar_status(id_update, novo_status)
    mensagem = str(mensagem)
    feedback_update_status.success(mensagem) if sucesso else feedback_update_status.error(mensagem)

st.divider()

# DELETE
st.subheader("🗑️ Deletar intenção (Admin)")
feedback_delete = st.empty()
with st.form("form_delete"):
    id_delete = st.text_input("ID Intenção para deletar")
    submit_delete = st.form_submit_button("Deletar")
if submit_delete:
    sucesso, mensagem = deletar_intencao(id_delete)
    mensagem = str(mensagem)
    feedback_delete.success(mensagem) if sucesso else feedback_delete.error(mensagem)
