from psycopg2 import Error
from dao.conexao import criar_conexao

# CREATE - Inserir nova lista
def inserir_lista(id_lista, titulo, id_ong, status, descricao):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            sql = """
                INSERT INTO public."lista" 
                ("ID_Lista", titulo, "ID_ONG", data_criacao, status, descricao)
                VALUES (%s, %s, %s, CURRENT_DATE, %s, %s)
            """
            valores = (id_lista, titulo, id_ong, status, descricao)
            cursor.execute(sql, valores)
            conexao.commit()
        return True, "Lista inserida com sucesso."
    
    except Error as erro:
        return False, f"Erro ao inserir lista: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# READ - Exibir todas as listas
def exibir_listas():
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        
        with conexao.cursor() as cursor:
            cursor.execute('SELECT * FROM public."lista" ORDER BY "ID_Lista" ASC')
            registros = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
            return [dict(zip(colunas, linha)) for linha in registros]
    
    except Error as erro:
        return f"Erro ao exibir listas: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# READ - Consultar lista por ID
def consultar_lista_id(id_lista):
    try:
        conexao = criar_conexao()
        if not conexao:
            return None
        
        with conexao.cursor() as cursor:
            cursor.execute('SELECT * FROM public."lista" WHERE "ID_Lista" = %s', (id_lista,))
            registro = cursor.fetchone()
            if registro:
                colunas = [desc[0] for desc in cursor.description]
                return dict(zip(colunas, registro))
            return None
    
    except Error as erro:
        return f"Erro ao consultar lista: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# READ - Exibir listas de uma ONG específica
def exibir_listas_por_ong(id_ong):
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        
        with conexao.cursor() as cursor:
            cursor.execute('SELECT * FROM public."lista" WHERE "ID_ONG" = %s ORDER BY "ID_Lista" ASC', (id_ong,))
            registros = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
            return [dict(zip(colunas, linha)) for linha in registros]
    
    except Error as erro:
        return f"Erro ao exibir listas da ONG: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# UPDATE - Atualizar campos da lista
def atualizar_lista(id_lista, titulo=None, id_ong=None, status=None, descricao=None):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."
        
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
            return False, "Nenhum campo para atualizar."
        
        with conexao.cursor() as cursor:
            sql = f'UPDATE public."lista" SET {", ".join(atualizacoes)} WHERE "ID_Lista" = %s'
            valores.append(id_lista)
            cursor.execute(sql, valores)
            conexao.commit()
            if cursor.rowcount:
                return True, "Lista atualizada com sucesso."
            else:
                return False, "Lista não encontrada."
    
    except Error as erro:
        return False, f"Erro ao atualizar lista: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# DELETE - Excluir lista
def deletar_lista(id_lista):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute('DELETE FROM public."lista" WHERE "ID_Lista" = %s', (id_lista,))
            conexao.commit()
            if cursor.rowcount:
                return True, "Lista deletada com sucesso."
            else:
                return False, "Lista não encontrada."
    
    except Error as erro:
        return False, f"Erro ao deletar lista: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# UPDATE - Atualizar status da lista
def atualizar_status_lista(id_lista, novo_status):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute(
                'UPDATE public."lista" SET status = %s WHERE "ID_Lista" = %s',
                (novo_status, id_lista)
            )
            conexao.commit()
            if cursor.rowcount:
                return True, "Status da lista atualizado com sucesso."
            else:
                return False, "Lista não encontrada."
    
    except Error as erro:
        return False, f"Erro ao atualizar status: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# UPDATE - Atualizar descrição da lista
def atualizar_descricao_lista(id_lista, nova_descricao):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute(
                'UPDATE public."lista" SET descricao = %s WHERE "ID_Lista" = %s',
                (nova_descricao, id_lista)
            )
            conexao.commit()
            if cursor.rowcount:
                return True, "Descrição da lista atualizada com sucesso."
            else:
                return False, "Lista não encontrada."
    
    except Error as erro:
        return False, f"Erro ao atualizar descrição: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()
