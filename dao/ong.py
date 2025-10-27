from psycopg2 import Error
from dao.conexao import criar_conexao
import bcrypt

# ---------------------------------------
# Função auxiliar para criptografar senha
# ---------------------------------------
def hash_senha(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode("utf-8").strip()

# ---------------------------
# CREATE - Cadastrar nova ONG
# ---------------------------

def cadastrar_ong(cnpj, nome, cep, contato, email, senha_hash, status_verificacao, status_conta, descricao, cargo):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public."ong" 
                ("CNPJ_ID", nome, cep, contato, email, senha, status_verificacao, status_conta, descricao, cargo) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(cnpj).strip(),
                str(nome).strip(),
                str(cep).strip(),
                str(contato).strip(),
                str(email).strip().lower(),
                str(senha_hash).strip(),
                status_verificacao,
                status_conta,
                str(descricao).strip(),
                str(cargo).strip()
            ))
            conexao.commit()
        return True, "✅ ONG cadastrada com sucesso!"
    
    except Error as erro:
        return False, f"❌ Erro ao cadastrar: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()


# ---------------------------
# READ - Listar todas as ONGs
# ---------------------------
def listar_ongs():
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        
        with conexao.cursor() as cursor:
            cursor.execute('SELECT * FROM public."ong"')
            colunas = [desc[0] for desc in cursor.description]
            registros = cursor.fetchall()
            resultado = []
            for linha in registros:
                item = dict(zip(colunas, linha))
                item["email"] = str(item.get("email", "")).strip().lower()
                item["senha"] = str(item.get("senha", "")).strip().replace("\n", "").replace(" ", "")
                resultado.append(item)
        return resultado
    
    except Exception:
        return []
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# READ - Buscar ONG por ID (CNPJ)
# ---------------------------
def buscar_ong_por_id(cnpj_id):
    try:
        conexao = criar_conexao()
        if not conexao:
            return None

        with conexao.cursor() as cursor:
            cursor.execute('SELECT * FROM public."ong" WHERE "CNPJ_ID" = %s', (cnpj_id,))
            registro = cursor.fetchone()
            if registro:
                colunas = [desc[0] for desc in cursor.description]
                return dict(zip(colunas, registro))
            return None

    except Error as erro:
        return None

    finally:
        if conexao:
            conexao.close()


# -----------------------------
# UPDATE - Atualizar status da ONG
# -----------------------------
def atualizar_status_ong(cnpj, novo_status):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute(
                'UPDATE public."ong" SET status_conta = %s WHERE "CNPJ_ID" = %s',
                (novo_status, cnpj)
            )
            conexao.commit()
            if cursor.rowcount:
                return True, "✅ Status da ONG atualizado com sucesso!"
            else:
                return False, "⚠️ ONG não encontrada."
    
    except Error as erro:
        return False, f"❌ Erro ao atualizar status: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------------------------
# UPDATE - Atualizar status de verificação da ONG
# ---------------------------------------------
def atualizar_status_verificacao_ong(cnpj_id, novo_status):
    """
    Atualiza o status de verificação da ONG.
    novo_status deve ser: 0 (Pendente), 1 (Aprovado), 2 (Recusado)
    """
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute(
                'UPDATE public."ong" SET status_verificacao = %s WHERE "CNPJ_ID" = %s',
                (novo_status, cnpj_id)
            )
            conexao.commit()
            if cursor.rowcount:
                return True, f"✅ Verificação atualizada para {novo_status} com sucesso!"
            else:
                return False, "⚠️ ONG não encontrada."
    
    except Error as erro:
        return False, f"❌ Erro ao atualizar verificação: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# VALIDAÇÃO - ONG está ativa?
# ---------------------------
def ong_esta_ativa(email):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False
        
        with conexao.cursor() as cursor:
            cursor.execute(
                'SELECT status_conta FROM public."ong" WHERE email = %s',
                (email.strip().lower(),)
            )
            resultado = cursor.fetchone()
            return resultado and resultado[0] == 1  # 1 = ativo
    
    except Error:
        return False
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# DELETE - Excluir ONG permanentemente (LGPD)
# ---------------------------
def excluir_ong(cnpj_id):
    """
    Exclui permanentemente a ONG e todos os dados vinculados a ela.
    Requer que o banco esteja configurado com ON DELETE CASCADE nas FKs.
    """
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute('DELETE FROM public."ong" WHERE "CNPJ_ID" = %s', (cnpj_id,))
            conexao.commit()
            if cursor.rowcount:
                return True, "✅ ONG excluída permanentemente com sucesso."
            else:
                return False, "⚠️ ONG não encontrada."
    
    except Error as erro:
        return False, f"❌ Erro ao excluir ONG: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()
