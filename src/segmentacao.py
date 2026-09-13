import numpy as np

def gera_segmentacao(df_rfm):
    agrupamentos = [
        (df_rfm['R_score'] >= 4) & (df_rfm['F_score'] == 5) & (df_rfm['M_score'] >= 4),
        (df_rfm['R_score'] >= 1) & (df_rfm['R_score'] <= 3) & (df_rfm['F_score'] >= 3) & (df_rfm['M_score'] >= 4),
        (df_rfm['R_score'] >= 4) & (df_rfm['F_score'] == 3) & (df_rfm['M_score'] >= 3),
        (df_rfm['R_score'] >= 4) & (df_rfm['F_score'] == 1) & (df_rfm['M_score'] >= 4),
        (df_rfm['R_score'] >= 4) & (df_rfm['F_score'] == 1) & (df_rfm['M_score'] <= 3),
        (df_rfm['R_score'] >= 1) & (df_rfm['R_score'] <= 3) & (df_rfm['F_score'] == 1) & (df_rfm['M_score'] >= 4),
        (df_rfm['R_score'] >= 1) & (df_rfm['R_score'] <= 3) & (df_rfm['F_score'] == 1) & (df_rfm['M_score'] <= 3)
    ]

    classificacoes = [
        'Campeões',
        'Clientes em Risco',
        'Clientes Leais',
        'Novos Clientes - Alto Valor',
        'Novos Clientes',
        'Clientes Inativos - Alto Valor',
        'Clientes Inativos'
    ]

    df_rfm['segmento'] = np.select(agrupamentos, classificacoes, default='Limbo')
    return df_rfm