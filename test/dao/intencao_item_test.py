import pytest
from dao.intencao_item import (
    inserir_itens_intencao,
    listar_itens_intencao,
    atualizar_item_intencao,
    deletar_item_intencao,
)

# -------------------------------
# Mock de conexão e cursor
# -------------------------------

class DummyCursor:
    def __init__(self, rows=None, rowcount=1, description=None):
        self._rows = rows or []
        self.rowcount = rowcount
        self.description = description or []
        self.closed = False
    def execute(self, query, params=None): pass
    def fetchall(self): return self._rows
    def fetchone(self): return self._rows[0] if self._rows else None
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
# Testes para inserir_itens_intencao
# -------------------------------

def test_inserir_itens_intencao_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_item.criar_conexao", lambda: dummy_conexao)

    itens = [{"id_item": "ITEM01", "quantidade_pretendida": 3, "observacao": "teste"}]
    ok, msg = inserir_itens_intencao("INT001", itens)
    assert ok is True
    assert "sucesso" in msg.lower()

def test_inserir_itens_intencao_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.intencao_item.criar_conexao", lambda: None)
    itens = [{"id_item": "ITEM01", "quantidade_pretendida": 3}]
    ok, msg = inserir_itens_intencao("INT001", itens)
    assert ok is False

# -------------------------------
# Testes para listar_itens_intencao
# -------------------------------

def test_listar_itens_intencao_sucesso(monkeypatch):
    colunas = ["ID_Intencao", "ID_Item", "quantidade_pretendida", "observacao"]
    registros = [("INT001", "ITEM01", 3, "teste")]
    dummy_cursor = DummyCursor(rows=registros, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_item.criar_conexao", lambda: dummy_conexao)

    resultado = listar_itens_intencao("INT001")
    assert len(resultado) == 1
    assert resultado[0]["ID_Item"] == "ITEM01"

def test_listar_itens_intencao_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.intencao_item.criar_conexao", lambda: None)
    resultado = listar_itens_intencao("INT001")
    assert resultado == []

# -------------------------------
# Testes para atualizar_item_intencao
# -------------------------------

def test_atualizar_item_intencao_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_item.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_item_intencao("INT001", "ITEM01", nova_quantidade=5)
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_item_intencao_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_item.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_item_intencao("INT001", "ITEM01", nova_quantidade=5)
    assert ok is False
    assert "não encontrado" in msg.lower()

def test_atualizar_item_intencao_sem_campos(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_item.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_item_intencao("INT001", "ITEM01")
    assert ok is False
    assert "nenhum campo" in msg.lower()

def test_atualizar_item_intencao_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.intencao_item.criar_conexao", lambda: None)
    ok, msg = atualizar_item_intencao("INT001", "ITEM01", nova_quantidade=5)
    assert ok is False

# -------------------------------
# Testes para deletar_item_intencao
# -------------------------------

def test_deletar_item_intencao_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_item.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_item_intencao("INT001", "ITEM01")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_deletar_item_intencao_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_item.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_item_intencao("INT001", "ITEM01")
    assert ok is False
    assert "não encontrado" in msg.lower()

def test_deletar_item_intencao_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.intencao_item.criar_conexao", lambda: None)
    ok, msg = deletar_item_intencao("INT001", "ITEM01")
    assert ok is False
