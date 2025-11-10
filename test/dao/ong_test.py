import pytest
from dao.ong import (
    hash_senha,
    cadastrar_ong,
    listar_ongs,
    buscar_ong_por_id,
    atualizar_status_ong,
    atualizar_status_verificacao_ong,
    ong_esta_ativa,
    excluir_ong,
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
# Testes para hash_senha
# -------------------------------

def test_hash_senha(monkeypatch):
    def fake_hashpw(pw, salt): return b"hashed_password"
    def fake_gensalt(): return b"salt"
    monkeypatch.setattr("dao.ong.bcrypt.hashpw", fake_hashpw)
    monkeypatch.setattr("dao.ong.bcrypt.gensalt", fake_gensalt)

    resultado = hash_senha("1234")
    assert resultado == "hashed_password"

# -------------------------------
# Testes para cadastrar_ong
# -------------------------------

def test_cadastrar_ong_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: dummy_conexao)

    ok, msg = cadastrar_ong("CNPJ1", "ONG1", "12345", "9999", "email@test.com", "senha", 1, 1, "desc", "cargo")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_cadastrar_ong_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: None)
    ok, msg = cadastrar_ong("CNPJ1", "ONG1", "12345", "9999", "email@test.com", "senha", 1, 1, "desc", "cargo")
    assert ok is False

# -------------------------------
# Testes para listar_ongs
# -------------------------------

def test_listar_ongs_sucesso(monkeypatch):
    colunas = ["CNPJ_ID", "nome", "email", "senha"]
    registros = [("CNPJ1", "ONG1", "EMAIL@TEST.COM", " senha\n")]
    dummy_cursor = DummyCursor(rows=registros, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: dummy_conexao)

    resultado = listar_ongs()
    assert len(resultado) == 1
    assert resultado[0]["email"] == "email@test.com"
    assert resultado[0]["senha"] == "senha"

def test_listar_ongs_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: None)
    resultado = listar_ongs()
    assert resultado == []

# -------------------------------
# Testes para buscar_ong_por_id
# -------------------------------

def test_buscar_ong_por_id_sucesso(monkeypatch):
    colunas = ["CNPJ_ID", "nome", "email"]
    registro = ("CNPJ1", "ONG1", "email@test.com")
    dummy_cursor = DummyCursor(registro=registro, description=[(c,) for c in colunas])
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: dummy_conexao)

    resultado = buscar_ong_por_id("CNPJ1")
    assert resultado["CNPJ_ID"] == "CNPJ1"

def test_buscar_ong_por_id_nao_encontrada(monkeypatch):
    dummy_cursor = DummyCursor(registro=None)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: dummy_conexao)

    resultado = buscar_ong_por_id("CNPJX")
    assert resultado is None

def test_buscar_ong_por_id_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: None)
    resultado = buscar_ong_por_id("CNPJ1")
    assert resultado is None

# -------------------------------
# Testes para atualizar_status_ong
# -------------------------------

def test_atualizar_status_ong_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_status_ong("CNPJ1", 1)
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_status_ong_nao_encontrada(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_status_ong("CNPJ1", 1)
    assert ok is False
    assert "não encontrada" in msg.lower()

def test_atualizar_status_ong_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: None)
    ok, msg = atualizar_status_ong("CNPJ1", 1)
    assert ok is False

# -------------------------------
# Testes para atualizar_status_verificacao_ong
# -------------------------------

def test_atualizar_status_verificacao_ong_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_status_verificacao_ong("CNPJ1", 1)
    assert ok is True
    assert "sucesso" in msg.lower()

def test_atualizar_status_verificacao_ong_nao_encontrada(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: dummy_conexao)

    ok, msg = atualizar_status_verificacao_ong("CNPJ1", 1)
    assert ok is False
    assert "não encontrada" in msg.lower()

def test_atualizar_status_verificacao_ong_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: None)
    ok, msg = atualizar_status_verificacao_ong("CNPJ1", 1)
    assert ok is False

# -------------------------------
# Testes para ong_esta_ativa
# -------------------------------

def test_ong_esta_ativa_true(monkeypatch):
    dummy_cursor = DummyCursor(registro=(1,))
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: dummy_conexao)

    assert ong_esta_ativa("email@test.com") is True

def test_ong_esta_ativa_false(monkeypatch):
    dummy_cursor = DummyCursor(registro=(0,))
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: dummy_conexao)

    assert ong_esta_ativa("email@test.com") is False

def test_ong_esta_ativa_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: None)
    assert ong_esta_ativa("email@test.com") is False

# -------------------------------
# Testes para excluir_ong
# -------------------------------

def test_excluir_ong_sucesso(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=1)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: dummy_conexao)

    ok, msg = excluir_ong("CNPJ1")
    assert ok is True
    assert "sucesso" in msg.lower()

def test_excluir_ong_nao_encontrada(monkeypatch):
    dummy_cursor = DummyCursor(rowcount=0)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: dummy_conexao)

    ok, msg = excluir_ong("CNPJ1")
    assert ok is False
    assert "não encontrada" in msg.lower()

def test_excluir_ong_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.ong.criar_conexao", lambda: None)
    ok, msg = excluir_ong("CNPJ1")
    assert ok is False
