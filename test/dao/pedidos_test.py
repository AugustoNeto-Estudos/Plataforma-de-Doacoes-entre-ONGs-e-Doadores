import pytest
from dao.pedidos import (
    inserir_pedido,
    listar_pedidos,
    atualizar_status_pedido,
    atualizar_pedido,
    deletar_pedido,
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
# Testes para inserir_pedido
# -------------------------------

def test_inserir_pedido_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.pedidos.criar_conexao", lambda: dummy_conexao)

    ok, msg = inserir_pedido("PED01", "ONG1", "DOADOR1", "INT1", 1, "2025-11-08")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_inserir_pedido_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.pedidos.criar_conexao", lambda: None)
    ok, msg = inserir_pedido("PED01", "ONG1", "DOADOR1", "INT1", 1, "2025-11-08")
    assert ok is False

# -------------------------------
# Testes para listar_pedidos
# -------------------------------

def test_listar_pedidos_sucesso(monkeypatch):
    colunas = ["ID_Pedido", "ID_ONG", "ID_Doador", "ID_Intencao", "status", "data_criacao"]
    registros = [("PED01", "ONG1", "DOADOR1", "INT1", 1, "2025-11-08")]
    dummy_cursor = DummyCursor(rows=registros, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.pedidos.criar_conexao", lambda: dummy_conexao)

    resultado = listar_pedidos()
    assert len(resultado) == 1
    assert resultado[0]["ID_Pedido"] == "PED01"

def test_listar_pedidos_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.pedidos.criar_conexao", lambda: None)
    resultado = listar_pedidos()
    assert resultado == []

# -------------------------------
# Testes para atualizar_status_pedido
# -------------------------------

def test_atualizar_status_pedido_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.pedidos.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_status_pedido("PED01", 2)
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_status_pedido_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.pedidos.criar_conexao", lambda: None)
    ok, msg = atualizar_status_pedido("PED01", 2)
    assert ok is False

# -------------------------------
# Testes para atualizar_pedido
# -------------------------------

def test_atualizar_pedido_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.pedidos.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_pedido("PED01", "ONG1", "DOADOR1", "INT1", 1, "2025-11-08")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_pedido_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.pedidos.criar_conexao", lambda: None)
    ok, msg = atualizar_pedido("PED01", "ONG1", "DOADOR1", "INT1", 1, "2025-11-08")
    assert ok is False

# -------------------------------
# Testes para deletar_pedido
# -------------------------------

def test_deletar_pedido_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.pedidos.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_pedido("PED01")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_deletar_pedido_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.pedidos.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_pedido("PED01")
    assert ok is False
    assert "não encontrado" in msg.lower()

def test_deletar_pedido_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.pedidos.criar_conexao", lambda: None)
    ok, msg = deletar_pedido("PED01")
    assert ok is False
