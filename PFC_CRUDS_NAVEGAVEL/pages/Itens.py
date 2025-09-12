import streamlit as st
from psycopg2 import Error
from conexao import criar_conexao

# ---------------------------
# Funções CRUD - Item
# ---------------------------

def inserir_item(id_item, categoria, subcategoria=None):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO public."item" ("ID_Item", categoria, subcategoria)
            VALUES (%s, %s, %s)
        """, (id_item, categoria, subcategoria))
        conexao.commit()
        return True, "✅ Item inserido com sucesso!"
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

def exibir_itens():
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM public."item" ORDER BY "ID_Item" ASC')
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

def consultar_item_id(id_item):
    try:
        conexao = criar_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM public."item" WHERE "ID_Item" = %s', (id_item,))
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

def atualizar_item(id_item, categoria=None, subcategoria=None):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        atualizacoes, valores = [], []
        if categoria:
            atualizacoes.append('categoria = %s')
            valores.append(categoria)
        if subcategoria:
            atualizacoes.append('subcategoria = %s')
            valores.append(subcategoria)
        if not atualizacoes:
            return False, "⚠️ Nenhum campo para atualizar."
        sql = f'UPDATE public."item" SET {", ".join(atualizacoes)} WHERE "ID_Item" = %s'
        valores.append(id_item)
        cursor.execute(sql, valores)
        conexao.commit()
        if cursor.rowcount:
            return True, "✅ Item atualizado com sucesso!"
        else:
            return False, "⚠️ Item não encontrado."
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

def deletar_item(id_item):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        cursor = conexao.cursor()
        cursor.execute('DELETE FROM public."item" WHERE "ID_Item" = %s', (id_item,))
        conexao.commit()
        if cursor.rowcount:
            return True, "✅ Item deletado com sucesso!"
        else:
            return False, "⚠️ Item não encontrado."
    except Error as erro:
        return False, str(erro)
    finally:
        if conexao:
            cursor.close()
            conexao.close()

# ---------------------------
# Interface Streamlit
# ---------------------------
st.title("📦 Gerenciar Itens")

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
st.subheader("➕ Inserir novo item")
feedback_create = st.empty()
with st.form("form_inserir_item"):
    id_item = st.text_input("ID do Item")
    categoria = st.text_input("Categoria")
    subcategoria = st.text_input("Subcategoria (opcional)")
    submit_create = st.form_submit_button("Inserir")
if submit_create:
    if not id_item or not categoria:
        feedback_create.warning("⚠️ ID e Categoria são obrigatórios.")
    else:
        sucesso, msg = inserir_item(id_item, categoria, subcategoria if subcategoria else None)
        msg = str(msg)  # garante que seja string
        if sucesso:
            feedback_create.success(msg)
        else:
            feedback_create.error(msg)

st.divider()

# READ
st.subheader("📋 Listar itens")
if st.button("📥 Carregar itens"):
    dados = exibir_itens()
    if dados:
        st.table(dados)
    else:
        st.info("Nenhum item encontrado.")

st.divider()

# CONSULTAR
st.subheader("🔍 Consultar item por ID")
feedback_consulta = st.empty()
with st.form("form_consultar_item"):
    id_item_consulta = st.text_input("ID do Item")
    submit_consulta = st.form_submit_button("Consultar")
if submit_consulta:
    item = consultar_item_id(id_item_consulta)
    if item:
        feedback_consulta.json(item)
    else:
        feedback_consulta.warning("Item não encontrado.")

st.divider()

# UPDATE
st.subheader("✏️ Atualizar item")
feedback_update = st.empty()
with st.form("form_update_item"):
    id_item_upd = st.text_input("ID do Item")
    categoria_upd = st.text_input("Nova Categoria")
    subcategoria_upd = st.text_input("Nova Subcategoria")
    submit_update = st.form_submit_button("Atualizar")
if submit_update:
    sucesso, msg = atualizar_item(
        id_item_upd,
        categoria_upd if categoria_upd else None,
        subcategoria_upd if subcategoria_upd else None
    )
    msg = str(msg)
    if sucesso:
        feedback_update.success(msg)
    else:
        feedback_update.error(msg)

st.divider()

# DELETE
st.subheader("🗑️ Deletar item")
feedback_delete = st.empty()
with st.form("form_delete_item"):
    id_item_del = st.text_input("ID do Item")
    submit_delete = st.form_submit_button("Deletar")
if submit_delete:
    sucesso, msg = deletar_item(id_item_del)
    msg = str(msg)
    if sucesso:
        feedback_delete.success(msg)
    else:
        feedback_delete.error(msg)
