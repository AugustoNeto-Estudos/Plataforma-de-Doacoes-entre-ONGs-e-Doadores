import pytest
from dao.itensLista import (
    inserir_lista_item,
    exibir_lista_itens,
    consultar_lista_item,
    atualizar_lista_item,
    deletar_lista_item,
    atualizar_quantidade_item,
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
# Testes para inserir_lista_item
# -------------------------------

def test_inserir_lista_item_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: dummy_conexao)

    ok, msg = inserir_lista_item("LISTA1", "ITEM1", 5)
    assert ok is True
    assert "sucesso" in msg.lower()

def test_inserir_lista_item_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: None)
    ok, msg = inserir_lista_item("LISTA1", "ITEM1", 5)
    assert ok is False

# -------------------------------
# Testes para exibir_lista_itens
# -------------------------------

def test_exibir_lista_itens_sucesso(monkeypatch):
    colunas = ["ID_Lista", "ID_Item", "quantidade_necessaria"]
    registros = [("LISTA1", "ITEM1", 5)]
    dummy_cursor = DummyCursor(rows=registros, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: dummy_conexao)

    resultado = exibir_lista_itens("LISTA1")
    assert len(resultado) == 1
    assert resultado[0]["ID_Item"] == "ITEM1"

def test_exibir_lista_itens_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: None)
    resultado = exibir_lista_itens("LISTA1")
    assert resultado == []

# -------------------------------
# Testes para consultar_lista_item
# -------------------------------

def test_consultar_lista_item_sucesso(monkeypatch):
    colunas = ["ID_Lista", "ID_Item", "quantidade_necessaria"]
    registro = ("LISTA1", "ITEM1", 5)
    dummy_cursor = DummyCursor(registro=registro, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: dummy_conexao)

    resultado = consultar_lista_item("LISTA1", "ITEM1")
    assert resultado["ID_Item"] == "ITEM1"

def test_consultar_lista_item_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(registro=None)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: dummy_conexao)

    resultado = consultar_lista_item("LISTA1", "ITEMX")
    assert resultado is None

def test_consultar_lista_item_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: None)
    resultado = consultar_lista_item("LISTA1", "ITEM1")
    assert resultado is None

# -------------------------------
# Testes para atualizar_lista_item
# -------------------------------

def test_atualizar_lista_item_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_lista_item("LISTA1", "ITEM1", 10)
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_lista_item_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_lista_item("LISTA1", "ITEM1", 10)
    assert ok is False
    assert "não encontrado" in msg.lower()

def test_atualizar_lista_item_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: None)
    ok, msg = atualizar_lista_item("LISTA1", "ITEM1", 10)
    assert ok is False

# -------------------------------
# Testes para deletar_lista_item
# -------------------------------

def test_deletar_lista_item_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_lista_item("LISTA1", "ITEM1")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_deletar_lista_item_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_lista_item("LISTA1", "ITEM1")
    assert ok is False
    assert "não encontrado" in msg.lower()

def test_deletar_lista_item_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: None)
    ok, msg = deletar_lista_item("LISTA1", "ITEM1")
    assert ok is False

# -------------------------------
# Testes para atualizar_quantidade_item
# -------------------------------

def test_atualizar_quantidade_item_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_quantidade_item("LISTA1", "ITEM1", 20)
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_quantidade_item_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_quantidade_item("LISTA1", "ITEM1", 20)
    assert ok is False
    assert "não encontrado" in msg.lower()

def test_atualizar_quantidade_item_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itensLista.criar_conexao", lambda: None)
    ok, msg = atualizar_quantidade_item("LISTA1", "ITEM1", 20)
    assert ok is False
