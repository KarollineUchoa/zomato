
#bibliotecas
import pandas as pd
import numpy as np
import inflection
import plotly.express as px
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title='Visão Países', page_icon='📍', layout='wide')

#import arquivos csv
df = pd.read_csv('dataset/zomato.csv')

#cópia de dataframe
df1 = df.copy()

#Renomeando colunas do dataframe
def rename_columns(dataframe):
    df1 = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df1.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df1.columns = cols_new
    return df1

#Criação do nome das cores (RGB para nomes)
colors = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}

def color_name(color_code):
    return colors[color_code]

#Criação do tipo de categoria de comida
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

#Criação do nome dos países
countries = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}
def country_name(country_id):
    return countries[country_id]

#Mudança do nome das moedas para conter o nome do país e possibilitar a conversão do dolar corretamente
dollar_countries = ['Australia', 'Canada', 'Singapure', 'United States of America']

def get_currency(name_country, currency):
    if currency == 'Dollar($)':
        return f'{currency} {name_country}'
    else:
        return currency

#Criação da coluna de siglas para as moedas
moedas = {
    'Botswana Pula(P)': "BWP",
    'Brazilian Real(R$)': "BRL",
    'Dollar($) Australia': "AUD",
    'Dollar($) United States of America': "USD",
    'Dollar($) Canada': "CAD",
    'Dollar($) Singapure': "SGD",
    'Emirati Diram(AED)': "AED",
    'Indian Rupees(Rs.)': "INR",
    'Indonesian Rupiah(IDR)': "IDR",
    'NewZealand($)': "NZD",
    'Pounds(£)': "GBP",
    'Qatari Rial(QR)': "QAR",
    'Rand(R)': "ZAR",
    'Sri Lankan Rupee(LKR)': "LKR",
    'Turkish Lira(TL)': "TRY",
}

def currency_code(currency_id):
    return moedas[currency_id]

# Chamando as funções
df1 = rename_columns(df1)
df1['name_rating_color'] = df1['rating_color'].map(color_name)
df1['name_price_range'] = df1['price_range'].map(create_price_tye)
df1['name_country'] = df1['country_code'].map(country_name)
df1['currency'] = df1.apply(lambda row: get_currency(row['name_country'], row['currency']), axis=1)
df1['code_currency'] = df1['currency'].map(currency_code)

#Conversão de dados da coluna 'cuisines' de float para string:
df1['cuisines'] = df1['cuisines'].astype(str)

#Convertendo a coluna para Float
df1['average_cost_for_two'] = df1['average_cost_for_two'].astype(float)

#Categorizando os restaurantes somente por 1 tipo de culinária
df1["cuisines"] = df1.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

#Retirando coluna 'switch_to_order_menu' que possui 0 em todas as linhas
df1 = df1.drop('switch_to_order_menu', axis=1)

#exclusão de linhas duplicadas
df1 = df1.drop_duplicates()

df1.isnull().any()

#--------------Conversão de moedas
req = ('https://economia.awesomeapi.com.br/json/last/USD-BRL,AED-BRL,INR-BRL,NZD-BRL,GBP-BRL,ZAR-BRL,TRY-BRL,AUD-BRL,CAD-BRL,SGD-BRL,ZAR-BRL')
response = requests.get(req)
df2 = pd.read_json(response.text, orient = "index")
df2 = df2[[
    "code",
    "bid"
]]

#Dicionário com as taxas de câmbio fixo para moedas não convertidas pela API
exchange_rates = {
    'BWP': 0.36470,
    'IDR': 0.00032,
    'QAR': 1.36218,
    'LKR': 0.01544,
    'BRL': 1
}

for index, row in df2.iterrows():
    # Atribuindo o valor da coluna 'code' da linha atual à variável 'code'
    code=row['code']
    # Atribuindo o valor da coluna 'bid' da linha atual à variável 'bid'
    bid=row['bid']
    # Adicionando a chave 'code' e o valor 'bid' ao dicionário 'exchange_rates'
    exchange_rates[code] = bid
    
data = {
    'code': list(exchange_rates.keys()),
    'bid': list(exchange_rates.values())
}

df3 = pd.DataFrame(data)

#Criando a coluna 'exchange_rates' com as taxas de câmbio para cada moeda
df1['exchange_rates'] = df1['code_currency'].map(df3.set_index('code')['bid'])

#criando a coluna 'exchange_cost_for_two' com o custo dos pratos convertidos para moeda única - Real
df1['exchange_cost_for_two'] = df1['exchange_rates'] * df1['average_cost_for_two']



#=================================================
# Barra lateral
#=================================================


st.markdown('# 📍 Visão Países')
image = Image.open('zomato.png')

st.sidebar.image (image, width=180)
st.sidebar.markdown('''# :red[Zomato]''')
st.sidebar.header('Better food for more people', divider='red')

st.sidebar.markdown('## Filtros:')
paises = st.sidebar.multiselect(
    'Escolha os países que deseja visualizar as informações:',
    ['Todos os Países'] + sorted(['Philippines', 'Brazil', 'Australia', 'United States of America',
     'Canada', 'Singapure', 'United Arab Emirates', 'India','Indonesia',
     'New Zeland', 'England', 'Qatar', 'South Africa','Sri Lanka', 'Turkey']),
    default= ['Todos os Países'])

#Filtro slider de número de países
number_countries = st.sidebar.slider(
    "Selecione a quantidade de Países que deseja visualizar",
    value=10,
    min_value=1,
    max_value=20)

def filter_countries(df, number_countries):
    return df.head(number_countries)

st.sidebar.header('', divider='red')
st.sidebar.markdown('### Powered by Karol Uchôa')

#Filtro de países
if 'Todos os Países' not in paises:
    linhas_selecionadas = df1['name_country'].isin(paises)
    df1 = df1.loc[linhas_selecionadas, :]
    
#---------------------------------------
#Funções pós limpeza referentes aos gráficos e tabelas (parte visual)
#---------------------------------------
#---Funções tab1
#container 1 -- Cidades e restaurantes cadastrados por país (gráfico de barras)
def country_nunique(df1, coluna, value_x, value_y):
    df_aux= (df1.groupby('name_country')
             [coluna]
             .nunique()
             .sort_values(ascending=False)
             .reset_index())
    df_aux.columns = [value_y, value_x]           
    fig = px.bar(df_aux.head(number_countries), x=value_x, y=value_y, text_auto='.2s')
    fig.update_traces(textposition="outside", marker_color='#cc232b')
    st.plotly_chart(fig, use_container_width=True)
    
#container 2 / col1 -- Países com preço mais elevado
def country_price(df1, price):
    df_aux = (df1[df1['price_range'] == price]
              .groupby('name_country')
              .restaurant_id
              .nunique()
              .sort_values(ascending=False)
              .reset_index())
    df_aux.columns = ['País', 'Restaurantes']
    df_aux.set_index('País', inplace=True)
    st.dataframe(df_aux.head(number_countries), use_container_width=True)

#container 2 / col2 -- Países com mais culinárias distintas (tabela)
def country_cuisines(df1):
    df_aux=(df1.groupby('name_country')
            .cuisines
            .nunique()
            .sort_values(ascending=False)
            .reset_index())
    df_aux.columns = ['País', 'Culinária']
    df_aux.set_index('País', inplace=True)
    st.dataframe(df_aux.head(number_countries), use_container_width=True)
    
#---container 3 (tab1) e container 3 (tab2) -- Número de avaliações e média de avaliações por país (gráfico de barras)   
def country_votes(df1, operation, value_x, value_y):
    df_aux = (df1.groupby('name_country')
              ['votes']
              .agg(operation)
              .sort_values(ascending=False)
              .reset_index())
    df_aux.columns = [value_y, value_x]
    fig = px.bar(df_aux.head(number_countries), x=value_x, y=value_y, text_auto='.3s')
    fig.update_traces(textposition="outside", marker_color='#cc232b')
    st.plotly_chart(fig, use_container_width=True)
    
     
#---Funções tab2
#container 1 -- Restaurantes que reservam por país (gráfico de barras)
def country_reservation(df1):
    df_aux=(df1[df1['has_table_booking'] == 1].groupby('name_country')
            .restaurant_id
            .nunique()
            .sort_values(ascending=False)
            .reset_index())
    df_aux.columns = ['Países', 'Restaurantes']
    fig = px.bar(df_aux.head(number_countries), x='Restaurantes', y='Países', text_auto='.1s')
    fig.update_traces(textposition="outside", marker_color='#cc232b')
    st.plotly_chart(fig, use_container_width=True)
    
#container 2 -- Países com maiores e menores notas (tabelas)
def country_rating(df1, top_asc):
    df_aux = (df1.groupby('name_country')
              .agg({'aggregate_rating': 'mean', 'votes': 'sum'})
              .round(2)
              .sort_values(by='aggregate_rating', ascending=top_asc)
              .reset_index())
    df_aux.columns = ['País', 'Nota média', 'Total de votos']
    df_aux.set_index('País', inplace=True)
    st.dataframe(df_aux.head(number_countries), use_container_width=True)
    
#container 3 -- ver tab1 container 3
    
#container 4 tab2 e container2 tab3 -- Média de prato para 2 por país e pratos mais baratos/caros em reais (tabela)
def country_plate(df1, coluna, top_asc, col1, col2):
    df_aux = (df1.groupby('name_country')
              [coluna]
              .mean()
              .round(1)
              .sort_values(ascending=top_asc)
              .reset_index())
    df_aux.columns = [col1, col2]
    df_aux.set_index(col1, inplace=True)
    st.dataframe(df_aux.head(number_countries), use_container_width=True)    
    
     
#---Funções tab3
#--container 1 -- Países pratos gourmet e mais caros em Reais
def country_plates_gourmet(df1):
    df_aux = (df1[df1['name_price_range'] == 'gourmet'].groupby('name_country')
              .exchange_cost_for_two
              .mean()
              .round(2)
              .sort_values(ascending=False)
              .reset_index())
    df_aux.columns = ['País', 'Valor médio em Reais']
    df_aux.head(10)
    fig = px.bar(df_aux.head(number_countries), x='Valor médio em Reais', y='País',text_auto='.3s')
    fig.update_traces(textposition="outside", marker_color='#cc232b')
    st.plotly_chart(fig, use_container_width=True)
    
#--container 2 -- ver tab2 container 4

#--container 3 -- Restaurantes por tipo de preço por país
def country_name_price(df1):
    df_aux = (df1.groupby(['name_price_range', 'name_country'])
              .restaurant_id
              .nunique()
              .reset_index()
              .sort_values(['name_price_range','restaurant_id'], ascending=False)
              .groupby('name_price_range')
              .head(4))
    df_aux.columns = ['Preço', 'País', 'Restaurantes']
    df_aux = df_aux.reset_index()
    df_aux = df_aux.drop(columns='index')
    fig = px.bar(df_aux.head(number_countries),
                 x="País", 
                 y="Restaurantes", 
                 color='Preço',
                 text='Restaurantes')
    st.plotly_chart(fig, use_container_width=True)


#=================================================
# Layout no Streamlit
#=================================================
tab1, tab2, tab3 = st.tabs( ['Visão 1', 'Visão 2', 'Visão 3'] )

with tab1:
#---container 1 -- Cidades e restaurantes cadastrados por país (gráfico de barras)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('#### Cidades cadastradas')
            country_nunique(df1, 'city', value_x = "Cidades", value_y = 'Paises')            
        
        with col2:
            st.markdown('#### Restaurantes cadastrados')           
            country_nunique(df1, 'restaurant_id',  value_x = "Restaurantes", value_y = 'Paises')

#---container 2 -- Países com preço mais elevado e culinárias distintas (tabela)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('#### Top países com preço mais elevado')
            country_price(df1, 4)           

        with col2:
            st.markdown('#### Top países com culinárias distintas')
            country_cuisines(df1)           
            
#---container 3 -- Número de avaliações por país (gráfico de barras)    
    with st.container():
        st.markdown('#### Avaliações por país')
        country_votes(df1, operation = sum, value_x='Avaliações', value_y='País')

with tab2:
#---container 1 -- Restaurantes que reservam por país (gráfico de barras)
    with st.container():
        st.markdown('## Restaurantes que aceitam reserva')
        country_reservation(df1)
        
#---container 2 -- Países com maiores e menores notas (tabelas)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('### Maiores notas médias')
            country_rating(df1, top_asc=False)        

        with col2:
            st.markdown('### Menores notas')
            country_rating(df1, top_asc=True)   
            
#---container 3 -- Média de avaliações por país (gráfico de barras)            
    with st.container():
        st.markdown('## Media de avaliações')
        country_votes(df1, operation = 'mean', value_x='Média de avaliações', value_y='País')
        
#---container 4 -- Média de prato para 2 por país (tabela)
    with st.container():
        st.markdown('## Média de prato para 2')
        country_plate(df1, coluna='average_cost_for_two', top_asc=False, col1 = 'País', col2='Média de prato para 2')        
            
with tab3:
#--container 1 -- Países pratos gourmet e mais caros em Reais
    with st.container():
        st.markdown('## Top países de pratos "gourmet" e mais caros em Reais')
        country_plates_gourmet(df1)

#--container 2 -- Países pratos mais caros/baratos em Reais
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('### Países com pratos mais caros em reais')            
            country_plate(df1, coluna='exchange_cost_for_two', top_asc=False, col1 = 'País', col2='Valor médio em Reais') 
            
        with col2:
            st.markdown('### Países com pratos mais baratos em reais')
            country_plate(df1, coluna='exchange_cost_for_two', top_asc=True, col1 = 'País', col2='Valor médio em Reais')

#--container 3 -- Restaurantes por tipo de preço por país            
    with st.container():
        st.markdown('## Restaurantes por tipo de preço por país')
        country_name_price(df1)