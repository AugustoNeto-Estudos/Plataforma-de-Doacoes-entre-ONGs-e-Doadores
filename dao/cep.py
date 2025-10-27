import requests
import re
from dao.conexao import criar_conexao
from psycopg2.extras import RealDictCursor


#Antiga versão
# def buscar_endereco(cep):
#     cep = re.sub(r'\D', '', cep)
#     if len(cep) != 8:
#         return None
#     try:
#         response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
#         if response.status_code != 200:
#             return None
#         dados = response.json()
#         if "erro" in dados:
#             return None
#         endereco_str = ', '.join([p for p in [
#             dados.get('logradouro', ''),
#             dados.get('bairro', ''),
#             dados.get('localidade', ''),
#             dados.get('uf', ''),
#             'Brasil'
#         ] if p])
#         return {
#             "cep": cep,
#             "cidade": dados.get("localidade", ""),
#             "bairro": dados.get("bairro", ""),
#             "endereco_completo": endereco_str
#         }
#     except:
#         return None

#DEPURAÇÃO
import requests
import re

def buscar_endereco(cep):
    cep = re.sub(r'\D', '', cep)
    print(f"[LOG] CEP limpo para consulta: {cep}")

    if len(cep) != 8:
        print("❌ CEP inválido: não possui 8 dígitos.")
        return None

    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
        print(f"🔎 Requisição para ViaCEP: status {response.status_code}")
        print("📦 Conteúdo bruto da resposta:", response.text)

        if response.status_code != 200:
            print("❌ Falha na requisição ao ViaCEP.")
            return None

        dados = response.json()
        print(f"[LOG] Dados recebidos do ViaCEP: {dados}")

        if "erro" in dados:
            print("❌ CEP não encontrado no ViaCEP:", dados)
            return None

        endereco_str = ', '.join([p for p in [
            dados.get('logradouro', ''),
            dados.get('bairro', ''),
            dados.get('localidade', ''),
            dados.get('uf', ''),
            'Brasil'
        ] if p])

        print("📍 Endereço formatado:", endereco_str)

        return {
            "cep": cep,
            "cidade": dados.get("localidade", ""),
            "bairro": dados.get("bairro", ""),
            "endereco_completo": endereco_str
        }

    except Exception as e:
        print("❌ Exceção ao buscar endereço:", str(e))
        return None

def carregar_ongs():
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
