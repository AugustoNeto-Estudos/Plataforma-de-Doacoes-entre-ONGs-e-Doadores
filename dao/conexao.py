import psycopg2
import os
from psycopg2 import OperationalError, Error
from dotenv import load_dotenv

load_dotenv()

def criar_conexao():
    try:
        conexao = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conexao
    except OperationalError:
        return None