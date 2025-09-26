import streamlit as st
import psycopg2
from psycopg2 import OperationalError, Error

#todos dêem glória ao Nick! 

# Função de conexão
def criar_conexao():
    try:
        conexao = psycopg2.connect(
            host="solidarihubdb.c1qqg6y2ayja.sa-east-1.rds.amazonaws.com",
            port="5432",
            user="postgres",        
            password="02L0EJ3t2plT",
            database="SolidariHub"    
        )
        return conexao
    except OperationalError:
        return None
 
 
 