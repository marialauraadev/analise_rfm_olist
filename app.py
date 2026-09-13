import streamlit as st
import plotly.graph_objects as go
import os
import sys
sys.path.append('src')

from extract import extrair_dados
from scoring import gera_score
from segmentacao import gera_segmentacao

st.set_page_config(page_title="Análise RFM", page_icon="📊", layout="wide")

# definicao do estilo 
cor_segmento = {
    'Campeões': '#3987e5',
    'Clientes Leais': '#199e70',
    'Novos Clientes': '#9085e9',
    'Clientes em Risco': '#d95926',
    'Clientes Inativos': '#e66767',
    'Limbo': '#898781',
}
ordem_segmentos = list(cor_segmento.keys())

texto_secundario = '#c3c2b7'
grade = '#2c2c2a'
limite_perguntas = 10

# cada metrica guarda a coluna, o tipo de agregacao, o formato do rotulo e o nome do eixo
metricas = {
    'Número de clientes': ('customer_unique_id', 'nunique', '{:,.0f}', 'Clientes'),
    'Receita total': ('total_price_per_client', 'sum', 'R$ {:,.0f}', 'R$'),
    'Ticket médio': ('total_price_per_client', 'mean', 'R$ {:,.0f}', 'R$'),
    'Recência média': ('days_last_purchase', 'mean', '{:.0f} dias', 'Dias'),
    'Compras por cliente': ('total_purchases', 'mean', '{:.2f}', 'Compras'),
}


st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #1a1a19;
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 12px;
        padding: 18px 20px;
    }
    div[data-testid="stMetricLabel"] p {
        font-size: 0.8rem;
        color: #898781;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.9rem;
    }
    .cartao-segmento {
        background-color: #1a1a19;
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-left: 4px solid var(--cor-segmento);
        border-radius: 12px;
        padding: 16px 18px;
    }
    .cartao-segmento .rotulo {
        font-size: 0.8rem;
        color: #898781;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .cartao-segmento .valor {
        font-size: 1.9rem;
        font-weight: 600;
        color: var(--cor-segmento);
        line-height: 1.2;
    }
    .cartao-segmento .detalhe {
        font-size: 0.85rem;
        color: #c3c2b7;
    }
    </style>
""", unsafe_allow_html=True)


st.title("Análise RFM de Clientes - Olist")
st.markdown("Segmentação de clientes baseada em Recência, Frequência e Valor Monetário")


# rodando o pipeline inteiro de uma vez e guardando em cache pra nao consultar o banco a cada clique
@st.cache_data
def carregar_dados():
    df = extrair_dados()
    df = gera_score(df)
    df = gera_segmentacao(df)
    return df


# mandando só os números agregados porque a base inteira é bem grande
@st.cache_data
def resumo_para_ia(df):
    por_segmento = df.groupby('segmento').agg(
        clientes=('customer_unique_id', 'nunique'),
        receita_total=('total_price_per_client', 'sum'),
        ticket_medio=('total_price_per_client', 'mean'),
        recencia_media=('days_last_purchase', 'mean'),
        compras_media=('total_purchases', 'mean'),
    ).round(2)

    quartis_recencia = df['days_last_purchase'].describe().round(1)
    quartis_valor = df['total_price_per_client'].describe().round(2)

    return f"""
MÉTRICAS GERAIS
- Clientes únicos: {df['customer_unique_id'].nunique():,}
- Receita total: R$ {df['total_price_per_client'].sum():,.2f}
- Ticket médio: R$ {df['total_price_per_client'].mean():,.2f}

POR SEGMENTO
{por_segmento.to_string()}

DISTRIBUIÇÃO DE COMPRAS POR CLIENTE
{df['total_purchases'].value_counts().sort_index().to_string()}

DISTRIBUIÇÃO DE RECÊNCIA (dias desde a última compra)
{quartis_recencia.to_string()}

DISTRIBUIÇÃO DE VALOR GASTO POR CLIENTE (R$)
{quartis_valor.to_string()}

DISTRIBUIÇÃO DOS SCORES
R_score (1=mais antigo, 5=mais recente): {df['R_score'].value_counts().sort_index().to_dict()}
F_score (1, 3 ou 5 conforme faixa de nº de compras): {df['F_score'].value_counts().sort_index().to_dict()}
M_score (1=menor valor, 5=maior valor): {df['M_score'].value_counts().sort_index().to_dict()}

REGRAS DE SEGMENTAÇÃO
- Campeões: R>=4 e F=5 e M>=4
- Clientes em Risco: R entre 1 e 3, F>=3 e M>=4
- Clientes Leais: R>=4, F=3 e M>=3
- Novos Clientes: R>=4 e F=1
- Clientes Inativos: R entre 1 e 3 e F=1
- Limbo: não se encaixa em nenhuma regra acima
"""


# api do free tier do gemini para análise automatizada
def chave_gemini():
    try:
        return st.secrets['GEMINI_API_KEY']
    except Exception:
        return os.environ.get('GEMINI_API_KEY', '')


# deixando todos os graficos com a mesma cara, fundo transparente pra pegar o tema escuro do streamlit
def layout_padrao(fig, altura=420):
    fig.update_layout(
        height=altura,
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=texto_secundario,
        legend_title_text='Segmento',
    )
    fig.update_xaxes(gridcolor=grade, zeroline=False)
    fig.update_yaxes(gridcolor=grade, zeroline=False)
    return fig


df_rfm = carregar_dados()

# so mostrando os segmentos que realmente aparecem na base, mantendo a ordem que eu defini la em cima
segmentos_presentes = [s for s in ordem_segmentos if s in df_rfm['segmento'].unique()]

receita_total = df_rfm['total_price_per_client'].sum()

# esse numero é o mais chamativo da base, quase todo mundo comprou uma vez so
compra_unica = (df_rfm['total_purchases'] == 1).mean() * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Clientes", f"{df_rfm['customer_unique_id'].nunique():,}")
col2.metric("Receita Total", f"R$ {receita_total/1_000_000:,.2f} mi")
col3.metric("Ticket Médio", f"R$ {df_rfm['total_price_per_client'].mean():,.2f}")
col4.metric("Compraram uma só vez", f"{compra_unica:.1f}%")

st.markdown("")
st.markdown("**Concentração de receita por segmento**")

# os cards mostram receita e nao quantidade de cliente, que é o que o grafico de barras ja mostra
receita_segmento = (
    df_rfm.groupby('segmento')['total_price_per_client'].sum().sort_values(ascending=False)
)

colunas_receita = st.columns(3)

for posicao, (segmento, valor) in enumerate(receita_segmento.head(3).items()):
    percentual = valor / receita_total * 100
    colunas_receita[posicao].markdown(
        f"""<div class="cartao-segmento" style="--cor-segmento: {cor_segmento[segmento]}">
            <div class="rotulo">{posicao + 1}º · {segmento}</div>
            <div class="valor">{percentual:.1f}%</div>
            <div class="detalhe">R$ {valor:,.0f} da receita</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.divider()

aba_visao_geral, aba_segmentos, aba_explorar, aba_ia = st.tabs(
    ["Visão Geral", "Comparar Segmentos", "Explorar Clientes", "Perguntar à IA"]
)

with aba_visao_geral:
    st.subheader("Distribuição de Clientes por Segmento")
    st.caption("Quantidade de clientes em cada grupo: inativos, novos clientes, clientes leais, clientes em risco, campeões e limbo")

    contagem = df_rfm['segmento'].value_counts().reindex(segmentos_presentes).reset_index()
    contagem.columns = ['segmento', 'clientes']
    contagem['percentual'] = contagem['clientes'] / contagem['clientes'].sum() * 100
    contagem = contagem.sort_values('clientes', ascending=True)

    fig_dist = go.Figure()
    fig_dist.add_trace(go.Bar(
        x=contagem['clientes'],
        y=contagem['segmento'],
        orientation='h',
        marker_color=[cor_segmento[s] for s in contagem['segmento']],
        text=[f"{c:,} ({p:.1f}%)" for c, p in zip(contagem['clientes'], contagem['percentual'])],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>%{x:,} clientes<extra></extra>',
    ))
    # escala log porque inativos e novos clientes sao tao grandes que sumiam com os outros segmentos
    fig_dist.update_xaxes(title='Clientes (escala logarítmica)', type='log')
    fig_dist.update_yaxes(title='')
    layout_padrao(fig_dist, altura=380)
    st.plotly_chart(fig_dist, width='stretch')

    st.subheader("Distribuição de Frequência de Compras")
    st.caption("Quantidade de clientes por número total de compras realizadas")

    # juntando todo mundo de 4 compras pra cima porque de la pra frente sao pouquissimos clientes
    compras = df_rfm['total_purchases'].clip(upper=4).map(
        {1: '1 compra', 2: '2 compras', 3: '3 compras', 4: '4 ou mais'}
    )
    contagem_compras = compras.value_counts().reindex(['1 compra', '2 compras', '3 compras', '4 ou mais'])

    fig_freq = go.Figure()
    fig_freq.add_trace(go.Bar(
        x=contagem_compras.index,
        y=contagem_compras.values,
        marker_color=cor_segmento['Campeões'],
        text=[f"{v:,}" for v in contagem_compras.values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>%{y:,} clientes<extra></extra>',
    ))
    fig_freq.update_yaxes(title='Clientes', type='log')
    fig_freq.update_xaxes(title='')
    layout_padrao(fig_freq, altura=380)
    st.plotly_chart(fig_freq, width='stretch')

with aba_segmentos:
    st.subheader("Comparação Personalizada de Segmentos")

    coluna_metrica, coluna_ordem = st.columns([2, 1])
    metrica = coluna_metrica.selectbox("Métrica para comparar:", list(metricas))
    ordenacao = coluna_ordem.selectbox("Ordenar por:", ["Maior valor", "Menor valor", "Ordem dos segmentos"])

    escolhidos = st.multiselect(
        "Segmentos incluídos:",
        segmentos_presentes,
        default=segmentos_presentes,
    )

    if not escolhidos:
        st.info("Selecione ao menos um segmento para comparar.")
    else:
        # desmontando a tupla da metrica escolhida pra montar o grafico
        coluna, operacao, formato, titulo_eixo = metricas[metrica]
        comparacao = (
            df_rfm[df_rfm['segmento'].isin(escolhidos)]
            .groupby('segmento')[coluna]
            .agg(operacao)
            .reindex([s for s in segmentos_presentes if s in escolhidos])
        )

        if ordenacao == "Maior valor":
            comparacao = comparacao.sort_values(ascending=False)
        elif ordenacao == "Menor valor":
            comparacao = comparacao.sort_values(ascending=True)

        fig_comparacao = go.Figure()
        fig_comparacao.add_trace(go.Bar(
            x=comparacao.index,
            y=comparacao.values,
            # a cor segue o segmento e nao a posicao, senao o grafico se repinta toda vez que filtra
            marker_color=[cor_segmento[s] for s in comparacao.index],
            text=[formato.format(v) for v in comparacao.values],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' + metrica + ': %{y:,.2f}<extra></extra>',
        ))
        fig_comparacao.update_yaxes(title=titulo_eixo)
        fig_comparacao.update_xaxes(title='')
        layout_padrao(fig_comparacao, altura=420)
        st.plotly_chart(fig_comparacao, width='stretch')

        st.subheader("Comparação Geral de Segmentos")

        resumo = df_rfm[df_rfm['segmento'].isin(escolhidos)].groupby('segmento').agg(
            clientes=('customer_unique_id', 'nunique'),
            receita_total=('total_price_per_client', 'sum'),
            ticket_medio=('total_price_per_client', 'mean'),
            recencia_media=('days_last_purchase', 'mean'),
            compras_por_cliente=('total_purchases', 'mean'),
        ).reindex(comparacao.index)

        # renomeando depois do agg porque nome de coluna com espaco e acento nao funciona como parametro
        resumo.columns = ['Clientes', 'Receita Total (R$)', 'Ticket Médio (R$)', 'Recência Média (dias)', 'Compras por Cliente']

        st.dataframe(
            resumo.style.format({
                'Clientes': '{:,.0f}',
                'Receita Total (R$)': 'R$ {:,.2f}',
                'Ticket Médio (R$)': 'R$ {:,.2f}',
                'Recência Média (dias)': '{:.0f}',
                'Compras por Cliente': '{:.2f}',
            }),
            width='stretch',
        )

with aba_explorar:
    st.subheader("Explorar Clientes por Segmento")
    segmento_selecionado = st.selectbox("Escolha um segmento:", segmentos_presentes)
    df_filtrado = df_rfm[df_rfm['segmento'] == segmento_selecionado]

    st.caption(f"{len(df_filtrado):,} clientes neste segmento")

    # deixando o id do cliente de fora da tabela
    st.dataframe(
        df_filtrado[['days_last_purchase', 'total_purchases', 'total_price_per_client', 'RFM_score']]
        .rename(columns={
            'days_last_purchase': 'Dias desde a última compra',
            'total_purchases': 'Total de compras',
            'total_price_per_client': 'Valor gasto (R$)',
            'RFM_score': 'Score RFM',
        }),
        width='stretch',
        hide_index=True,
    )

with aba_ia:
    st.subheader("Pergunte sobre os dados")
    st.caption("Faça uma pergunta. Um modelo de linguagem interpreta os números da análise e fornece a resposta.")

    api_key = chave_gemini()
    perguntas_usadas = st.session_state.get('perguntas_ia', 0)

    if not api_key:
        st.warning(
            "Para ativar o assistente, configure a GEMINI_API_KEY no arquivo .streamlit/secrets.toml "
            "ou no painel de Secrets do Streamlit Cloud."
        )
    else:
        pergunta = st.text_area(
            "Sua pergunta",
            placeholder="Ex: qual segmento concentra mais receita e o que isso sugere para a estratégia?",
        )

        # limitando as perguntas por sessao pra uma pessoa so nao gastar a cota gratuita do dia inteiro
        if st.button("Analisar", disabled=not pergunta.strip()):
            if perguntas_usadas >= limite_perguntas:
                st.warning(f"Você atingiu o limite de {limite_perguntas} perguntas desta sessão.")
            else:
                with st.spinner("Analisando..."):
                    try:
                        from google import genai

                        cliente = genai.Client(api_key=api_key)
                        resposta = cliente.interactions.create(
                            model="gemini-3.8-flash",
                            system_instruction=(
                                "Você é um analista de dados respondendo sobre uma análise RFM da base da Olist. "
                                "Responda em português do Brasil, de forma objetiva, usando apenas os números fornecidos. "
                                "Se a informação necessária não estiver no contexto, diga isso claramente em vez de estimar."
                            ),
                            input=f"Contexto da análise:\n{resumo_para_ia(df_rfm)}\n\nPergunta: {pergunta}",
                        )
                        st.session_state['perguntas_ia'] = perguntas_usadas + 1
                        st.markdown(resposta.output_text.replace('$', '\\$'))
                    # tratando o estouro de cota separado pra nao aparecer erro pra quem ta visitando
                    except Exception as erro:
                        if 'RESOURCE_EXHAUSTED' in str(erro) or '429' in str(erro):
                            st.warning("O limite gratuito de perguntas do dia foi atingido. Tente novamente mais tarde.")
                        else:
                            # sem mostrar o texto do erro pro visitante pra nao expor detalhe interno do app
                            st.error("Não foi possível obter a resposta agora. Tente novamente em instantes.")
                            print(f"erro na chamada do gemini: {erro}")

        st.caption(f"Perguntas nesta sessão: {st.session_state.get('perguntas_ia', 0)}/{limite_perguntas}")
