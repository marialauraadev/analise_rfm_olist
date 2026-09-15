import sqlite3
import pandas as pd
import os

def extrair_dados():
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_raiz = os.path.dirname(pasta_atual)

    caminho_db = os.path.join(pasta_raiz, 'sql', 'dados.db')
    caminho_query = os.path.join(pasta_raiz, 'sql', 'analise_rfm.sql')

    conexao = sqlite3.connect(caminho_db)

    with open(caminho_query, "r") as analise_rfm:
        query = analise_rfm.read()

    df_rfm = pd.read_sql_query(query, conexao)

    conexao.close()
    return df_rfm