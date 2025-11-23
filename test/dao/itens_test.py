import pytest
from dao.itens import (
    inserir_item,
    exibir_itens,
    consultar_item_id,
    atualizar_item,
    deletar_item,
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
# Testes para inserir_item
# -------------------------------

def test_inserir_item_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: dummy_conexao)

    ok, msg = inserir_item("ITEM01", "Categoria", "Subcategoria")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_inserir_item_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: None)
    ok, msg = inserir_item("ITEM01", "Categoria")
    assert ok is False

# -------------------------------
# Testes para exibir_itens
# -------------------------------

def test_exibir_itens_sucesso(monkeypatch):
    colunas = ["ID_Item", "categoria", "subcategoria"]
    registros = [("ITEM01", "Categoria", "Subcategoria")]
    dummy_cursor = DummyCursor(rows=registros, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: dummy_conexao)

    resultado = exibir_itens()
    assert len(resultado) == 1
    assert resultado[0]["ID_Item"] == "ITEM01"

def test_exibir_itens_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: None)
    resultado = exibir_itens()
    assert resultado == []

# -------------------------------
# Testes para consultar_item_id
# -------------------------------

def test_consultar_item_id_sucesso(monkeypatch):
    colunas = ["ID_Item", "categoria", "subcategoria"]
    registro = ("ITEM01", "Categoria", "Subcategoria")
    dummy_cursor = DummyCursor(registro=registro, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: dummy_conexao)

    resultado = consultar_item_id("ITEM01")
    assert resultado["ID_Item"] == "ITEM01"

def test_consultar_item_id_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(registro=None)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: dummy_conexao)

    resultado = consultar_item_id("ITEM99")
    assert resultado is None

def test_consultar_item_id_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: None)
    resultado = consultar_item_id("ITEM01")
    assert resultado is None

# -------------------------------
# Testes para atualizar_item
# -------------------------------

def test_atualizar_item_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_item("ITEM01", categoria="NovaCategoria")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_item_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_item("ITEM01", categoria="NovaCategoria")
    assert ok is False
    assert "não encontrado" in msg.lower()

def test_atualizar_item_sem_campos(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_item("ITEM01")
    assert ok is False
    assert "nenhum campo" in msg.lower()

def test_atualizar_item_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: None)
    ok, msg = atualizar_item("ITEM01", categoria="NovaCategoria")
    assert ok is False

# -------------------------------
# Testes para deletar_item
# -------------------------------

def test_deletar_item_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_item("ITEM01")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_deletar_item_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_item("ITEM01")
    assert ok is False
    assert "não encontrado" in msg.lower()

def test_deletar_item_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itens.criar_conexao", lambda: None)
    ok, msg = deletar_item("ITEM01")
    assert ok is False
