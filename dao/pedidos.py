from psycopg2 import Error
from dao.conexao import criar_conexao
from datetime import date

# ---------------------------
# CREATE - Inserir novo pedido
# ---------------------------
def inserir_pedido(id_pedido, id_ong, id_doador, id_intencao, status, data_criacao):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
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
        return False, f"❌ Erro ao inserir pedido: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# READ - Listar todos os pedidos
# ---------------------------
def listar_pedidos():
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        
        with conexao.cursor() as cursor:
            cursor.execute('SELECT * FROM public."pedido" ORDER BY data_criacao DESC')
            registros = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
            return [dict(zip(colunas, linha)) for linha in registros]
    
    except Error as erro:
        return(f"❌ Erro ao listar pedidos: {str(erro).strip()[:200]}")
    
    finally:
        if conexao:
            conexao.close()


# ---------------------------
# UPDATE - Atualizar status do pedido
# ---------------------------
def atualizar_status_pedido(id_pedido, novo_status):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            sql = 'UPDATE public."pedido" SET status = %s WHERE "ID_Pedido" = %s'
            cursor.execute(sql, (novo_status, id_pedido))
            conexao.commit()
        return True, "✅ Status do pedido atualizado com sucesso!"
    
    except Error as erro:
        return False, f"❌ Erro ao atualizar status: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# UPDATE - Atualizar dados do pedido
# ---------------------------
def atualizar_pedido(id_pedido, id_ong, id_doador, id_intencao,  status, data_criacao):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
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
        return False, f"❌ Erro ao atualizar pedido: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# DELETE - Excluir pedido
# ---------------------------
def deletar_pedido(id_pedido):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute('DELETE FROM public."pedido" WHERE "ID_Pedido" = %s', (id_pedido,))
            conexao.commit()
            if cursor.rowcount:
                return True, "✅ Pedido deletado com sucesso!"
            else:
                return False, "⚠️ Pedido não encontrado."
    
    except Error as erro:
        return False, f"❌ Erro ao deletar pedido: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()
