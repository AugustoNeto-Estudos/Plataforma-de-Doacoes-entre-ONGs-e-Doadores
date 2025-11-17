from psycopg2 import Error
from dao.conexao import criar_conexao

# CREATE - Inserir itens de uma intenção
def inserir_itens_intencao(id_intencao, itens):
    """
    Insere múltiplos itens associados a uma intenção.
    itens deve ser uma lista de dicionários:
    [{"id_item": "ITEM01", "quantidade_pretendida": 3, "observacao": "opcional"}, ...]
    """
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."

        with conexao.cursor() as cursor:
            sql = """
                INSERT INTO public.intencao_item ("ID_Intencao", "ID_Item", quantidade_pretendida, observacao)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT ("ID_Intencao", "ID_Item") DO UPDATE
                SET quantidade_pretendida = EXCLUDED.quantidade_pretendida,
                    observacao = EXCLUDED.observacao
            """
            for item in itens:
                valores = (
                    id_intencao,
                    item["id_item"],
                    item["quantidade_pretendida"],
                    item.get("observacao")
                )
                cursor.execute(sql, valores)

            conexao.commit()
        return True, "Itens da intenção inseridos/atualizados com sucesso."

    except Error as erro:
        return False, f"Erro ao inserir itens da intenção: {str(erro).strip()[:200]}"

    finally:
        if conexao:
            conexao.close()

# READ - Listar itens de uma intenção
def listar_itens_intencao(id_intencao):
    try:
        conexao = criar_conexao()
        if not conexao:
            return []

        with conexao.cursor() as cursor:
            sql = 'SELECT * FROM public.intencao_item WHERE "ID_Intencao" = %s'
            cursor.execute(sql, (id_intencao,))
            registros = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
            return [dict(zip(colunas, linha)) for linha in registros]

    except Error as erro:
        return False,f"Erro ao listar itens da intenção: {str(erro).strip()[:200]}"

    finally:
        if conexao:
            conexao.close()

# UPDATE - Atualizar quantidade_pretendida e/ou observacao
def atualizar_item_intencao(id_intencao, id_item, nova_quantidade=None, nova_observacao=None):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."

        atualizacoes, valores = [], []
        if nova_quantidade is not None:
            atualizacoes.append("quantidade_pretendida = %s")
            valores.append(nova_quantidade)
        if nova_observacao is not None:
            atualizacoes.append("observacao = %s")
            valores.append(nova_observacao)

        if not atualizacoes:
            return False, "Nenhum campo para atualizar."

        with conexao.cursor() as cursor:
            sql = f"""
                UPDATE public.intencao_item
                SET {", ".join(atualizacoes)}
                WHERE "ID_Intencao" = %s AND "ID_Item" = %s
            """
            valores.extend([id_intencao, id_item])
            cursor.execute(sql, valores)
            conexao.commit()

            if cursor.rowcount:
                return True, "Item da intenção atualizado com sucesso."
            else:
                return False, "Item não encontrado nesta intenção."

    except Error as erro:
        return False, f"Erro ao atualizar item da intenção: {str(erro).strip()[:200]}"

    finally:
        if conexao:
            conexao.close()

# DELETE - Excluir item de uma intenção
def deletar_item_intencao(id_intencao, id_item):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."

        with conexao.cursor() as cursor:
            sql = 'DELETE FROM public.intencao_item WHERE "ID_Intencao" = %s AND "ID_Item" = %s'
            cursor.execute(sql, (id_intencao, id_item))
            conexao.commit()

            if cursor.rowcount:
                return True, "Item removido da intenção com sucesso."
            else:
                return False, "Item não encontrado nesta intenção."

    except Error as erro:
        return False, f"Erro ao deletar item da intenção: {str(erro).strip()[:200]}"

    finally:
        if conexao:
            conexao.close()
