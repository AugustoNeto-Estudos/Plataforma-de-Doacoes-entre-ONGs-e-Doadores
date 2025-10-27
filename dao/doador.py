from psycopg2 import Error
from dao.conexao import criar_conexao
import bcrypt

# ---------------------------
# Função auxiliar para criptografar senha
# ---------------------------
def hash_senha(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode("utf-8").strip()

# ---------------------------
# CREATE - Cadastrar novo doador
# ---------------------------
def cadastrar_doador(cpf, nome, email, contato, senha_hash, status_conta, cargo):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public."doador" 
                ("CPF_ID", nome, email, contato, senha, status_conta, cargo) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                str(cpf).strip(),
                str(nome).strip(),
                str(email).strip().lower(),
                str(contato).strip(),
                str(senha_hash).strip(),
                status_conta,
                cargo
            ))
            conexao.commit()
        return True, "✅ Doador cadastrado com sucesso!"
    
    except Error as erro:
        mensagem = f"❌ Erro ao cadastrar: {str(erro).strip().replace(chr(10), ' ')[:200]}"
        return False, mensagem
    
    finally:
        if conexao:
            conexao.close()


# ---------------------------
# READ - Listar todos os doadores
# ---------------------------
def listar_doadores():
    try:
        conexao = criar_conexao()
        if not conexao:
            return []
        
        with conexao.cursor() as cursor:
            cursor.execute('SELECT * FROM public."doador"')
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
# UPDATE - Atualizar status do doador
# ---------------------------
def atualizar_status_doador(cpf, novo_status):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute(
                'UPDATE public."doador" SET status_conta = %s WHERE "CPF_ID" = %s',
                (novo_status, cpf)
            )
            conexao.commit()
            if cursor.rowcount:
                return True, "✅ Status do doador atualizado com sucesso!"
            else:
                return False, "⚠️ Doador não encontrado."
    
    except Error as erro:
        return False, f"❌ Erro ao atualizar status: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()

# ---------------------------
# VALIDAÇÃO - Verifica se o doador está ativo
# ---------------------------
def doador_esta_ativo(email):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False
        
        with conexao.cursor() as cursor:
            cursor.execute(
                'SELECT status_conta FROM public."doador" WHERE email = %s',
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
# DELETE - Excluir doador permanentemente (LGPD)
# ---------------------------
def excluir_doador(cpf_id):
    """
    Exclui permanentemente o doador e seus dados vinculados.
    Requer que o banco esteja configurado com ON DELETE CASCADE nas FKs.
    """
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "❌ Falha ao conectar ao banco."
        
        with conexao.cursor() as cursor:
            cursor.execute('DELETE FROM public."doador" WHERE "CPF_ID" = %s', (cpf_id,))
            conexao.commit()
            if cursor.rowcount:
                return True, "✅ Doador excluído permanentemente com sucesso."
            else:
                return False, "⚠️ Doador não encontrado."
    
    except Error as erro:
        return False, f"❌ Erro ao excluir doador: {str(erro).strip()[:200]}"
    
    finally:
        if conexao:
            conexao.close()
