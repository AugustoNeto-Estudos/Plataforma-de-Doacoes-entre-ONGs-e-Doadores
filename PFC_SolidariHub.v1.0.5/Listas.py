import streamlit as st
from psycopg2 import Error
from conexao import criar_conexao

# ---------------------------
# Funções CRUD - Lista
# ---------------------------

def inserir_lista(id_lista, titulo, id_ong, status, descricao):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, str("❌ Falha ao conectar ao banco.")
        cursor = conexao.cursor()
        sql = """
        INSERT INTO public."lista" 
        ("ID_Lista", titulo, "ID_ONG", data_criacao, status, descricao)
        VALUES (%s, %s, %s, CURRENT_DATE, %s, %s)
        """
        valores = (id_lista, titulo, id_ong, status, descricao)
        cursor.execute(sql, valores)
        conexao.commit()
        return True, str("✅ Lista inserida com sucesso!")
    except Error as erro:
        return False, str(f"❌ Erro ao inserir lista: {str(erro).strip()[:200]}")
    finally:
        try:
            cursor.close()
            conexao.close()
        except:
            pass

def exibir_listas():
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM public."lista" ORDER BY "ID_Lista" ASC')
        registros = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        return [dict(zip(colunas, linha)) for linha in registros]
    except Error as erro:
        st.error(str(f"❌ Erro ao exibir listas: {str(erro).strip()[:200]}"))
        return []
    finally:
        try:
            cursor.close()
            conexao.close()
        except:
            pass

def consultar_lista_id(id_lista):
    try:
        conexao = criar_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM public."lista" WHERE "ID_Lista" = %s', (id_lista,))
        registro = cursor.fetchone()
        if registro:
            colunas = [desc[0] for desc in cursor.description]
            return dict(zip(colunas, registro))
        return None
    except Error as erro:
        st.error(str(f"❌ Erro ao consultar lista: {str(erro).strip()[:200]}"))
        return None
    finally:
        try:
            cursor.close()
            conexao.close()
        except:
            pass

def atualizar_lista(id_lista, titulo=None, id_ong=None, status=None, descricao=None):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, str("❌ Falha ao conectar ao banco.")
        cursor = conexao.cursor()
        atualizacoes, valores = [], []
        if titulo:
            atualizacoes.append('titulo = %s')
            valores.append(titulo)
        if id_ong:
            atualizacoes.append('"ID_ONG" = %s')
            valores.append(id_ong)
        if status is not None:
            atualizacoes.append('status = %s')
            valores.append(status)
        if descricao:
            atualizacoes.append('descricao = %s')
            valores.append(descricao)
        if not atualizacoes:
            return False, str("⚠️ Nenhum campo para atualizar.")
        sql = f'UPDATE public."lista" SET {", ".join(atualizacoes)} WHERE "ID_Lista" = %s'
        valores.append(id_lista)
        cursor.execute(sql, valores)
        conexao.commit()
        if cursor.rowcount:
            return True, str("✅ Lista atualizada com sucesso!")
        else:
            return False, str("⚠️ Lista não encontrada.")
    except Error as erro:
        return False, str(f"❌ Erro ao atualizar lista: {str(erro).strip()[:200]}")
    finally:
        try:
            cursor.close()
            conexao.close()
        except:
            pass

def deletar_lista(id_lista):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, str("❌ Falha ao conectar ao banco.")
        cursor = conexao.cursor()
        cursor.execute('DELETE FROM public."lista" WHERE "ID_Lista" = %s', (id_lista,))
        conexao.commit()
        if cursor.rowcount:
            return True, str("✅ Lista deletada com sucesso!")
        else:
            return False, str("⚠️ Lista não encontrada.")
    except Error as erro:
        return False, str(f"❌ Erro ao deletar lista: {str(erro).strip()[:200]}")
    finally:
        try:
            cursor.close()
            conexao.close()
        except:
            pass

# ---------------------------
# Interface Streamlit
# ---------------------------
st.title("🗂️ Gerenciar Listas")

# Testar conexão
if st.button("🔌 Testar Conexão"):
    conexao = criar_conexao()
    if conexao:
        st.success(str("✅ Conexão estabelecida com sucesso!"))
        conexao.close()
    else:
        st.error(str("❌ Erro ao conectar ao PostgreSQL."))

st.divider()

# CREATE
st.subheader("➕ Inserir nova lista")
feedback_create = st.empty()
with st.form("form_inserir_lista"):
    id_lista = st.text_input("ID da Lista")
    titulo = st.text_input("Título da Lista")
    id_ong = st.text_input("ID da ONG")
    status = st.checkbox("Lista Ativa?")
    descricao = st.text_area("Descrição")
    submit_create = st.form_submit_button("Inserir")
if submit_create:
    if not id_lista or not titulo or not id_ong:
        feedback_create.warning(str("⚠️ Campos obrigatórios: ID da Lista, Título e ID da ONG."))
    else:
        sucesso, mensagem = inserir_lista(id_lista, titulo, id_ong, status, descricao)
        mensagem = str(mensagem)
        feedback_create.success(mensagem) if sucesso else feedback_create.error(mensagem)

st.divider()

# READ
st.subheader("📋 Listar todas as listas")
if st.button("📥 Carregar listas"):
    dados = exibir_listas()
    if dados:
        st.table(dados)
    else:
        st.info(str("Nenhuma lista encontrada."))

st.divider()

# CONSULTAR
st.subheader("🔍 Consultar lista por ID")
feedback_consulta = st.empty()
with st.form("form_consultar_lista"):
    id_lista_consulta = st.text_input("ID da Lista")
    submit_consulta = st.form_submit_button("Consultar")
if submit_consulta:
    lista = consultar_lista_id(id_lista_consulta)
    if lista:
        feedback_consulta.success(str("✅ Lista encontrada!"))
        st.json(lista)
    else:
        feedback_consulta.warning(str("Lista não encontrada."))

st.divider()

# UPDATE
st.subheader("✏️ Atualizar lista")
feedback_update = st.empty()
with st.form("form_update_lista"):
    id_lista_upd = st.text_input("ID da Lista")
    titulo_upd = st.text_input("Novo Título")
    id_ong_upd = st.text_input("Novo ID da ONG")
    status_upd = st.checkbox("Lista Ativa?")
    descricao_upd = st.text_area("Nova Descrição")
    submit_update = st.form_submit_button("Atualizar")
if submit_update:
    sucesso, mensagem = atualizar_lista(id_lista_upd, titulo_upd, id_ong_upd, status_upd, descricao_upd)
    mensagem = str(mensagem)
    feedback_update.success(mensagem) if sucesso else feedback_update.error(mensagem)

st.divider()

# DELETE
st.subheader("🗑️ Deletar lista")
feedback_delete = st.empty()
with st.form("form_delete_lista"):
    id_lista_del = st.text_input("ID da Lista")
    submit_delete = st.form_submit_button("Deletar")
if submit_delete:
    sucesso, mensagem = deletar_lista(id_lista_del)
    mensagem = str(mensagem)
    feedback_delete.success(mensagem) if sucesso else feedback_delete.error(mensagem)
