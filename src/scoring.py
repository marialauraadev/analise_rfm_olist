import pandas as pd
from extract import extrair_dados

def gera_score(df_rfm):
    # transformando R score para int por conta da ordem de posição lista de labels (pandas entendendo que 5 seria a categoria mais baixa e 1 a mais alta)
    df_rfm['R_score'] = pd.qcut(df_rfm['days_last_purchase'], 5, labels=[5, 4, 3, 2, 1])
    df_rfm['R_score'] = df_rfm['R_score'].astype('int')

    # utilizando cut pelo erro no cálculo dos limites que deram o mesmo valor (maioria das compras tinha total 1)
    df_rfm['F_score'] = pd.cut(df_rfm['total_purchases'], bins=[0, 3, 6, 15], labels=[1, 3, 5])

    df_rfm['M_score'] = pd.qcut(df_rfm['total_price_per_client'], 5, labels=[1, 2, 3, 4, 5])

    # utilizando colunas em string pra poder preservar as colunas originais caso seja necessário fazer alguma conta depois
    df_rfm['R_score_str'] = df_rfm['R_score'].astype('string')
    df_rfm['F_score_str'] = df_rfm['F_score'].astype('string')
    df_rfm['M_score_str'] = df_rfm['M_score'].astype('string')

    df_rfm['RFM_score'] = df_rfm['R_score_str'] + df_rfm['F_score_str'] + df_rfm['M_score_str']
    return df_rfm