#bibliotecas
import pandas as pd
import numpy as np
import inflection
import plotly.express as px
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍴', layout='wide')

#import arquivos csv
df = pd.read_csv('../dataset/zomato.csv')

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

#---------------------------------------
#Funções pós limpeza referentes aos gráficos e tabelas (parte visual)
#---------------------------------------
#---Funções tab1
#container 1 -- Maior/menor nota restaurante (métricas)
def restaurant_metric1(df1, top_asc, col, legend):
    df_aux=(df1.groupby(['name_country', 'restaurant_name'])
            .aggregate_rating
            .mean()
            .round(2)
            .sort_values(ascending=top_asc)
            .reset_index())
    df_country = df_aux.iloc[0,0]
    df_restaurant = df_aux.iloc[0,1]
    df_rating = df_aux.iloc[0,2]
    col.metric(legend + f"\n\n {df_country} - {df_restaurant}", df_rating)

def restaurant_metric2(df1, top_asc, col, legend):
    df_aux=(df1.groupby(['restaurant_id', 'restaurant_name', 'name_country'])
            .votes
            .mean()
            .sort_values(ascending=top_asc)
            .reset_index())
    df_country = df_aux.iloc[0,2]
    df_restaurant = df_aux.iloc[0,1]
    df_rating = df_aux.iloc[0,3]
    col.metric(legend + f" \n\n {df_country} - {df_restaurant}", df_rating)
    
#container 2 -- Restaurantes com mais avaliações
def restaurant_rating(df1):
    df_aux = (df1.groupby(['restaurant_id', 'restaurant_name'])
              .votes
              .sum()
              .sort_values(ascending=False)
              .reset_index())
    df_aux.columns = ['ID', 'Restaurante', 'Avaliações']
    df_aux = df_aux.drop('ID', axis=1)

    fig = px.bar(df_aux.head(number_restaurants),
                 x='Avaliações', 
                 y='Restaurante', 
                 text='Avaliações', 
                 text_auto='.3s',
                 color='Avaliações',
                 color_continuous_scale='OrRd') 
    st.plotly_chart(fig, use_container_width=True)
    
#container 3 -- Restaurantes com maior/menor média de avaliação
def restaurant_mean(df1, top_asc):
    df_aux = (df1.sort_values(['aggregate_rating', 'restaurant_id'], ascending=[top_asc, True])
              .reset_index(drop=True)
              .iloc[:, [1, 16, 19]])
    df_aux.columns = ['Restaurante', 'Nota', 'Avaliações']
    df_aux['Avaliações'] = df_aux['Avaliações'].round(2)
    df_aux.set_index('Restaurante', inplace=True)
    st.dataframe(df_aux.head(number_restaurants), use_container_width=True)
    
#container 4 -- Restaurantes culinária brasileira com maiores notas
def restaurant_brazilian(df1):
    df_aux = (df1[(df1['name_country'] == 'Brazil') & (df1['cuisines'] == 'Brazilian')]
              .sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True])
              .reset_index(drop=True)
              .iloc[:,[1, 16]])
    df_aux.columns = ['Restaurante', 'Nota']
    
    fig = px.bar(df_aux.head(number_restaurants), x="Nota", y="Restaurante", color='Nota' , text='Nota', color_continuous_scale='OrRd')
    
    st.plotly_chart(fig, use_container_width=True)

#container 5 -- Restaurantes maior valor de prato para 2 (moeda local) e em Reais
def restaurant_for_two(df1, coluna, legenda, indexador):
    df_aux = (df1.sort_values([coluna,'restaurant_id'], ascending=[False, True])
              .reset_index(drop=True)
              .round(1)
              .iloc[:,[1,indexador]])
    df_aux.columns = ['Restaurante', legenda]
    df_aux.set_index('Restaurante', inplace=True)
    st.dataframe(df_aux.head(number_restaurants), use_container_width=True)
    

#=================================================
# Barra lateral
#=================================================


st.header('🍴 Visão Restaurantes')
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

number_restaurants = st.sidebar.slider(
    "Selecione a quantidade de Restaurantes que deseja visualizar",
    value=10,
    min_value=1,
    max_value=20)

def filter_restaurants(df, number_restaurants):
    return df.head(number_restaurants)
st.sidebar.header('', divider='red')

st.sidebar.markdown('### Powered by Karol Uchôa')

#Filtro de países
if 'Todos os Países' not in paises:
    linhas_selecionadas = df1['name_country'].isin(paises)
    df1 = df1.loc[linhas_selecionadas, :]

#=================================================
# Layout no Streamlit
#=================================================
#---container 1 -- Métricas de culinária
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        restaurant_metric1(df1, top_asc=False, col=col1, legend="Maior nota: ")
        
    with col2:
         restaurant_metric1(df1, top_asc=True, col=col2, legend="Menor nota: ")
    
    with col3:
        restaurant_metric2(df1, top_asc=False, col=col3, legend="Restaurante mais avaliado")
        
    with col4:
        restaurant_metric2(df1, top_asc=True, col=col4, legend="Restaurante menos avaliado")

#---container 2 -- Restaurantes com mais avaliações
with st.container():
    st.markdown('### Restaurantes com maior número de avaliações')
    restaurant_rating(df1)

#---container 3 -- Restaurantes com maior/menor média de avaliação
with st.container():
    col1, col2 = st.columns(2)
    with col1:              
        st.markdown('### Restaurantes maior média de avaliação')
        restaurant_mean(df1, top_asc=False)

    
    with col2:
        st.markdown('#### Restaurantes com menor média de avaliação')
        restaurant_mean(df1, top_asc=True)

#---container 4 -- Restaurantes culinária brasileira com maiores notas
with st.container():
    st.markdown('### Restaurantes de culinária brasileira com maiores notas')
    restaurant_brazilian(df1)

#---container 5 -- Restaurantes maior valor de prato para 2 (moeda local) e em Reais
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### Restaurantes com maior valor de prato para 2')
        restaurant_for_two(df1, coluna='average_cost_for_two', legenda = 'Prato para 2', indexador=10)

        
    with col2:
        st.markdown('#### Restaurantes com maior valor de prato para 2 em Reais')
        restaurant_for_two(df1, coluna='exchange_cost_for_two', legenda='Prato para 2 em Reais', indexador=25)    