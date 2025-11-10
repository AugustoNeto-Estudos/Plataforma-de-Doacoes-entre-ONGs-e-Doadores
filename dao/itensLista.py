import streamlit as st
from psycopg2 import Error
from dao.conexao import criar_conexao

# ---------------------------
# CREATE - Inserir item na lista
# ---------------------------
def inserir_lista_item(id_lista, id_item, quantidade):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            sql = """
                INSERT INTO public."lista_item" ("ID_Lista", "ID_Item", quantidade_necessaria)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (id_lista, id_item, quantidade))
            conexao.commit()
        return True, "✅ Item adicionado à lista com sucesso!"
    
    except Error as erro:
        return False, f"❌ Erro ao inserir item: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# READ - Exibir itens de uma lista
# ---------------------------
def exibir_lista_itens(id_lista):
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        
        with conexao.cursor() as cursor:
            cursor.execute('SELECT * FROM public."lista_item" WHERE "ID_Lista" = %s', (id_lista,))
            registros = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
            return [dict(zip(colunas, linha)) for linha in registros]
    
    except Error as erro:
        st.error(f"❌ Erro ao exibir itens: {str(erro).strip()[:200]}")
        return []
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# READ - Consultar item específico da lista
# ---------------------------
def consultar_lista_item(id_lista, id_item):
    try:
        conexao = criar_conexao()
        if not conexao:
            return None
        
        with conexao.cursor() as cursor:
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
        st.error(f"❌ Erro ao consultar item: {str(erro).strip()[:200]}")
        return None
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# UPDATE - Atualizar item da lista
# ---------------------------
def atualizar_lista_item(id_lista, id_item, quantidade):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            sql = """
                UPDATE public."lista_item"
                SET quantidade_necessaria = %s
                WHERE "ID_Lista" = %s AND "ID_Item" = %s
            """
            cursor.execute(sql, (quantidade, id_lista, id_item))
            conexao.commit()
            if cursor.rowcount:
                return True, "✅ Item da lista atualizado com sucesso!"
            else:
                return False, "⚠️ Item da lista não encontrado."
    
    except Error as erro:
        return False, f"❌ Erro ao atualizar item: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# DELETE - Remover item da lista
# ---------------------------
def deletar_lista_item(id_lista, id_item):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
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
        return False, f"❌ Erro ao deletar item: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# UPDATE - Atualizar quantidade de item na lista
# ---------------------------
def atualizar_quantidade_item(id_lista, id_item, nova_quantidade):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute("""
                UPDATE public."lista_item"
                SET quantidade_necessaria = %s
                WHERE "ID_Lista" = %s AND "ID_Item" = %s
            """, (nova_quantidade, id_lista, id_item))
            conexao.commit()
            if cursor.rowcount:
                return True, "✅ Quantidade atualizada com sucesso!"
            else:
                return False, "⚠️ Item não encontrado na lista."
    
    except Error as erro:
        return False, f"❌ Erro ao atualizar quantidade: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()
