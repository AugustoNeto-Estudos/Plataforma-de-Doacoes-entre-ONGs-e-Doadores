import pytest
from dao.listas import (
    inserir_lista,
    exibir_listas,
    consultar_lista_id,
    exibir_listas_por_ong,
    atualizar_lista,
    deletar_lista,
    atualizar_status_lista,
    atualizar_descricao_lista,
)

# -------------------------------
# Mock de conexão e cursor
# -------------------------------

class DummyCursor:
    def __init__(self, rows=None, rowcount=1, description=None, registro=None):
        self._rows = rows or []
        self._registro = registro
        self.rowcount = rowcount
        self.description = description or []
        self.closed = False
    def execute(self, query, params=None): pass
    def fetchall(self): return self._rows
    def fetchone(self): return self._registro
    def close(self): self.closed = True
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): return False

class DummyConexao:
    def __init__(self, cursor_obj):
        self._cursor_obj = cursor_obj
        self.closed = False
    def cursor(self, cursor_factory=None): return self._cursor_obj
    def commit(self): pass
    def close(self): self.closed = True
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): return False

# -------------------------------
# Testes para inserir_lista
# -------------------------------

def test_inserir_lista_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    ok, msg = inserir_lista("LISTA1", "Titulo", "ONG1", 1, "Descricao")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_inserir_lista_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: None)
    ok, msg = inserir_lista("LISTA1", "Titulo", "ONG1", 1, "Descricao")
    assert ok is False

# -------------------------------
# Testes para exibir_listas
# -------------------------------

def test_exibir_listas_sucesso(monkeypatch):
    colunas = ["ID_Lista", "titulo", "ID_ONG", "status", "descricao"]
    registros = [("LISTA1", "Titulo", "ONG1", 1, "Descricao")]
    dummy_cursor = DummyCursor(rows=registros, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    resultado = exibir_listas()
    assert len(resultado) == 1
    assert resultado[0]["ID_Lista"] == "LISTA1"

def test_exibir_listas_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: None)
    resultado = exibir_listas()
    assert resultado == []

# -------------------------------
# Testes para consultar_lista_id
# -------------------------------

def test_consultar_lista_id_sucesso(monkeypatch):
    colunas = ["ID_Lista", "titulo", "ID_ONG", "status", "descricao"]
    registro = ("LISTA1", "Titulo", "ONG1", 1, "Descricao")
    dummy_cursor = DummyCursor(registro=registro, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    resultado = consultar_lista_id("LISTA1")
    assert resultado["ID_Lista"] == "LISTA1"

def test_consultar_lista_id_nao_encontrada(monkeypatch):
    dummy_cursor = DummyCursor(registro=None)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    resultado = consultar_lista_id("LISTAX")
    assert resultado is None

def test_consultar_lista_id_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: None)
    resultado = consultar_lista_id("LISTA1")
    assert resultado is None

# -------------------------------
# Testes para exibir_listas_por_ong
# -------------------------------

def test_exibir_listas_por_ong_sucesso(monkeypatch):
    colunas = ["ID_Lista", "titulo", "ID_ONG", "status", "descricao"]
    registros = [("LISTA1", "Titulo", "ONG1", 1, "Descricao")]
    dummy_cursor = DummyCursor(rows=registros, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    resultado = exibir_listas_por_ong("ONG1")
    assert len(resultado) == 1
    assert resultado[0]["ID_ONG"] == "ONG1"

def test_exibir_listas_por_ong_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: None)
    resultado = exibir_listas_por_ong("ONG1")
    assert resultado == []

# -------------------------------
# Testes para atualizar_lista
# -------------------------------

def test_atualizar_lista_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_lista("LISTA1", titulo="NovoTitulo")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_lista_nao_encontrada(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_lista("LISTA1", titulo="NovoTitulo")
    assert ok is False
    assert "não encontrada" in msg.lower()

def test_atualizar_lista_sem_campos(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_lista("LISTA1")
    assert ok is False
    assert "nenhum campo" in msg.lower()

def test_atualizar_lista_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: None)
    ok, msg = atualizar_lista("LISTA1", titulo="NovoTitulo")
    assert ok is False

# -------------------------------
# Testes para deletar_lista
# -------------------------------

def test_deletar_lista_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_lista("LISTA1")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_deletar_lista_nao_encontrada(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_lista("LISTA1")
    assert ok is False
    assert "não encontrada" in msg.lower()

def test_deletar_lista_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: None)
    ok, msg = deletar_lista("LISTA1")
    assert ok is False

# -------------------------------
# Testes para atualizar_status_lista
# -------------------------------

def test_atualizar_status_lista_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_status_lista("LISTA1", 2)
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_status_lista_nao_encontrada(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_status_lista("LISTA1", 2)
    assert ok is False
    assert "não encontrada" in msg.lower()


def test_atualizar_status_lista_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: None)
    ok, msg = atualizar_status_lista("LISTA1", 2)
    assert ok is False


# -------------------------------
# Testes para atualizar_descricao_lista
# -------------------------------

def test_atualizar_descricao_lista_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_descricao_lista("LISTA1", "Nova descrição")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_descricao_lista_nao_encontrada(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_descricao_lista("LISTA1", "Nova descrição")
    assert ok is False
    assert "não encontrada" in msg.lower()

def test_atualizar_descricao_lista_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.listas.criar_conexao", lambda: None)
    ok, msg = atualizar_descricao_lista("LISTA1", "Nova descrição")
    assert ok is False