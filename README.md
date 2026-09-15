# Análise RFM de Clientes — Olist

Segmentação de clientes de um e-commerce brasileiro usando a metodologia RFM (Recência, Frequência, Monetário), do modelo do banco de dados até um dashboard interativo publicado.

🔗 **[Acessar o dashboard](https://segmentacaorfmolist.streamlit.app/)** · 🗂️ Dataset: [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

---

## Índice

- [Sobre o projeto](#sobre-o-projeto)
- [O que é RFM](#o-que-é-rfm)
- [Sobre os dados](#sobre-os-dados)
- [Pipeline do projeto](#pipeline-do-projeto)
- [Desafios técnicos e decisões](#desafios-técnicos-e-decisões)
- [Resultados](#resultados)
- [Limitações](#limitações)
- [Próximos passos](#próximos-passos)
- [Stack utilizada](#stack-utilizada)
- [Como rodar o projeto](#como-rodar-o-projeto)
- [Fontes](#fontes)

---

## Sobre o projeto

Este projeto nasceu como um exercício de portfólio para praticar dois blocos de habilidades separados: **engenharia de dados** (modelagem relacional, SQL, validação de pipeline) e **análise de dados** (Python, segmentação estatística, visualização). A escolha do RFM como tema veio a partir de pesquisas e da vontade de trabalhar com uma técnica clássica de marketing que é, ao mesmo tempo, simples de explicar e rica o suficiente para gerar decisões reais de negócio. 

O projeto usa dados reais e anônimos de pedidos feitos na **Olist**, uma plataforma brasileira que conecta pequenos e médios lojistas a grandes marketplaces (Mercado Livre, Americanas, Magalu, entre outros).

> **Nota sobre a data dos dados**: este projeto utiliza dados históricos (2016–2018) para fins de prática de segmentação de clientes. A metodologia RFM é atemporal e aplicável a qualquer período de dados transacionais. O objetivo aqui é demonstrar o raciocínio e a técnica, e posteriormente desenvolver análises ao longo dos anos seguintes para entender o comportamento do mercado.

## O que é RFM

RFM é uma técnica de segmentação de clientes baseada em três métricas de comportamento de compra:

- Recência (R): há quanto tempo o cliente comprou pela última vez
- Frequência (F): quantas vezes o cliente comprou em um período
- Monetário (M): quanto o cliente gastou no total

A lógica por trás é simples: um cliente que comprou recentemente, compra com frequência e gasta bastante vale mais para o negócio do que alguém que comprou uma vez há muito tempo.

### Por que RFM

Existem várias formas de segmentar clientes e cada uma responde a uma pergunta diferente:

- Segmentação demográfica (idade, gênero, escolaridade) e psicográfica (valores, personalidade, estilo de vida) tentam entender quem o cliente é.
- Análise de coorte agrupa clientes por características em comum para acompanhar como diferentes grupos se comportam ao longo do tempo. Ela olha para múltiplos fatores em conjunto, não para uma métrica isolada.
- RFM foca em como o cliente compra, não em quem ele é. Isso torna a segmentação mais "palpável" para decisões de marketing: não importa a idade ou o perfil psicológico do cliente, importa se ele está comprando ou sumiu.

Em negócios onde a métrica principal não é a compra em si, como em aplicativos e plataformas de conteúdo, essa mesma lógica é adaptada para RFE (Recência, Frequência, Engajamento).

### Por que isso importa para o negócio

RFM ajuda a responder perguntas centrais de qualquer operação de e-commerce:

- Quem são os melhores clientes?
- Quais clientes estão em risco de abandono (churn)?
- Quem tem potencial de se tornar mais valioso?
- Quem pode ser retido de forma eficaz?
- Quem tem mais chance de responder a uma campanha de reengajamento?

Ao responder essas perguntas, uma empresa consegue: identificar e cultivar clientes de alto valor, priorizar estratégias de reengajamento onde elas realmente importam e encontrar oportunidades de upsell/cross-sell com base em comportamento real, não em suposição.

## Sobre os dados

O dataset da Olist é composto por várias tabelas relacionadas: pedidos, itens, produtos, clientes, pagamentos, avaliações, vendedores. Para este projeto, o escopo foi reduzido: apenas as tabelas essenciais para calcular RFM foram trazidas para o banco: `customers`, `orders`, `order_items` e `products`.

### A armadilha do `customer_id` vs `customer_unique_id`

Um dos primeiros pontos de atenção no dataset é como ele identifica clientes:

> *"Each order is assigned to a unique customer_id. This means that the same customer will get different ids for different orders. The purpose of having a customer_unique_id on the dataset is to allow you to identify customers that made repurchases at the store."*

Ou seja: `customer_id` muda a cada pedido e usar esse campo para agrupar compras faria cada pedido parecer um cliente diferente, quebrando completamente a lógica de Frequência do RFM. O campo correto para identificar a pessoa ao longo do tempo é `customer_unique_id`.

### Por que a Olist é "uma empresa só", mas os clientes não recompram

A Olist não é uma loja com identidade própria para o consumidor final. Ela é a infraestrutura por trás de milhares de lojistas vendendo em marketplaces como Mercado Livre e Americanas. Um cliente compra pensando que está comprando do Mercado Livre, sem saber que a Olist existe. Isso ajuda a explicar um padrão que chamou atenção durante a análise: a esmagadora maioria dos clientes comprou uma única vez. Sem uma marca visível para criar lealdade, e considerando que boa parte das categorias vendidas (móveis, eletrônicos, decoração) não são de recompra frequente, essa baixa taxa de recompra é esperada e acaba sendo um dos principais achados da análise.

### Estrutura do banco de dados

O projeto usa SQLite (escolhido para praticar SQL de verdade, em vez de resolver tudo com `merge()` do pandas). O schema relaciona as 4 tabelas por chave estrangeira, com `order_items` usando uma chave primária composta (`order_id` + `order_item_id`), já que um pedido pode ter múltiplos itens.

O schema completo está em [`sql/schema.sql`](sql/schema.sql) ou em (https://dbdiagram.io/d/analise_rfm-6aa2018b70fd27e3c7635a62).

## Pipeline do projeto

```
1. Modelagem e criação do banco (SQLite)
2. Importação dos CSVs para as tabelas
3. Query SQL: extração e agregação por cliente (Recência, Frequência, Monetário brutos)
4. Validação da query (3 níveis de teste, ver abaixo)
5. Python: cálculo dos scores (1-5) e segmentação
6. Visualização exploratória (matplotlib/plotly)
7. Dashboard interativo (Streamlit)
```

### A query RFM, em resumo

A query final ([`sql/analise_rfm.sql`](sql/analise_rfm.sql)) segue esta lógica:

1. Filtra apenas pedidos com status `delivered` para medir comportamento de compra real, não intenções ou pedidos cancelados/não concluídos
2. Agrupa `order_items` por `order_id`, somando o preço dos produtos (sem frete). Isso é necessário porque cada item de um pedido ocupa uma linha própria na tabela
3. Calcula a Recência como a distância, em dias, entre a data da última compra do cliente e a data mais recente presente em todo o dataset
4. Agrupa tudo por `customer_unique_id`, obtendo Recência (mínima), Frequência (contagem de pedidos) e Monetário (soma do valor)

**Por que o frete fica fora do cálculo do Monetário**: frete é um custo logístico de entrega e varia por distância e peso do produto, não pelo quanto o cliente valoriza a compra. Por isso, `payment_value` (que inclui frete) não foi usado. O valor do Monetário vem da soma de `order_items.price`.

### Validação da query

Antes de confiar no resultado, a query foi validada em três frentes (validação na pasta `sql/validacao`):

1. Teste pontual: um cliente com poucos pedidos, conferido manualmente linha por linha
2. Teste de estresse: um cliente com 15 pedidos (o maior volume da base), para garantir que o JOIN não duplicava linhas em escala
3. Conservação de totais: a soma de todo o Monetário calculado pela query RFM foi comparada com a soma bruta de `order_items.price` (filtrada por `delivered`), calculada de forma totalmente independente. Os dois caminhos bateram exatamente: R$ 13.221.498,11

## Desafios técnicos e decisões

Esta seção documenta os principais obstáculos encontrados porque o processo de resolvê-los foi tão parte do aprendizado quanto o resultado final.

### Fan-out no JOIN entre pedidos e datas

Ao juntar duas tabelas intermediárias (uma com o valor por pedido, outra com a recência por pedido) usando apenas `customer_id` como chave de junção, cada linha de uma tabela "casava" com todas as linhas correspondentes da outra, multiplicando artificialmente o número de pedidos de clientes com mais de uma compra. A correção foi juntar as tabelas por `customer_id` e `order_id` simultaneamente, garantindo que cada linha só case com seu par exato.

### Frequência extremamente concentrada

A tentativa inicial de dividir a Frequência em quintis (`pd.qcut`, como foi feito com Recência e Monetário) falhou: como a maioria esmagadora dos clientes tem exatamente 1 compra, os limites calculados para os 5 grupos colapsavam no mesmo valor. A solução foi trocar por `pd.cut` com faixas definidas manualmente (1–3, 4–6, 7–15 compras), mapeadas para os scores 1, 3 e 5.

### Ordem categórica invertida no score de Recência

Um bug sutil: ao criar o score de Recência com `pd.qcut(..., labels=[5, 4, 3, 2, 1])` (invertido de propósito, já que menos dias = melhor), o pandas passou a tratar a ordem da lista de labels como a ordem de comparação, não o valor numérico. Na prática, comparações como `R_score >= 4` passaram a excluir silenciosamente os clientes com `R_score = 5` (o melhor valor), porque `5` aparecia antes de `4` na lista de labels. O bug não gerava nenhum erro, só um resultado incorreto, descoberto porque a quantidade de clientes numa categoria "genérica" (chamada internamente de Limbo) estava desproporcionalmente alta. A correção foi converter a coluna para um tipo numérico inteiro logo após sua criação, eliminando a ambiguidade categórica.

### Regras de segmentação e cobertura de 100% dos clientes

As regras de segmentação foram construídas para cobrir toda a base, não só os padrões ideais. Isso expôs combinações de score que não se encaixavam em nenhuma categoria inicialmente prevista, por exemplo recência baixa combinada com frequência média, o que levou à criação de uma categoria adicional (Clientes Inativos) e ao ajuste fino da regra de Clientes em Risco. Ao final, restaram apenas 3 clientes (0,003% da base) em uma categoria de exceção, documentados como tal em vez de forçados em uma regra artificial.

### Segmentação pouco granular para 97% da base

Uma primeira versão da segmentação, embora tecnicamente correta, tinha um problema prático: como cerca de 97% da base tem `F_score == 1` (compraram uma única vez), os segmentos Novos Clientes e Clientes Inativos, diferenciados apenas pela Recência, concentravam quase toda a base sozinhos, deixando o Monetário sem nenhum papel na segmentação da maioria dos clientes. Um cliente que gastou R$ 5 numa única compra e outro que gastou R$ 2.000 numa única compra caíam no mesmo segmento.

A correção foi subdividir esses dois grupos por Monetário, criando "Novos Clientes - Alto Valor" e "Clientes Inativos - Alto Valor" (`M_score >= 4`, ou seja, top 40% em valor gasto). O resultado passou de 2 segmentos concentrando quase 100% da base para 4 segmentos de peso comparável, revelando que quase 40% dos clientes de compra única na verdade gastaram bem naquela compra, uma diferenciação relevante que estava escondida antes.

## Resultados

### Distribuição dos segmentos

| Segmento | Clientes | % da base | Receita Total | Ticket Médio |
|---|---|---|---|---|
| Clientes Inativos | 34.113 | 36,5% | R$ 1.912.788 | R$ 56,07 |
| Novos Clientes | 22.108 | 23,7% | R$ 1.236.554 | R$ 55,93 |
| Clientes Inativos - Alto Valor | 21.679 | 23,2% | R$ 5.872.728 | R$ 270,89 |
| Novos Clientes - Alto Valor | 15.411 | 16,5% | R$ 4.168.268 | R$ 270,47 |
| Clientes Leais | 30 | <0,1% | R$ 21.798 | R$ 726,61 |
| Clientes em Risco | 11 | <0,1% | R$ 7.011 | R$ 637,38 |
| Campeões | 3 | <0,1% | R$ 2.185 | R$ 728,48 |
| Limbo | 3 | <0,1% | R$ 165 | R$ 54,87 |

### O contraste entre volume e valor individual

Um dos achados mais interessantes da análise vem de comparar dois ângulos diferentes dos mesmos dados:

- Receita total por segmento: os quatro segmentos de compra única (Inativos e Novos, com e sem Alto Valor) somam 99,9% dos clientes e a maior parte da receita histórica  porque são muitos.
- Receita média por cliente: individualmente, Campeões, Clientes Leais e Clientes em Risco gastam, em média, R$ 700, mais que o dobro dos segmentos "Alto Valor" de compra única (R$ 270) e cerca de 13x mais que os segmentos regulares (R$ 56).
- A subdivisão por Alto Valor confirmou um padrão intermediário: quase 40% dos clientes de compra única (Novos + Inativos - Alto Valor somados) gastaram, em média, R$ 270 numa única compra quase 5x mais que o restante do mesmo grupo de compra única, mas ainda longe do ticket médio de quem tem histórico de recompra (R$ 700).

A leitura de negócio: a maior parte do faturamento histórico vem de clientes que compraram uma vez e nunca voltaram, não de uma base fiel e recorrente. Isso muda a prioridade estratégica: o problema não é reter os poucos "Campeões" (estatisticamente irrelevantes em volume), e sim converter os clientes de compra única, especialmente os de Alto Valor, que já demonstraram disposição de gastar bem em compradores recorrentes.

### O pico da Black Friday

O histograma de Recência revelou um pico isolado de clientes adquiridos em um período específico. Investigando a data exata por trás desse pico, a hipótese foi confirmada com uma segunda query, direta na tabela de pedidos: **24 de novembro de 2017** (Black Friday daquele ano) teve **1.147 pedidos**, mais que o dobro do segundo dia mais movimentado do período. Isso reforça que uma parcela relevante da base foi adquirida por um evento promocional pontual, não por engajamento orgânico contínuo.

## Limitações

Este projeto fez escolhas conscientes de escopo, documentadas aqui para transparência:

- RFM calculado no nível da plataforma, não por vendedor ou categoria: como a Olist processa vendas de milhares de lojistas diferentes, seria possível calcular RFM por vendedor. Essa abordagem foi descartada porque a pergunta de negócio deste projeto é sobre a plataforma como um todo, não sobre lojistas individuais.
- Frequência com poucos níveis reais: por causa da baixíssima taxa de recompra, o score de Frequência efetivamente só assume 3 valores (1, 3, 5), em vez de uma escala contínua de 1 a 5.
- Dados históricos (2016–2018): a metodologia é atemporal, mas os números refletem um período específico e não devem ser lidos como retrato do mercado atual.

## Próximos passos

- Segmentação por categoria de produto: cruzar o segmento RFM de cada cliente com a categoria de produto mais comprada, permitindo respostas mais específicas do tipo "quem são os Campeões que compram eletrônicos?"
- Análise de coorte: acompanhar como diferentes grupos de clientes evoluem ao longo do tempo, complementando a fotografia estática que o RFM oferece.
- Análises futuras: complementar uma base de dados com informações do mercado ao longo dos anos.

## Stack utilizada

- **SQLite**: modelagem e armazenamento dos dados
- **Python** (pandas, numpy): cálculo dos scores e segmentação
- **Matplotlib / Plotly**: visualização
- **Streamlit**: dashboard interativo publicado
- **Google Gemini API**: assistente de perguntas em linguagem natural dentro do dashboard

O banco de dados (`dados.db`) já está incluído no repositório. Para recriá-lo do zero a partir dos CSVs originais, use o schema em [`sql/schema.sql`](sql/schema.sql).

## Fontes

- [CleverTap — RFM Analysis for Customer Segmentation](https://clevertap.com/blog/rfm-analysis/)
- [CleverTap — RFM Analysis in E-commerce](https://clevertap.com/blog/rfm-ecommerce/)
- [CleverTap — Cohort Analysis](https://clevertap.com/blog/cohort-analysis/)
- [CleverTap — Demographic Segmentation](https://clevertap.com/blog/demographic-segmentation/)
- [CleverTap — Psychographic Segmentation](https://clevertap.com/blog/psychographic-segmentation/)
- [Olist Brazilian E-Commerce Public Dataset (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- [Pandas Documentation - General Functions (QCUT)](https://pandas.pydata.org/docs/reference/api/pandas.qcut.html)
- [Livro Python para Análise de Dados - Wes McKinney] 