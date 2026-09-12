import pandas as pd
import sqlite3

conexao = sqlite3.connect('dados.db')

with open("sql/analise_rfm.sql", "r") as analise_rfm:
    query = analise_rfm.read()

df_rfm = pd.read_sql_query(query, conexao)

conexao.close()

df_rfm['R_score'] = pd.qcut(df_rfm['days_last_purchase'], 5, labels=[5, 4, 3, 2, 1])