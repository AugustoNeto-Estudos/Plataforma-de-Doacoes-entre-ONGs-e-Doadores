import streamlit as st
from psycopg2 import Error
from conexao import criar_conexao
from datetime import date

# ---------------------------
# Funções CRUD
# ---------------------------

def inserir_pedido(id_pedido, id_ong, id_doador, id_intencao, status, data_criacao):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        sql = """
        INSERT INTO public."pedido" 
        ("ID_Pedido", "ID_ONG", "ID_Doador", "ID_Intencao", status, data_criacao)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (id_pedido, id_ong, id_doador, id_intencao, status, data_criacao)
        cursor.execute(sql, valores)
        conexao.commit()
        return True, "✅ Pedido inserido com sucesso!"
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

def listar_pedidos():
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM public."pedido" ORDER BY data_criacao DESC')
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

def atualizar_status_pedido(id_pedido, novo_status):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        sql = 'UPDATE public."pedido" SET status = %s WHERE "ID_Pedido" = %s'
        cursor.execute(sql, (novo_status, id_pedido))
        conexao.commit()
        return True, "✅ Status do pedido atualizado com sucesso!"
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

def atualizar_pedido(id_pedido, id_ong, id_doador, id_intencao, status, data_criacao):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        sql = """
        UPDATE public."pedido"
        SET "ID_ONG" = %s,
            "ID_Doador" = %s,
            "ID_Intencao" = %s,
            status = %s,
            data_criacao = %s
        WHERE "ID_Pedido" = %s
        """
        valores = (id_ong, id_doador, id_intencao, status, data_criacao, id_pedido)
        cursor.execute(sql, valores)
        conexao.commit()
        return True, "✅ Pedido atualizado com sucesso!"
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

def deletar_pedido(id_pedido):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        cursor.execute('DELETE FROM public."pedido" WHERE "ID_Pedido" = %s', (id_pedido,))
        conexao.commit()
        if cursor.rowcount:
            return True, "✅ Pedido deletado com sucesso!"
        else:
            return False, "⚠️ Pedido não encontrado."
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

# ---------------------------
# Interface Streamlit
# ---------------------------
st.title("📦 CRUD - Pedido")

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
st.subheader("➕ Cadastrar novo pedido")
feedback_create = st.empty()
with st.form("form_inserir_pedido"):
    id_pedido = st.text_input("ID Pedido")
    id_ong = st.text_input("ID ONG")
    id_doador = st.text_input("ID Doador")
    id_intencao = st.text_input("ID Intenção")
    status = st.number_input("Status (0=pendente, 1=concluído, 2=cancelado)", min_value=0, max_value=2, step=1)
    data_criacao = st.date_input("Data de Criação", value=date.today())
    submit_create = st.form_submit_button("Inserir")
if submit_create:
    if not id_pedido or not id_ong or not id_doador or not id_intencao:
        feedback_create.warning("⚠️ Todos os campos são obrigatórios.")
    else:
        sucesso, mensagem = inserir_pedido(id_pedido, id_ong, id_doador, id_intencao, status, data_criacao)
        mensagem = str(mensagem)
        feedback_create.success(mensagem) if sucesso else feedback_create.error(mensagem)

st.divider()

# READ
st.subheader("📋 Lista de pedidos")
feedback_read = st.empty()
if st.button("📥 Carregar pedidos"):
    dados = listar_pedidos()
    if dados:
        feedback_read.success(f"✅ {len(dados)} pedidos encontrados.")
        st.table(dados)
    else:
        feedback_read.info("Nenhum pedido encontrado ou banco indisponível.")

st.divider()

# UPDATE - status
st.subheader("✏️ Atualizar status do pedido")
feedback_update_status = st.empty()
with st.form("form_update_status_pedido"):
    id_update = st.text_input("ID Pedido para atualizar status")
    novo_status = st.number_input("Novo Status", min_value=0, max_value=2, step=1)
    submit_update = st.form_submit_button("Atualizar Status")
if submit_update:
    sucesso, mensagem = atualizar_status_pedido(id_update, novo_status)
    mensagem = str(mensagem)
    feedback_update_status.success(mensagem) if sucesso else feedback_update_status.error(mensagem)

st.divider()

# UPDATE - todos os campos
st.subheader("🛠️ Atualizar todos os dados do pedido (Admin)")
feedback_update_all = st.empty()
with st.form("form_update_all_pedido"):
    id_pedido_upd = st.text_input("ID Pedido a atualizar")
    id_ong_upd = st.text_input("Novo ID ONG")
    id_doador_upd = st.text_input("Novo ID Doador")
    id_intencao_upd = st.text_input("Novo ID Intenção")
    status_upd = st.number_input("Novo Status", min_value=0, max_value=2, step=1)
    data_criacao_upd = st.date_input("Nova Data de Criação", value=date.today())
    submit_update_all = st.form_submit_button("Atualizar todos os dados")
if submit_update_all:
    if not id_pedido_upd or not id_ong_upd or not id_doador_upd or not id_intencao_upd:
        feedback_update_all.warning("⚠️ Todos os campos são obrigatórios.")
    else:
        sucesso, mensagem = atualizar_pedido(
            id_pedido_upd,
            id_ong_upd,
            id_doador_upd,
            id_intencao_upd,
            status_upd,
            data_criacao_upd
        )
        mensagem = str(mensagem)
        feedback_update_all.success(mensagem) if sucesso else feedback_update_all.error(mensagem)

st.divider()

# DELETE
st.subheader("🗑️ Deletar pedido")
feedback_delete = st.empty()
with st.form("form_delete_pedido"):
    id_delete = st.text_input("ID Pedido para deletar")
    submit_delete = st.form_submit_button("Deletar")
if submit_delete:
    sucesso, mensagem = deletar_pedido(id_delete)
    mensagem = str(mensagem)
    feedback_delete.success(mensagem) if sucesso else feedback_delete.error(mensagem)
