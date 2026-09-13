import sqlite3
import pandas as pd

def extrair_dados():
    conexao = sqlite3.connect('sql/dados.db')

    with open("sql/analise_rfm.sql", "r") as analise_rfm:
        query = analise_rfm.read()

    df_rfm = pd.read_sql_query(query, conexao)

    conexao.close()
    return df_rfm