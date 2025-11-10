from dao.conexao import criar_conexao
from psycopg2.extras import RealDictCursor

# 🔹 Criar novo feedback
def criar_feedback(id_ong, id_doador, id_pedido, id_lista, nota, reacao, comentario):
    conexao = criar_conexao()
    if not conexao:
        return False
    try:
        cur = conexao.cursor()
        cur.execute("""
            INSERT INTO feedback (id_ong, id_doador, id_pedido, id_lista, nota, reacao, comentario)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (id_ong, id_doador, id_pedido, id_lista, nota, reacao, comentario))
        conexao.commit()
        cur.close()
        conexao.close()
        return True
    except Exception as e:
        print(f"[LOG] Erro ao criar feedback: {str(e)}")
        return False

# 🔹 Listar todos os feedbacks
def listar_feedbacks():
    conexao = criar_conexao()
    if not conexao:
        return []
    try:
        cur = conexao.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT f.*, d.nome AS nome
            FROM feedback f
            JOIN doador d ON d."CPF_ID" = f.id_doador
            ORDER BY f.id_feedback DESC;
        """)
        feedbacks = cur.fetchall()
        cur.close()
        conexao.close()
        return feedbacks
    except Exception as e:
        print(f"[LOG] Erro ao listar feedbacks: {str(e)}")
        return []

# 🔹 Buscar feedbacks por ONG
def buscar_feedbacks_por_ong(id_ong):
    conexao = criar_conexao()
    if not conexao:
        return []
    try:
        cur = conexao.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT f.*, d.nome AS nome
            FROM feedback f
            JOIN doador d ON d."CPF_ID" = f.id_doador
            WHERE f.id_ong = %s
            ORDER BY f.id_feedback DESC;
        """, (id_ong,))
        feedbacks = cur.fetchall()
        cur.close()
        conexao.close()
        return feedbacks
    except Exception as e:
        print(f"[LOG] Erro ao buscar feedbacks da ONG: {str(e)}")
        return []

# 🔹 Buscar feedbacks por doador
def buscar_feedbacks_por_doador(id_doador):
    conexao = criar_conexao()
    if not conexao:
        return []
    try:
        cur = conexao.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT f.*, d.nome AS nome
            FROM feedback f
            JOIN doador d ON d."CPF_ID" = f.id_doador
            WHERE f.id_doador = %s
            ORDER BY f.id_feedback DESC;
        """, (id_doador,))
        feedbacks = cur.fetchall()
        cur.close()
        conexao.close()
        return feedbacks
    except Exception as e:
        print(f"[LOG] Erro ao buscar feedbacks do doador: {str(e)}")
        return []

# 🔹 Buscar feedbacks por pedido
def buscar_feedbacks_por_pedido(id_pedido):
    conexao = criar_conexao()
    if not conexao:
        return []
    try:
        cur = conexao.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT f.*, d.nome AS nome
            FROM feedback f
            JOIN doador d ON d."CPF_ID" = f.id_doador
            WHERE f.id_pedido = %s
            ORDER BY f.id_feedback DESC;
        """, (id_pedido,))
        feedbacks = cur.fetchall()
        cur.close()
        conexao.close()
        return feedbacks
    except Exception as e:
        print(f"[LOG] Erro ao buscar feedbacks do pedido: {str(e)}")
        return []

# 🔹 Buscar feedbacks por lista
def buscar_feedbacks_por_lista(id_lista):
    conexao = criar_conexao()
    if not conexao:
        return []
    try:
        cur = conexao.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT f.*, d.nome AS nome_doador
            FROM feedback f
            JOIN doador d ON d."CPF_ID" = f.id_doador
            WHERE f.id_lista = %s
            ORDER BY f.id_feedback DESC;
        """, (id_lista,))
        feedbacks = cur.fetchall()
        cur.close()
        conexao.close()
        return feedbacks
    except Exception as e:
        print(f"[LOG] Erro ao buscar feedbacks da lista: {str(e)}")
        return []

# 🔹 Atualizar feedback existente
def atualizar_feedback(id_feedback, nota, reacao, comentario):
    conexao = criar_conexao()
    if not conexao:
        return False
    try:
        cur = conexao.cursor()
        cur.execute("""
            UPDATE feedback
            SET nota = %s, reacao = %s, comentario = %s
            WHERE id_feedback = %s;
        """, (nota, reacao, comentario, id_feedback))
        conexao.commit()
        cur.close()
        conexao.close()
        return True
    except Exception as e:
        print(f"[LOG] Erro ao atualizar feedback: {str(e)}")
        return False

# 🔹 Deletar feedback
def deletar_feedback(id_feedback):
    conexao = criar_conexao()
    if not conexao:
        return False
    try:
        cur = conexao.cursor()
        cur.execute("DELETE FROM feedback WHERE id_feedback = %s;", (id_feedback,))
        conexao.commit()
        cur.close()
        conexao.close()
        return True
    except Exception as e:
        print(f"[LOG] Erro ao deletar feedback: {str(e)}")
        return False
