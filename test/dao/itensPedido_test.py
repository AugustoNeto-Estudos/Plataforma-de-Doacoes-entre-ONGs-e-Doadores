import pytest
from dao.itensPedido import (
    inserir_pedido_item,
    exibir_pedidos_itens,
    consultar_pedido_item,
    atualizar_pedido_item,
    deletar_pedido_item,
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
# Testes para inserir_pedido_item
# -------------------------------

def test_inserir_pedido_item_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: dummy_conexao)

    ok, msg = inserir_pedido_item("PED01", "ITEM01", 3, "obs")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_inserir_pedido_item_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: None)
    ok, msg = inserir_pedido_item("PED01", "ITEM01", 3)
    assert ok is False

# -------------------------------
# Testes para exibir_pedidos_itens
# -------------------------------

def test_exibir_pedidos_itens_sucesso(monkeypatch):
    colunas = ["ID_Pedido", "ID_Item", "quantidade", "observacao"]
    registros = [("PED01", "ITEM01", 3, "obs")]
    dummy_cursor = DummyCursor(rows=registros, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: dummy_conexao)

    resultado = exibir_pedidos_itens("PED01")
    assert len(resultado) == 1
    assert resultado[0]["ID_Item"] == "ITEM01"

def test_exibir_pedidos_itens_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: None)
    resultado = exibir_pedidos_itens("PED01")
    assert resultado == []

# -------------------------------
# Testes para consultar_pedido_item
# -------------------------------

def test_consultar_pedido_item_sucesso(monkeypatch):
    colunas = ["ID_Pedido", "ID_Item", "quantidade", "observacao"]
    registro = ("PED01", "ITEM01", 3, "obs")
    dummy_cursor = DummyCursor(registro=registro, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: dummy_conexao)

    resultado = consultar_pedido_item("PED01", "ITEM01")
    assert resultado["ID_Item"] == "ITEM01"

def test_consultar_pedido_item_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(registro=None)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: dummy_conexao)

    resultado = consultar_pedido_item("PED01", "ITEMX")
    assert resultado is None

def test_consultar_pedido_item_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: None)
    resultado = consultar_pedido_item("PED01", "ITEM01")
    assert resultado is None

# -------------------------------
# Testes para atualizar_pedido_item
# -------------------------------

def test_atualizar_pedido_item_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_pedido_item("PED01", "ITEM01", quantidade=5)
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_pedido_item_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_pedido_item("PED01", "ITEM01", quantidade=5)
    assert ok is False
    assert "não encontrado" in msg.lower()

def test_atualizar_pedido_item_sem_campos(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_pedido_item("PED01", "ITEM01")
    assert ok is False
    assert "nenhum campo" in msg.lower()

def test_atualizar_pedido_item_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: None)
    ok, msg = atualizar_pedido_item("PED01", "ITEM01", quantidade=5)
    assert ok is False

# -------------------------------
# Testes para deletar_pedido_item
# -------------------------------

def test_deletar_pedido_item_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_pedido_item("PED01", "ITEM01")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_deletar_pedido_item_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_pedido_item("PED01", "ITEM01")
    assert ok is False
    assert "não encontrado" in msg.lower()

def test_deletar_pedido_item_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.itensPedido.criar_conexao", lambda: None)
    ok, msg = deletar_pedido_item("PED01", "ITEM01")
    assert ok is False
