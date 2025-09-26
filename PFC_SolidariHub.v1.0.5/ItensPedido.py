import streamlit as st
from psycopg2 import Error
from conexao import criar_conexao

# ---------------------------
# Funções CRUD - Pedido_Item
# ---------------------------

def inserir_pedido_item(id_pedido, id_item, quantidade, observacao=None):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, str("❌ Falha ao conectar ao banco.")
        cursor = conexao.cursor()
        sql = """
        INSERT INTO public."pedido_item" ("ID_Pedido", "ID_Item", quantidade, observacao)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (id_pedido, id_item, quantidade, observacao))
        conexao.commit()
        return True, str("✅ Item adicionado ao pedido com sucesso!")
    except Error as erro:
        return False, str(f"❌ Erro ao inserir item: {str(erro).strip()[:200]}")
    finally:
        try:
            cursor.close()
            conexao.close()
        except:
            pass

def exibir_pedidos_itens(id_pedido):
    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM public."pedido_item" WHERE "ID_Pedido" = %s', (id_pedido,))
        registros = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        return [dict(zip(colunas, linha)) for linha in registros]
    except Error as erro:
        st.error(str(f"❌ Erro ao exibir itens: {str(erro).strip()[:200]}"))
        return []
    finally:
        try:
            cursor.close()
            conexao.close()
        except:
            pass

def consultar_pedido_item(id_pedido, id_item):
    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()
        cursor.execute(
            'SELECT * FROM public."pedido_item" WHERE "ID_Pedido" = %s AND "ID_Item" = %s',
            (id_pedido, id_item)
        )
        registro = cursor.fetchone()
        if registro:
            colunas = [desc[0] for desc in cursor.description]
            return dict(zip(colunas, registro))
        return None
    except Error as erro:
        st.error(str(f"❌ Erro ao consultar item: {str(erro).strip()[:200]}"))
        return None
    finally:
        try:
            cursor.close()
            conexao.close()
        except:
            pass

def atualizar_pedido_item(id_pedido, id_item, quantidade=None, observacao=None):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, str("❌ Falha ao conectar ao banco.")
        cursor = conexao.cursor()
        atualizacoes, valores = [], []
        if quantidade is not None:
            atualizacoes.append('quantidade = %s')
            valores.append(quantidade)
        if observacao is not None:
            atualizacoes.append('observacao = %s')
            valores.append(observacao)
        if not atualizacoes:
            return False, str("⚠️ Nenhum campo para atualizar.")
        sql = f'UPDATE public."pedido_item" SET {", ".join(atualizacoes)} WHERE "ID_Pedido" = %s AND "ID_Item" = %s'
        valores.extend([id_pedido, id_item])
        cursor.execute(sql, valores)
        conexao.commit()
        if cursor.rowcount:
            return True, str("✅ Item do pedido atualizado com sucesso!")
        else:
            return False, str("⚠️ Item não encontrado.")
    except Error as erro:
        return False, str(f"❌ Erro ao atualizar item: {str(erro).strip()[:200]}")
    finally:
        try:
            cursor.close()
            conexao.close()
        except:
            pass

def deletar_pedido_item(id_pedido, id_item):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, str("❌ Falha ao conectar ao banco.")
        cursor = conexao.cursor()
        cursor.execute(
            'DELETE FROM public."pedido_item" WHERE "ID_Pedido" = %s AND "ID_Item" = %s',
            (id_pedido, id_item)
        )
        conexao.commit()
        if cursor.rowcount:
            return True, str("✅ Item removido do pedido com sucesso!")
        else:
            return False, str("⚠️ Item não encontrado.")
    except Error as erro:
        return False, str(f"❌ Erro ao deletar item: {str(erro).strip()[:200]}")
    finally:
        try:
            cursor.close()
            conexao.close()
        except:
            pass

# ---------------------------
# Interface Streamlit
# ---------------------------
st.title("📦 Gerenciar Pedido de Itens")

# CREATE
st.subheader("➕ Adicionar item ao pedido")
feedback_create = st.empty()
with st.form("form_inserir_pedido_item"):
    id_pedido = st.text_input("ID do Pedido")
    id_item = st.text_input("ID do Item")
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    observacao = st.text_area("Observação (opcional)")
    submit_create = st.form_submit_button("Inserir")
if submit_create:
    if not id_pedido or not id_item:
        feedback_create.warning(str("⚠️ ID do pedido e ID do item são obrigatórios."))
    else:
        sucesso, mensagem = inserir_pedido_item(id_pedido, id_item, quantidade, observacao)
        mensagem = str(mensagem)
        feedback_create.success(mensagem) if sucesso else feedback_create.error(mensagem)

st.divider()

# READ
st.subheader("📋 Exibir itens de um pedido")
feedback_read = st.empty()
id_pedido_exibir = st.text_input("ID do Pedido para exibir itens")
if st.button("📥 Carregar itens"):
    dados = exibir_pedidos_itens(id_pedido_exibir)
    if dados:
        feedback_read.success(str(f"✅ {len(dados)} itens encontrados."))
        st.table(dados)
    else:
        feedback_read.info(str("Nenhum item encontrado para este pedido."))

st.divider()

# UPDATE
st.subheader("✏️ Atualizar item do pedido")
feedback_update = st.empty()
with st.form("form_update_pedido_item"):
    id_pedido_upd = st.text_input("ID do Pedido")
    id_item_upd = st.text_input("ID do Item")
    qtd_upd = st.number_input("Nova Quantidade", min_value=1, step=1)
    obs_upd = st.text_area("Nova Observação (opcional)")
    submit_update = st.form_submit_button("Atualizar")
if submit_update:
    sucesso, mensagem = atualizar_pedido_item(id_pedido_upd, id_item_upd, qtd_upd, obs_upd if obs_upd else None)
    mensagem = str(mensagem)
    feedback_update.success(mensagem) if sucesso else feedback_update.error(mensagem)

st.divider()

# DELETE
st.subheader("🗑️ Deletar item do pedido")
feedback_delete = st.empty()
with st.form("form_delete_pedido_item"):
    id_pedido_del = st.text_input("ID do Pedido")
    id_item_del = st.text_input("ID do Item")
    submit_delete = st.form_submit_button("Deletar")
if submit_delete:
    sucesso, mensagem = deletar_pedido_item(id_pedido_del, id_item_del)
    mensagem = str(mensagem)
    feedback_delete.success(mensagem) if sucesso else feedback_delete.error(mensagem)
