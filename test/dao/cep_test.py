import pytest
from dao.cep import buscar_endereco, carregar_ongs, ongs_ordenadas_por_distancia

# -------------------------------
# Testes para buscar_endereco
# -------------------------------

class MockResponse:
    def __init__(self, status_code=200, json_data=None, text="{}"):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self):
        return self._json_data


def test_buscar_endereco_valido(monkeypatch):
    """Simula um CEP válido retornado pela API ViaCEP"""
    def mock_get(url, timeout=5):
        return MockResponse(
            status_code=200,
            json_data={
                "logradouro": "Rua Ipiranga",
                "bairro": "Centro",
                "localidade": "Mogi das Cruzes",
                "uf": "SP"
            },
            text="ok"
        )
    monkeypatch.setattr("dao.cep.requests.get", mock_get)

    resultado = buscar_endereco("08710100")
    assert resultado is not None
    assert resultado["cep"] == "08710100"
    assert "Mogi das Cruzes" in resultado["endereco_completo"]


def test_buscar_endereco_invalido():
    """Simula CEP com menos de 8 dígitos"""
    resultado = buscar_endereco("123")
    assert resultado is None


def test_buscar_endereco_api_erro(monkeypatch):
    """Simula erro na API (status != 200)"""
    def mock_get(url, timeout=5):
        return MockResponse(status_code=500, text="erro")
    monkeypatch.setattr("dao.cep.requests.get", mock_get)

    resultado = buscar_endereco("08710100")
    assert resultado is None


def test_buscar_endereco_nao_encontrado(monkeypatch):
    """Simula resposta com 'erro' no JSON"""
    def mock_get(url, timeout=5):
        return MockResponse(status_code=200, json_data={"erro": True}, text="erro")
    monkeypatch.setattr("dao.cep.requests.get", mock_get)

    resultado = buscar_endereco("08710100")
    assert resultado is None


# -------------------------------
# Testes para carregar_ongs
# -------------------------------

class DummyCursor:
    def __init__(self, rows):
        self._rows = rows
    def execute(self, query): pass
    def fetchall(self): return self._rows
    def close(self): pass

class DummyConexao:
    def __init__(self, rows):
        self._rows = rows
    def cursor(self, cursor_factory=None): return DummyCursor(self._rows)
    def close(self): pass


def test_carregar_ongs_sucesso(monkeypatch):
    """Simula conexão retornando ONGs"""
    def mock_conexao():
        return DummyConexao([{"CNPJ_ID": "1", "nome": "ONG A", "cep": "08710100", "descricao": "Teste"}])
    monkeypatch.setattr("dao.cep.criar_conexao", mock_conexao)

    resultado = carregar_ongs()
    assert len(resultado) == 1
    assert resultado[0]["nome"] == "ONG A"


def test_carregar_ongs_sem_conexao(monkeypatch):
    """Simula falha na conexão"""
    def mock_conexao():
        return None
    monkeypatch.setattr("dao.cep.criar_conexao", mock_conexao)

    resultado = carregar_ongs()
    assert resultado == []


# -------------------------------
# Testes para ongs_ordenadas_por_distancia
# -------------------------------

def test_ongs_ordenadas_por_distancia(monkeypatch):
    """Testa ordenação por CEP"""
    def mock_carregar():
        return [
            {"CNPJ_ID": "1", "nome": "ONG A", "cep": "08710100", "descricao": "Teste"},
            {"CNPJ_ID": "2", "nome": "ONG B", "cep": "08710999", "descricao": "Teste"},
            {"CNPJ_ID": "3", "nome": "ONG C", "cep": "99999999", "descricao": "Teste"},
        ]
    monkeypatch.setattr("dao.cep.carregar_ongs", mock_carregar)

    resultado = ongs_ordenadas_por_distancia("08710100")
    nomes = [ong["nome"] for ong in resultado]

    # ONG A deve vir primeiro (CEP igual)
    assert nomes[0] == "ONG A"
    # ONG B deve vir em seguida (mesmo prefixo)
    assert "ONG B" in nomes
    # ONG C por último
    assert "ONG C" in nomes
