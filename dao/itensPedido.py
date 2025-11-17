from psycopg2 import Error
from dao.conexao import criar_conexao

# CREATE - Inserir item no pedido
def inserir_pedido_item(id_pedido, id_item, quantidade, observacao=None):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            sql = """
                INSERT INTO public."pedido_item" ("ID_Pedido", "ID_Item", quantidade, observacao)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (id_pedido, id_item, quantidade, observacao))
            conexao.commit()
        return True, "Item adicionado ao pedido com sucesso."
    
    except Error as erro:
        return False, f"Erro ao inserir item: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# READ - Exibir itens de um pedido
def exibir_pedidos_itens(id_pedido):
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        
        with conexao.cursor() as cursor:
            cursor.execute('SELECT * FROM public."pedido_item" WHERE "ID_Pedido" = %s', (id_pedido,))
            registros = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
            return [dict(zip(colunas, linha)) for linha in registros]
    
    except Error as erro:
        return False,f"Erro ao exibir itens: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# READ - Consultar item específico do pedido
def consultar_pedido_item(id_pedido, id_item):
    try:
        conexao = criar_conexao()
        if not conexao:
            return None
        
        with conexao.cursor() as cursor:
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
        return False,f"Erro ao consultar item: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# UPDATE - Atualizar item do pedido
def atualizar_pedido_item(id_pedido, id_item, quantidade=None, observacao=None):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."
        
        atualizacoes, valores = [], []
        if quantidade is not None:
            atualizacoes.append('quantidade = %s')
            valores.append(quantidade)
        if observacao is not None:
            atualizacoes.append('observacao = %s')
            valores.append(observacao)
        if not atualizacoes:
            return False, "Nenhum campo para atualizar."
        
        with conexao.cursor() as cursor:
            sql = f"""
                UPDATE public."pedido_item"
                SET {", ".join(atualizacoes)}
                WHERE "ID_Pedido" = %s AND "ID_Item" = %s
            """
            valores.extend([id_pedido, id_item])
            cursor.execute(sql, valores)
            conexao.commit()
            if cursor.rowcount:
                return True, "Item do pedido atualizado com sucesso."
            else:
                return False, "Item não encontrado."
    
    except Error as erro:
        return False, f"Erro ao atualizar item: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# DELETE - Remover item do pedido
def deletar_pedido_item(id_pedido, id_item):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute(
                'DELETE FROM public."pedido_item" WHERE "ID_Pedido" = %s AND "ID_Item" = %s',
                (id_pedido, id_item)
            )
            conexao.commit()
            if cursor.rowcount:
                return True, "Item removido do pedido com sucesso."
            else:
                return False, "Item não encontrado."
    
    except Error as erro:
        return False, f"Erro ao deletar item: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()
