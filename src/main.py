from extract import extrair_dados
from scoring import gera_score
from segmentacao import gera_segmentacao

df_rfm = extrair_dados()

df_rfm = gera_score(df_rfm)

df_rfm = gera_segmentacao(df_rfm)