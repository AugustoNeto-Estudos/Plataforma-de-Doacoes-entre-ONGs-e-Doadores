import streamlit as st
from psycopg2 import Error
from conexao import criar_conexao

# ---------------------------
# Funções CRUD - Lista_Item
# ---------------------------

def inserir_lista_item(id_lista, id_item, quantidade):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        sql = """
        INSERT INTO public."lista_item" ("ID_Lista", "ID_Item", quantidade_necessaria)
        VALUES (%s, %s, %s)
        """
        valores = (id_lista, id_item, quantidade)
        cursor.execute(sql, valores)
        conexao.commit()
        return True, "✅ Item adicionado à lista com sucesso!"
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

def exibir_lista_itens(id_lista):
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM public."lista_item" WHERE "ID_Lista" = %s', (id_lista,))
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

def consultar_lista_item(id_lista, id_item):
    try:
        conexao = criar_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        cursor.execute(
            'SELECT * FROM public."lista_item" WHERE "ID_Lista" = %s AND "ID_Item" = %s',
            (id_lista, id_item)
        )
        registro = cursor.fetchone()
        if registro:
            colunas = [desc[0] for desc in cursor.description]
            return dict(zip(colunas, registro))
        return None
    except Error as erro:
        st.error(str(erro))
        return None
    finally:
        if conexao:
            cursor.close()
            conexao.close()

def atualizar_lista_item(id_lista, id_item, quantidade):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        sql = 'UPDATE public."lista_item" SET quantidade_necessaria = %s WHERE "ID_Lista" = %s AND "ID_Item" = %s'
        valores = (quantidade, id_lista, id_item)
        cursor.execute(sql, valores)
        conexao.commit()
        if cursor.rowcount:
            return True, "✅ Item da lista atualizado com sucesso!"
        else:
            return False, "⚠️ Item da lista não encontrado."
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

def deletar_lista_item(id_lista, id_item):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        cursor.execute(
            'DELETE FROM public."lista_item" WHERE "ID_Lista" = %s AND "ID_Item" = %s',
            (id_lista, id_item)
        )
        conexao.commit()
        if cursor.rowcount:
            return True, "✅ Item removido da lista com sucesso!"
        else:
            return False, "⚠️ Item da lista não encontrado."
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

# ---------------------------
# Interface Streamlit
# ---------------------------
st.title("📝 CRUD - Lista de Itens")

# CREATE
st.subheader("➕ Adicionar item à lista")
feedback_create = st.empty()
with st.form("form_inserir_lista_item"):
    id_lista = st.text_input("ID da Lista")
    id_item = st.text_input("ID do Item")
    quantidade = st.number_input("Quantidade Necessária", min_value=1, step=1)
    submit_create = st.form_submit_button("Inserir")
if submit_create:
    if not id_lista or not id_item:
        feedback_create.warning("⚠️ ID da lista e ID do item são obrigatórios.")
    else:
        sucesso, mensagem = inserir_lista_item(id_lista, id_item, quantidade)
        mensagem = str(mensagem)
        feedback_create.success(mensagem) if sucesso else feedback_create.error(mensagem)

st.divider()

# READ - listar itens de uma lista
st.subheader("📋 Exibir itens de uma lista")
feedback_read = st.empty()
id_lista_exibir = st.text_input("ID da Lista para exibir itens")
if st.button("📥 Carregar itens"):
    dados = exibir_lista_itens(id_lista_exibir)
    if dados:
        feedback_read.success(f"✅ {len(dados)} itens encontrados.")
        st.table(dados)
    else:
        feedback_read.info("Nenhum item encontrado para esta lista.")

st.divider()

# UPDATE
st.subheader("✏️ Atualizar item da lista")
feedback_update = st.empty()
with st.form("form_update_lista_item"):
    id_lista_upd = st.text_input("ID da Lista")
    id_item_upd = st.text_input("ID do Item")
    qtd_upd = st.number_input("Nova Quantidade", min_value=1, step=1)
    submit_update = st.form_submit_button("Atualizar")
if submit_update:
    sucesso, mensagem = atualizar_lista_item(id_lista_upd, id_item_upd, qtd_upd)
    mensagem = str(mensagem)
    feedback_update.success(mensagem) if sucesso else feedback_update.error(mensagem)

st.divider()

# DELETE
st.subheader("🗑️ Deletar item da lista")
feedback_delete = st.empty()
with st.form("form_delete_lista_item"):
    id_lista_del = st.text_input("ID da Lista")
    id_item_del = st.text_input("ID do Item")
    submit_delete = st.form_submit_button("Deletar")
if submit_delete:
    sucesso, mensagem = deletar_lista_item(id_lista_del, id_item_del)
    mensagem = str(mensagem)
    feedback_delete.success(mensagem) if sucesso else feedback_delete.error(mensagem)
