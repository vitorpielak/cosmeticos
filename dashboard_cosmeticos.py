import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(layout="wide") 

# Carregar o CSV
df = pd.read_csv('cosmetics_sales_data.csv', delimiter=',', encoding='utf-8')

# Traduzir dados da coluna Product usando map
df['Product'] = df['Product'].map({
    'Aloe Vera Gel': 'Aloe Vera Gel',
    'Body Butter Cream': 'Creme de Manteiga Corporal',
    'Salicylic Acid Cleanser':'Limpador de ácido salicílico',
    'Lip Balm Pack': 'Pacote de protetor labial',
    'Rose Water Toner': 'Tônico de água de rosas',
    'Tea Tree Moisturizer':'Hidratante da árvore do chá',
    'Face Sheet Masks' : 'Máscaras faciais',
    'Hair Repair Oil' : 'Óleo de reparação capilar',
    'Vitamin C Cream': 'Creme de vitamina C',
    'Niacinamide Toner': 'Tônico de niacinamida',
    'Under Eye Cream': 'Creme para os olhos',
    'Hydrating Face Serum': 'Sérum facial hidratante',
    'Charcoal Face Wash': 'Sabonete Facial Carvão',
    'Anti-Aging Serum': 'Soro Anti-Envelhecimento',
    'SPF 50 Sunscreen': 'Protetor Solar FPS 50',
})

df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day

#converter mes numero em nome em pt-br
df['Month'] = df['Month'].astype(str)
df['Month'] = df['Month'].map({
    '1': 'Janeiro',
    '2': 'Fevereiro',
    '3': 'Março',
    '4': 'Abril',
    '5': 'Maio',
    '6': 'Junho',
    '7': 'Julho',
    '8': 'Agosto',
    '9': 'Setembro',
    '10': 'Outubro',
    '11': 'Novembro',
    '12': 'Dezembro'
}) 


meses_ordenados = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 
    'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 
    'Novembro', 'Dezembro']

#ordem o mes por ordem correta
df['Month'] = pd.Categorical(df['Month'], categories=meses_ordenados, ordered=True)

# ========================================
# FILTROS GLOBAIS NO TOPO
# ========================================

st.title('Dashboard de Vendas de Cosméticos')

# Informações do autor e dataset
st.markdown("---")
st.markdown("### 📊 Sobre este Dashboard")
st.markdown("**Estudo desenvolvido por:** Vitor Pielak")
st.markdown("**LinkedIn:** [@vitorpielak-ti](https://www.linkedin.com/in/vitorpielak-ti/)")
st.markdown("**Dataset utilizado:** [Cosmetics and Skincare Product Sales Data 2022](https://www.kaggle.com/datasets/atharvasoundankar/cosmetics-and-skincare-product-sales-data-2022/data) - Kaggle")
st.markdown("---")

st.write('Dados de vendas de cosméticos')

# Filtros globais
st.subheader('🔍 Filtros Globais')
st.markdown('*Aplique filtros para analisar dados específicos. Todos os insights abaixo serão atualizados automaticamente.*')

# Criar filtros em colunas
col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

with col_filtro1:
    # Filtro de países
    paises_disponiveis = ['Todos'] + sorted(df['Country'].unique().tolist())
    selected_countries = st.multiselect(
        '🌍 Selecione os países:',
        options=paises_disponiveis,
        default=['Todos']
    )
    
    # Se "Todos" estiver selecionado, incluir todos os países
    if 'Todos' in selected_countries:
        selected_countries = df['Country'].unique().tolist()

with col_filtro2:
    # Filtro de produtos
    produtos_disponiveis = ['Todos'] + sorted(df['Product'].unique().tolist())
    selected_products = st.multiselect(
        '📦 Selecione os produtos:',
        options=produtos_disponiveis,
        default=['Todos']
    )
    
    # Se "Todos" estiver selecionado, incluir todos os produtos
    if 'Todos' in selected_products:
        selected_products = df['Product'].unique().tolist()

with col_filtro3:
    # Filtro de vendedores (se a coluna existir)
    if 'Sales_Person' in df.columns:
        vendedores_disponiveis = ['Todos'] + sorted(df['Sales_Person'].unique().tolist())
        selected_salespeople = st.multiselect(
            '👥 Selecione os vendedores:',
            options=vendedores_disponiveis,
            default=['Todos']
        )
        
        # Se "Todos" estiver selecionado, incluir todos os vendedores
        if 'Todos' in selected_salespeople:
            selected_salespeople = df['Sales_Person'].unique().tolist()
    else:
        selected_salespeople = df['Sales_Person'].unique().tolist() if 'Sales_Person' in df.columns else []
        st.info("⚠️ Coluna 'Sales_Person' não encontrada nos dados.")

# Aplicar filtros ao dataframe
df_filtered = df.copy()

# Filtrar por países
if selected_countries and 'Todos' not in selected_countries:
    df_filtered = df_filtered[df_filtered['Country'].isin(selected_countries)]

# Filtrar por produtos
if selected_products and 'Todos' not in selected_products:
    df_filtered = df_filtered[df_filtered['Product'].isin(selected_products)]

# Filtrar por vendedores
if selected_salespeople and 'Sales_Person' in df.columns and 'Todos' not in selected_salespeople:
    df_filtered = df_filtered[df_filtered['Sales_Person'].isin(selected_salespeople)]

# Mostrar resumo dos filtros aplicados
st.markdown(f"**📊 Dados filtrados:** {len(df_filtered)} registros de {len(df)} total")

# ========================================
# KPIs DE ACOMPANHAMENTO
# ========================================

# KPIs de Acompanhamento
st.subheader('📊 KPIs de Acompanhamento')

# Calcular métricas
receita_total = df_filtered['Amount ($)'].sum()
total_caixas = df_filtered['Boxes_Shipped'].sum()
paises_atendidos = df_filtered['Country'].nunique()
produtos_diferentes = df_filtered['Product'].nunique()
ticket_medio = df_filtered['Amount ($)'].mean()

# Melhor vendedor (assumindo que há uma coluna de vendedor, caso contrário será o produto mais vendido)
if 'Sales_Person' in df_filtered.columns:
    melhor_vendedor = df_filtered.groupby('Sales_Person')['Amount ($)'].sum().idxmax()
    valor_melhor_vendedor = df_filtered.groupby('Sales_Person')['Amount ($)'].sum().max()
else:
    melhor_vendedor = "N/A"
    valor_melhor_vendedor = 0

# Produto mais vendido em valor
produto_mais_vendido_valor = df_filtered.groupby('Product')['Amount ($)'].sum().idxmax()
valor_produto_mais_vendido = df_filtered.groupby('Product')['Amount ($)'].sum().max()

# Produto mais vendido em caixas
produto_mais_vendido_caixas = df_filtered.groupby('Product')['Boxes_Shipped'].sum().idxmax()
caixas_produto_mais_vendido = df_filtered.groupby('Product')['Boxes_Shipped'].sum().max()

# Variação de vendas mês a mês (2022-01 a 2022-08)
df_2022 = df_filtered[df_filtered['Year'] == 2022].copy()
df_2022['Month_Num'] = pd.to_datetime(df_2022['Date']).dt.month
vendas_mensais = df_2022.groupby('Month_Num')['Amount ($)'].sum().reset_index()
vendas_mensais['Month_Name'] = vendas_mensais['Month_Num'].map({
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago'
})

# Calcular variação percentual
if len(vendas_mensais) > 1:
    variacao_ultimo_mes = ((vendas_mensais.iloc[-1]['Amount ($)'] - vendas_mensais.iloc[-2]['Amount ($)']) / vendas_mensais.iloc[-2]['Amount ($)']) * 100
else:
    variacao_ultimo_mes = 0

# Exibir KPIs em colunas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 Receita Total", f"R$ {receita_total:,.2f}")
    st.metric("📦 Total de Caixas", f"{total_caixas:,}")

with col2:
    st.metric("🌍 Países Atendidos", f"{paises_atendidos}")
    st.metric("📦 Produtos Diferentes", f"{produtos_diferentes}")

with col3:
    if melhor_vendedor != "N/A":
        st.metric("👑 Melhor Vendedor", f"{melhor_vendedor}", f"R$ {valor_melhor_vendedor:,.2f}")
    else:
        st.metric("👑 Melhor Vendedor", "N/A")
    st.metric("🏆 Produto Mais Vendido (Valor)", f"{produto_mais_vendido_valor}", f"R$ {valor_produto_mais_vendido:,.2f}")

with col4:
    st.metric("📊 Ticket Médio", f"R$ {ticket_medio:,.2f}")
    st.metric("📈 Variação Mês/Mês", f"{variacao_ultimo_mes:+.1f}%")

# Análise de concentração
st.subheader('🎯 Análise de Concentração')
concentracao_paises = (df_filtered.groupby('Country')['Amount ($)'].sum() / df_filtered['Amount ($)'].sum() * 100).sort_values(ascending=False)
st.write("**Top 3 países representam:**", f"{concentracao_paises.head(3).sum():.1f}% das vendas")

concentracao_produtos = (df_filtered.groupby('Product')['Amount ($)'].sum() / df_filtered['Amount ($)'].sum() * 100).sort_values(ascending=False)
st.write("**Top 3 produtos representam:**", f"{concentracao_produtos.head(3).sum():.1f}% das vendas")

# Gráfico de variação mensal
st.subheader('📈 Evolução das Vendas por Mês (2022)')
fig_variacao = px.line(vendas_mensais, 
                       x='Month_Name', 
                       y='Amount ($)',
                       title='Vendas Mensais 2022',
                       labels={'Month_Name': 'Mês', 'Amount ($)': 'Vendas (R$)'},
                       markers=True,
                       template='plotly_white')
fig_variacao.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago']})
st.plotly_chart(fig_variacao, use_container_width=True)

st.subheader('📋 Dados Detalhados')
st.dataframe(df_filtered)

# ========================================
# SEÇÃO DE GRÁFICOS E VISUALIZAÇÕES
# ========================================

st.markdown("---")
st.subheader('📈 Visualizações Detalhadas')

# a) Receita ao longo do tempo
st.subheader('📊 a) Receita ao longo do tempo')

# Preparar dados para gráfico de linha
df_tempo = df_filtered.groupby(['Year', 'Month']).agg({
    'Amount ($)': 'sum',
    'Boxes_Shipped': 'sum'
}).reset_index()

# Criar coluna de data para ordenação
df_tempo['Date_Key'] = df_tempo['Year'].astype(str) + '-' + df_tempo['Month'].astype(str).str.zfill(2)
df_tempo = df_tempo.sort_values('Date_Key')

fig_tempo = px.line(df_tempo, 
                    x='Date_Key', 
                    y=['Amount ($)', 'Boxes_Shipped'],
                    title='Evolução das Vendas e Caixas Enviadas ao Longo do Tempo',
                    labels={'Date_Key': 'Período', 'value': 'Valor', 'variable': 'Métrica'},
                    template='plotly_white')

fig_tempo.update_layout(
    xaxis_title="Período",
    yaxis_title="Valor",
    legend_title="Métrica"
)

st.plotly_chart(fig_tempo, use_container_width=True)

# b) Vendas por país
st.subheader('🌍 b) Vendas por país')

col_pais1, col_pais2 = st.columns(2)

# Países que mais faturaram
paises_faturamento = df_filtered.groupby('Country')['Amount ($)'].sum().sort_values(ascending=True).tail(10)

fig_paises_fat = px.bar(
    x=paises_faturamento.values,
    y=paises_faturamento.index,
    orientation='h',
    title='Top 10 Países por Faturamento',
    labels={'x': 'Faturamento (R$)', 'y': 'País'},
    template='plotly_white',
    color=paises_faturamento.values,
    color_continuous_scale='viridis'
)

with col_pais1:
    st.plotly_chart(fig_paises_fat, use_container_width=True)

# Países que mais receberam caixas
paises_caixas = df_filtered.groupby('Country')['Boxes_Shipped'].sum().sort_values(ascending=True).tail(10)

fig_paises_caixas = px.bar(
    x=paises_caixas.values,
    y=paises_caixas.index,
    orientation='h',
    title='Top 10 Países por Caixas Recebidas',
    labels={'x': 'Caixas Enviadas', 'y': 'País'},
    template='plotly_white',
    color=paises_caixas.values,
    color_continuous_scale='plasma'
)

with col_pais2:
    st.plotly_chart(fig_paises_caixas, use_container_width=True)

# c) Top 10 produtos em receita
st.subheader('🏆 c) Top 10 produtos em receita')

col_prod1, col_prod2 = st.columns(2)

# Produtos mais vendidos em valor
produtos_valor = df_filtered.groupby('Product')['Amount ($)'].sum().sort_values(ascending=True).tail(10)

fig_produtos_valor = px.bar(
    x=produtos_valor.values,
    y=produtos_valor.index,
    orientation='h',
    title='Top 10 Produtos por Faturamento',
    labels={'x': 'Faturamento (R$)', 'y': 'Produto'},
    template='plotly_white',
    color=produtos_valor.values,
    color_continuous_scale='viridis'
)

with col_prod1:
    st.plotly_chart(fig_produtos_valor, use_container_width=True)

# Produtos mais vendidos em caixas
produtos_caixas = df_filtered.groupby('Product')['Boxes_Shipped'].sum().sort_values(ascending=True).tail(10)

fig_produtos_caixas = px.bar(
    x=produtos_caixas.values,
    y=produtos_caixas.index,
    orientation='h',
    title='Top 10 Produtos por Caixas Vendidas',
    labels={'x': 'Caixas Vendidas', 'y': 'Produto'},
    template='plotly_white',
    color=produtos_caixas.values,
    color_continuous_scale='plasma'
)

with col_prod2:
    st.plotly_chart(fig_produtos_caixas, use_container_width=True)

# d) Participação de cada produto nas vendas
st.subheader('🥧 d) Participação de cada produto nas vendas')

# Calcular participação de cada produto
produtos_participacao = df_filtered.groupby('Product')['Amount ($)'].sum().sort_values(ascending=False)

# Agrupar produtos menores em "Outros"
total_vendas = produtos_participacao.sum()
limite_outros = total_vendas * 0.05  # 5% do total

produtos_principais = produtos_participacao[produtos_participacao >= limite_outros]
outros_valor = produtos_participacao[produtos_participacao < limite_outros].sum()

# Criar dados para o gráfico
dados_pie = produtos_principais.copy()
if outros_valor > 0:
    dados_pie['Outros'] = outros_valor

fig_participacao = px.pie(
    values=dados_pie.values,
    names=dados_pie.index,
    title='Participação dos Produtos nas Vendas',
    template='plotly_white',
    hole=0.3,
    color_discrete_sequence=px.colors.qualitative.Set3
)

st.plotly_chart(fig_participacao, use_container_width=True)

# e) Vendas por vendedor
st.subheader('👥 e) Vendas por vendedor')

if 'Sales_Person' in df_filtered.columns:
    col_vend1, col_vend2 = st.columns(2)
    
    # Vendedores com maior receita
    vendedores_receita = df_filtered.groupby('Sales_Person')['Amount ($)'].sum().sort_values(ascending=True).tail(10)
    
    fig_vendedores_receita = px.bar(
        x=vendedores_receita.values,
        y=vendedores_receita.index,
        orientation='h',
        title='Top 10 Vendedores por Receita',
        labels={'x': 'Receita (R$)', 'y': 'Vendedor'},
        template='plotly_white',
        color=vendedores_receita.values,
        color_continuous_scale='viridis'
    )
    
    with col_vend1:
        st.plotly_chart(fig_vendedores_receita, use_container_width=True)
    
    # Número de vendas por vendedor
    vendedores_vendas = df_filtered.groupby('Sales_Person').size().sort_values(ascending=True).tail(10)
    
    fig_vendedores_vendas = px.bar(
        x=vendedores_vendas.values,
        y=vendedores_vendas.index,
        orientation='h',
        title='Top 10 Vendedores por Número de Vendas',
        labels={'x': 'Número de Vendas', 'y': 'Vendedor'},
        template='plotly_white',
        color=vendedores_vendas.values,
        color_continuous_scale='plasma'
    )
    
    with col_vend2:
        st.plotly_chart(fig_vendedores_vendas, use_container_width=True)
else:
    st.info("⚠️ Coluna 'Sales_Person' não encontrada nos dados. Pulando gráficos de vendedores.")

# f) Produtos mais populares por país
st.subheader('🗺️ f) Produtos mais populares por país')

# Criar tabela dinâmica
pivot_produtos_paises = df_filtered.pivot_table(
    values='Amount ($)',
    index='Country',
    columns='Product',
    aggfunc='sum',
    fill_value=0
)

# Criar heatmap
fig_heatmap = px.imshow(
    pivot_produtos_paises,
    title='Heatmap: Produtos vs Países (Receita)',
    labels=dict(x="Produto", y="País", color="Receita (R$)"),
    aspect="auto",
    color_continuous_scale='viridis'
)

fig_heatmap.update_layout(
    xaxis_title="Produto",
    yaxis_title="País"
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# Tabela dinâmica interativa
st.subheader('📊 Tabela Dinâmica: Produtos vs Países')
st.dataframe(pivot_produtos_paises)

# Resumo estatístico
st.markdown("---")
st.subheader('📈 Resumo Estatístico')

col_res1, col_res2, col_res3 = st.columns(3)

with col_res1:
    st.metric("Total Geral de Vendas", f"R$ {df_filtered['Amount ($)'].sum():,.2f}")
    st.metric("Total Geral de Caixas", f"{df_filtered['Boxes_Shipped'].sum():,}")

with col_res2:
    st.metric("Ticket Médio Geral", f"R$ {df_filtered['Amount ($)'].mean():,.2f}")
    st.metric("Países Únicos", f"{df_filtered['Country'].nunique()}")

with col_res3:
    st.metric("Produtos Únicos", f"{df_filtered['Product'].nunique()}")
    if 'Sales_Person' in df_filtered.columns:
        st.metric("Vendedores Únicos", f"{df_filtered['Sales_Person'].nunique()}")
    else:
        st.metric("Vendedores Únicos", "N/A")

# c) Correlação valor x quantidade
st.subheader('🔗 c) Correlação valor x quantidade')

# Criar scatterplot
fig_correlacao = px.scatter(df_filtered, 
                            x='Boxes_Shipped', 
                            y='Amount ($)',
                            color='Product',
                            title='Correlação: Quantidade de Caixas vs Valor das Vendas',
                            labels={'Boxes_Shipped': 'Caixas Enviadas', 'Amount ($)': 'Valor (R$)', 'Product': 'Produto'},
                            template='plotly_white',
                            hover_data=['Country', 'Date'])

fig_correlacao.update_layout(
    xaxis_title="Caixas Enviadas",
    yaxis_title="Valor (R$)",
    legend_title="Produto"
)

st.plotly_chart(fig_correlacao, use_container_width=True)

# Calcular correlação
correlacao = df_filtered['Boxes_Shipped'].corr(df_filtered['Amount ($)'])
st.metric("Coeficiente de Correlação", f"{correlacao:.3f}")

# Insights adicionais
st.markdown("---")
st.subheader('💡 Insights Adicionais')

# Análise de sazonalidade
st.subheader('📅 Análise de Sazonalidade')
vendas_por_mes = df_filtered.groupby('Month')['Amount ($)'].sum().reindex(meses_ordenados)
fig_sazonalidade = px.bar(
    x=vendas_por_mes.index,
    y=vendas_por_mes.values,
    title='Vendas por Mês - Análise de Sazonalidade',
    labels={'x': 'Mês', 'y': 'Vendas (R$)'},
    template='plotly_white',
    color=vendas_por_mes.values,
    color_continuous_scale='viridis'
)
st.plotly_chart(fig_sazonalidade, use_container_width=True)




