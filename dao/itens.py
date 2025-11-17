from psycopg2 import Error
from dao.conexao import criar_conexao

# CREATE - Inserir novo item
def inserir_item(id_item, categoria, subcategoria=None):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."

        with conexao.cursor() as cursor:
            sql = """
                INSERT INTO public."item" ("ID_Item", categoria, subcategoria)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (id_item, categoria, subcategoria))
            conexao.commit()
        return True, "Item inserido com sucesso."

    except Error as erro:
        return False, f"Erro ao inserir item: {str(erro).strip()[:200]}"

    finally:
        if conexao:
            conexao.close()

# READ - Exibir todos os itens
def exibir_itens():
    try:
        conexao = criar_conexao()
        if not conexao:
            return []

        with conexao.cursor() as cursor:
            cursor.execute('SELECT * FROM public."item" ORDER BY "ID_Item" ASC')
            registros = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
            return [dict(zip(colunas, linha)) for linha in registros]

    except Error as erro:
        print(f"Erro ao exibir itens: {str(erro).strip()[:200]}")
        return []

    finally:
        if conexao:
            conexao.close()

# READ - Consultar item por ID
def consultar_item_id(id_item):
    try:
        conexao = criar_conexao()
        if not conexao:
            return None

        with conexao.cursor() as cursor:
            cursor.execute('SELECT * FROM public."item" WHERE "ID_Item" = %s', (id_item,))
            registro = cursor.fetchone()
            if registro:
                colunas = [desc[0] for desc in cursor.description]
                return dict(zip(colunas, registro))
            return None

    except Error as erro:
        print(f"Erro ao consultar item: {str(erro).strip()[:200]}")
        return None

    finally:
        if conexao:
            conexao.close()

# UPDATE - Atualizar item
def atualizar_item(id_item, categoria=None, subcategoria=None):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."

        atualizacoes, valores = [], []
        if categoria:
            atualizacoes.append("categoria = %s")
            valores.append(categoria)
        if subcategoria:
            atualizacoes.append("subcategoria = %s")
            valores.append(subcategoria)

        if not atualizacoes:
            return False, "Nenhum campo para atualizar."

        with conexao.cursor() as cursor:
            sql = f'UPDATE public."item" SET {", ".join(atualizacoes)} WHERE "ID_Item" = %s'
            valores.append(id_item)
            cursor.execute(sql, valores)
            conexao.commit()
            if cursor.rowcount:
                return True, "Item atualizado com sucesso."
            else:
                return False, "Item não encontrado."

    except Error as erro:
        return False, f"Erro ao atualizar item: {str(erro).strip()[:200]}"

    finally:
        if conexao:
            conexao.close()

# DELETE - Excluir item
def deletar_item(id_item):
    try:
        conexao = criar_conexao()
        if not conexao:
            return False, "Falha ao conectar ao banco."

        with conexao.cursor() as cursor:
            cursor.execute('DELETE FROM public."item" WHERE "ID_Item" = %s', (id_item,))
            conexao.commit()
            if cursor.rowcount:
                return True, "Item deletado com sucesso."
            else:
                return False, "Item não encontrado."

    except Error as erro:
        return False, f"Erro ao deletar item: {str(erro).strip()[:200]}"

    finally:
        if conexao:
            conexao.close()
