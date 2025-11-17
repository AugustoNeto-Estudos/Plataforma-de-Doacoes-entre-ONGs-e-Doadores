import pytest
from dao.feedback import (
    criar_feedback,
    listar_feedbacks,
    buscar_feedbacks_por_ong,
    buscar_feedbacks_por_doador,
    buscar_feedbacks_por_pedido,
    buscar_feedbacks_por_lista,
    atualizar_feedback,
    deletar_feedback,
)

# -------------------------------
# Mock de conexão e cursor
# -------------------------------

class DummyCursor:
    def __init__(self, rows=None):
        self._rows = rows or []
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
# Testes para criar_feedback
# -------------------------------

def test_criar_feedback_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.feedback.criar_conexao", lambda: dummy_conexao)

    ok = criar_feedback(1, 2, 3, 4, 5, "boa", "comentário")
    assert ok is True

def test_criar_feedback_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.feedback.criar_conexao", lambda: None)
    ok = criar_feedback(1, 2, 3, 4, 5, "boa", "comentário")
    assert ok is False

# -------------------------------
# Testes para listar_feedbacks
# -------------------------------

def test_listar_feedbacks_sucesso(monkeypatch):
    rows = [{"id_feedback": 1, "nome": "Doador"}]
    dummy_cursor = DummyCursor(rows=rows)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.feedback.criar_conexao", lambda: dummy_conexao)

    resultado = listar_feedbacks()
    assert len(resultado) == 1
    assert resultado[0]["nome"] == "Doador"

def test_listar_feedbacks_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.feedback.criar_conexao", lambda: None)
    resultado = listar_feedbacks()
    assert resultado == []

# -------------------------------
# Testes para buscar_feedbacks_por_ong
# -------------------------------

def test_buscar_feedbacks_por_ong(monkeypatch):
    rows = [{"id_feedback": 1, "id_ong": 10, "nome": "ONG"}]
    dummy_cursor = DummyCursor(rows=rows)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.feedback.criar_conexao", lambda: dummy_conexao)

    resultado = buscar_feedbacks_por_ong(10)
    assert resultado[0]["id_ong"] == 10

# -------------------------------
# Testes para buscar_feedbacks_por_doador
# -------------------------------

def test_buscar_feedbacks_por_doador(monkeypatch):
    rows = [{"id_feedback": 1, "id_doador": 20, "nome": "Doador"}]
    dummy_cursor = DummyCursor(rows=rows)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.feedback.criar_conexao", lambda: dummy_conexao)

    resultado = buscar_feedbacks_por_doador(20)
    assert resultado[0]["id_doador"] == 20

# -------------------------------
# Testes para buscar_feedbacks_por_pedido
# -------------------------------

def test_buscar_feedbacks_por_pedido(monkeypatch):
    rows = [{"id_feedback": 1, "id_pedido": 30, "nome": "Pedido"}]
    dummy_cursor = DummyCursor(rows=rows)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.feedback.criar_conexao", lambda: dummy_conexao)

    resultado = buscar_feedbacks_por_pedido(30)
    assert resultado[0]["id_pedido"] == 30

# -------------------------------
# Testes para buscar_feedbacks_por_lista
# -------------------------------

def test_buscar_feedbacks_por_lista(monkeypatch):
    rows = [{"id_feedback": 1, "id_lista": 40, "nome_doador": "Doador"}]
    dummy_cursor = DummyCursor(rows=rows)
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.feedback.criar_conexao", lambda: dummy_conexao)

    resultado = buscar_feedbacks_por_lista(40)
    assert resultado[0]["id_lista"] == 40

# -------------------------------
# Testes para atualizar_feedback
# -------------------------------

def test_atualizar_feedback_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.feedback.criar_conexao", lambda: dummy_conexao)

    ok = atualizar_feedback(1, 5, "boa", "comentário")
    assert ok is True

def test_atualizar_feedback_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.feedback.criar_conexao", lambda: None)
    ok = atualizar_feedback(1, 5, "boa", "comentário")
    assert ok is False

# -------------------------------
# Testes para deletar_feedback
# -------------------------------

def test_deletar_feedback_sucesso(monkeypatch):
    dummy_cursor = DummyCursor()
    dummy_conexao = DummyConexao(dummy_cursor)
    monkeypatch.setattr("dao.feedback.criar_conexao", lambda: dummy_conexao)

    ok = deletar_feedback(1)
    assert ok is True

def test_deletar_feedback_sem_conexao(monkeypatch):
    monkeypatch.setattr("dao.feedback.criar_conexao", lambda: None)
    ok = deletar_feedback(1)
    assert ok is False
