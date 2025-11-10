import pytest
from dao.intencao_de_doacao import (
    inserir_intencao,
    listar_intencoes,
    atualizar_intencao,
    atualizar_status,
    verificar_intencao_existente,
    deletar_intencao,
    STATUS_MAP_STR_TO_INT,
    STATUS_MAP_INT_TO_STR,
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
# Testes para inserir_intencao
# -------------------------------

def test_inserir_intencao_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: dummy_conexao)

    ok, msg = inserir_intencao("id1", "ong1", "doador1", "lista1", "Aprovado", "2025-11-07")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_inserir_intencao_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: None)
    ok, msg = inserir_intencao("id1", "ong1", "doador1", "lista1", "Aprovado", "2025-11-07")
    assert ok is False

# -------------------------------
# Testes para listar_intencoes
# -------------------------------

def test_listar_intencoes_sucesso(monkeypatch):
    colunas = ["ID_Intencao", "ID_ONG", "ID_Doador", "ID_Lista", "status", "data_criacao"]
    registros = [("id1", "ong1", "doador1", "lista1", 1, "2025-11-07")]
    dummy_cursor = DummyCursor(rows=registros, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: dummy_conexao)

    resultado = listar_intencoes()
    assert len(resultado) == 1
    assert resultado[0]["status"] == STATUS_MAP_INT_TO_STR[1]

def test_listar_intencoes_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: None)
    resultado = listar_intencoes()
    assert resultado == []

# -------------------------------
# Testes para atualizar_intencao
# -------------------------------

def test_atualizar_intencao_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_intencao("id1", "ong1", "doador1", "lista1", "Reprovado", "2025-11-07")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_intencao_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: None)
    ok, msg = atualizar_intencao("id1", "ong1", "doador1", "lista1", "Reprovado", "2025-11-07")
    assert ok is False

# -------------------------------
# Testes para atualizar_status
# -------------------------------

def test_atualizar_status_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_status("id1", "Finalizado")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_status_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: None)
    ok, msg = atualizar_status("id1", "Finalizado")
    assert ok is False

# -------------------------------
# Testes para verificar_intencao_existente
# -------------------------------

def test_verificar_intencao_existente_true(monkeypatch):
    dummy_cursor = DummyCursor(rows=[(1,)])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: dummy_conexao)

    ok, msg = verificar_intencao_existente("doador1", "lista1")
    assert ok is True

def test_verificar_intencao_existente_false(monkeypatch):
    dummy_cursor = DummyCursor(rows=[(0,)])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: dummy_conexao)

    ok, msg = verificar_intencao_existente("doador1", "lista1")
    assert ok is False

def test_verificar_intencao_existente_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: None)
    ok, msg = verificar_intencao_existente("doador1", "lista1")
    assert ok is False

# -------------------------------
# Testes para deletar_intencao
# -------------------------------

def test_deletar_intencao_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_intencao("id1")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_deletar_intencao_nao_encontrada(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: dummy_conexao)

    ok, msg = deletar_intencao("id1")
    assert ok is False
    assert "não encontrada" in msg.lower()

def test_deletar_intencao_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.intencao_de_doacao.criar_conexao", lambda: None)
    ok, msg = deletar_intencao("id1")
    assert ok is False
