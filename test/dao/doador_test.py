import pytest
from dao.doador import (
    hash_senha,
    cadastrar_doador,
    listar_doadores,
    atualizar_status_doador,
    doador_esta_ativo,
    excluir_doador,
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
# Testes para hash_senha
# -------------------------------

def test_hash_senha(monkeypatch):
    def fake_hashpw(pw, salt):
        return b"hashed_password"
    def fake_gensalt(): return b"salt"
    monkeypatch.setattr("dao.doador.bcrypt.hashpw", fake_hashpw)
    monkeypatch.setattr("dao.doador.bcrypt.gensalt", fake_gensalt)

    resultado = hash_senha("1234")
    assert resultado == "hashed_password"

# -------------------------------
# Testes para cadastrar_doador
# -------------------------------

def test_cadastrar_doador_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)

    monkeypatch.setattr("dao.doador.criar_conexao", lambda: dummy_conexao)

    ok, msg = cadastrar_doador("111", "Nome", "email@test.com", "9999", "senha", 1, "cargo")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_cadastrar_doador_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.doador.criar_conexao", lambda: None)
    ok, msg = cadastrar_doador("111", "Nome", "email@test.com", "9999", "senha", 1, "cargo")
    assert ok is False

# -------------------------------
# Testes para listar_doadores
# -------------------------------

def test_listar_doadores_sucesso(monkeypatch):
    colunas = ["CPF_ID", "nome", "email", "senha"]
    registros = [("111", "Nome", "EMAIL@TEST.COM", " senha\n")]
    dummy_cursor = DummyCursor(rows=registros, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)

    monkeypatch.setattr("dao.doador.criar_conexao", lambda: dummy_conexao)

    resultado = listar_doadores()
    assert len(resultado) == 1
    assert resultado[0]["email"] == "email@test.com"
    assert resultado[0]["senha"] == "senha"

def test_listar_doadores_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.doador.criar_conexao", lambda: None)
    resultado = listar_doadores()
    assert resultado == []

# -------------------------------
# Testes para atualizar_status_doador
# -------------------------------

def test_atualizar_status_doador_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.doador.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_status_doador("111", 1)
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_status_doador_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.doador.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_status_doador("111", 1)
    assert ok is False
    assert "não encontrado" in msg.lower()

# -------------------------------
# Testes para doador_esta_ativo
# -------------------------------

def test_doador_esta_ativo_true(monkeypatch):
    dummy_cursor = DummyCursor(rows=[(1,)])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.doador.criar_conexao", lambda: dummy_conexao)

    assert doador_esta_ativo("email@test.com") is True

def test_doador_esta_ativo_false(monkeypatch):
    dummy_cursor = DummyCursor(rows=[(0,)])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.doador.criar_conexao", lambda: dummy_conexao)

    assert doador_esta_ativo("email@test.com") is False

def test_doador_esta_ativo_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.doador.criar_conexao", lambda: None)
    assert doador_esta_ativo("email@test.com") is False

# -------------------------------
# Testes para excluir_doador
# -------------------------------

def test_excluir_doador_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.doador.criar_conexao", lambda: dummy_conexao)

    ok, msg = excluir_doador("111")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_excluir_doador_nao_encontrado(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.doador.criar_conexao", lambda: dummy_conexao)

    ok, msg = excluir_doador("111")
    assert ok is False
    assert "não encontrado" in msg.lower()
