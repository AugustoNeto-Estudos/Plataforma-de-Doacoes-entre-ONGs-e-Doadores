from psycopg2 import Error
from dao.conexao import criar_conexao
from datetime import date
import uuid

# --- Mapeamento de Status ---
STATUS_MAP_STR_TO_INT = {
    "Pendente": 0,
    "Aprovado": 1,
    "Reprovado": 2,
    "Finalizado": 3
}

STATUS_MAP_INT_TO_STR = {v: k for k, v in STATUS_MAP_STR_TO_INT.items()}

# ---------------------------
# CREATE - Inserir nova intenção de doação
# ---------------------------

def inserir_intencao(id_intencao, id_ong, id_doador, id_lista, status_str, data_criacao):
    try:
        status_int = STATUS_MAP_STR_TO_INT.get(status_str, 0) # Converte a string para o inteiro
        
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            sql = """
                INSERT INTO public."intencaodoacao" 
                ("ID_Intencao", "ID_ONG", "ID_Doador", "ID_Lista", status, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            valores = (id_intencao, id_ong, id_doador, id_lista, status_int, data_criacao) # Usa o inteiro
            cursor.execute(sql, valores)
            conexao.commit()
        return True, "✅ Intenção inserida com sucesso!"
    
    except Error as erro:
        return False, f"❌ Erro ao inserir intenção: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# READ - Listar intenções de doação
# ---------------------------
def listar_intencoes():
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        
        with conexao.cursor() as cursor:
            cursor.execute('SELECT * FROM public."intencaodoacao" ORDER BY data_criacao DESC')
            registros = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
            
            # Converte o status de inteiro para string
            lista_intencoes = []
            for linha in registros:
                intencao = dict(zip(colunas, linha))
                intencao["status"] = STATUS_MAP_INT_TO_STR.get(intencao["status"], "Desconhecido")
                lista_intencoes.append(intencao)
            
            return lista_intencoes
    
    except Error as erro:
        return(f"❌ Erro ao listar intenções: {str(erro).strip()[:200]}")

    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# UPDATE - Atualizar intenção completa
# ---------------------------
def atualizar_intencao(id_intencao, id_ong, id_doador, id_lista, status_str, data_criacao):
    try:
        status_int = STATUS_MAP_STR_TO_INT.get(status_str, 0) # Converte a string para o inteiro
        
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            sql = """
                UPDATE public."intencaodoacao"
                SET "ID_ONG" = %s,
                    "ID_Doador" = %s,
                    "ID_Lista" = %s,
                    status = %s,
                    data_criacao = %s
                WHERE "ID_Intencao" = %s
            """
            valores = (id_ong, id_doador, id_lista, status_int, data_criacao, id_intencao) # Usa o inteiro
            cursor.execute(sql, valores)
            conexao.commit()
        return True, "✅ Intenção atualizada com sucesso!"
    
    except Error as erro:
        return False, f"❌ Erro ao atualizar intenção: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# UPDATE - Atualizar apenas o status da intenção
# ---------------------------
def atualizar_status(id_intencao, novo_status_str):
    try:
        novo_status_int = STATUS_MAP_STR_TO_INT.get(novo_status_str, 0) # Converte a string para o inteiro
        
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            sql = 'UPDATE public."intencaodoacao" SET status = %s WHERE "ID_Intencao" = %s'
            cursor.execute(sql, (novo_status_int, id_intencao)) # Usa o inteiro
            conexao.commit()
        return True, "✅ Status atualizado com sucesso!"
    
    except Error as erro:
        return False, f"❌ Erro ao atualizar status: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()


def verificar_intencao_existente(id_doador, id_lista):
    """
    Verifica se existe uma intenção de doação PENDENTE (status != 'Finalizado')
    para a lista e doador especificados.
    """
    try:
        status_finalizado = STATUS_MAP_STR_TO_INT.get("Finalizado", 3)
        
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."

        with conexao.cursor() as cursor:
            # Verifica se existe alguma intenção para o doador e lista que NÃO esteja 'Finalizado' (status != 3)
            sql = 'SELECT COUNT(*) FROM public."intencaodoacao" WHERE "ID_Doador" = %s AND "ID_Lista" = %s AND status != %s'
            cursor.execute(sql, (id_doador, id_lista, status_finalizado)) # Usa o inteiro
            count = cursor.fetchone()[0]
            return count > 0, ""

    except Error as erro:
        return False, f"❌ Erro ao verificar intenção existente: {str(erro).strip()[:200]}"

    finally:
        if conexao:
            conexao.close()
            
# ---------------------------
# DELETE - Excluir intenção de doação
# ---------------------------
def deletar_intencao(id_intencao):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute('DELETE FROM public."intencaodoacao" WHERE "ID_Intencao" = %s', (id_intencao,))
            conexao.commit()
            if cursor.rowcount:
                return True, "✅ Intenção deletada com sucesso!"
            else:
                return False, "⚠️ Intenção não encontrada."
    
    except Error as erro:
        return False, f"❌ Erro ao deletar intenção: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()
