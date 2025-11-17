import psycopg2
from psycopg2 import OperationalError, Error

# # Função de conexão DB hospedado no aws
# def criar_conexao():
#     try:
#         conexao = psycopg2.connect(
#             host="solidarihubdb.c1qqg6y2ayja.sa-east-1.rds.amazonaws.com",
#             port="5432",
#             user="postgres",        
#             password="020504",
#             database="SolidariHub"    
#         )
#         return conexao
#     except OperationalError:
#         return None
 
# Função de conexão com o banco de dados Local
def criar_conexao():
    try:
        # Estabelece conexão com o banco de dados PostgreSQL
        # Aqui estamos usando um banco local, então o host é 'localhost'
        conexao = psycopg2.connect(
            host="localhost",        # endereço do servidor local
            port="5432",             # porta padrão do PostgreSQL
            user="postgres",         # nome de usuário do banco
            password="1234",       # senha do usuário
            database="SolidariHub"   # nome do banco de dados local
        )
        return conexao  # retorna o objeto de conexão se tudo der certo
    except OperationalError:
        return None  # retorna None se ocorrer erro de conexão
