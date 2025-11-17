import requests
import re
from dao.conexao import criar_conexao
from psycopg2.extras import RealDictCursor

def buscar_endereco(cep):
    # Remove caracteres não numéricos
    cep = re.sub(r'\D', '', cep)
    print(f"[LOG] CEP limpo para consulta: {cep}")

    # Valida tamanho do CEP
    if len(cep) != 8:
        print("CEP inválido: não possui 8 dígitos.")
        return None

    try:
        # Consulta API ViaCEP
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
        print(f"[LOG] Status da requisição: {response.status_code}")
        print("[LOG] Conteúdo bruto:", response.text)

        if response.status_code != 200:
            print("Falha na requisição ao ViaCEP.")
            return None

        dados = response.json()
        print(f"[LOG] Dados recebidos: {dados}")

        if "erro" in dados:
            print("CEP não encontrado:", dados)
            return None

        # Monta endereço completo
        endereco_str = ', '.join([p for p in [
            dados.get('logradouro', ''),
            dados.get('bairro', ''),
            dados.get('localidade', ''),
            dados.get('uf', ''),
            'Brasil'
        ] if p])

        print("[LOG] Endereço formatado:", endereco_str)

        return {
            "cep": cep,
            "cidade": dados.get("localidade", ""),
            "bairro": dados.get("bairro", ""),
            "endereco_completo": endereco_str
        }

    except Exception as e:
        print("Exceção ao buscar endereço:", str(e))
        return None


def carregar_ongs():
    # Carrega ONGs do banco
    conexao = criar_conexao()
    if not conexao:
        return []
    try:
        cur = conexao.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT "CNPJ_ID", nome, cep, descricao FROM ong;')
        rows = cur.fetchall()
        cur.close()
        conexao.close()
        return rows
    except Exception:
        return []


def ongs_ordenadas_por_distancia(cep_usuario):
    # Ordena ONGs por proximidade do CEP
    ongs = carregar_ongs()
    resultados = []
    for ong in ongs:
        pontuacao = 4
        if ong["cep"] and ong["cep"] == cep_usuario:
            pontuacao = 0
        elif ong["cep"] and ong["cep"][:5] == cep_usuario[:5]:
            pontuacao = 1
        resultados.append((ong, pontuacao))
    resultados.sort(key=lambda x: x[1])
    return [ong for ong, _ in resultados]
