import pandas as pd
import sqlite3

conexao = sqlite3.connect('dados.db')

with open("sql/analise_rfm.sql", "r") as analise_rfm:
    query = analise_rfm.read()

df_rfm = pd.read_sql_query(query, conexao)

conexao.close()

df_rfm['R_score'] = pd.qcut(df_rfm['days_last_purchase'], 5, labels=[5, 4, 3, 2, 1])

# utilizando cut pelo erro no cálculo dos limites que deram o mesmo valor (maioria das compras tinha total 1)
df_rfm['F_score'] = pd.cut(df_rfm['total_purchases'], bins=[0, 3, 6, 15], labels=[1, 3, 5])

df_rfm['M_score'] = pd.qcut(df_rfm['total_price_per_client'], 5, labels=[1, 2, 3, 4, 5])