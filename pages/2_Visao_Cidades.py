#bibliotecas
import pandas as pd
import numpy as np
import inflection
import plotly.express as px
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title='Visão Cidades', page_icon='🏙️', layout='wide')

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
    "CDD614": "yellow",
    "FFBA00": "mustard",
    "CBCBC8": "grey",
    "FF7800": "orange",
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
#container 1 -- Cidades com mais e menos restaurantes (gráfico de barras)
def top_cities_restaurant (df1, top_asc):
    df_aux = (df1.loc[:,['city', 'restaurant_id']]
              .groupby(['city'])
              .nunique()
              .sort_values('restaurant_id',ascending=top_asc)
              .reset_index())
    df_aux.columns=['Cidades', 'Restaurantes']
    fig = px.bar(df_aux.head(number_cities), x='Cidades', y='Restaurantes', text_auto='.1s')
    fig.update_traces(marker_color='#cc232b', textposition="outside")
    fig = st.plotly_chart(fig, use_container_width=True)
    return fig

#container 2 -- cidades com maior valor de prato para 2 (tabelas)
def cities_plates(df1, coluna, number_cities, value):
    df_aux = (df1.groupby('city')
              [coluna]
              .mean()
              .round(1)
              .sort_values(ascending=False)
              .reset_index())
    df_aux.columns = ['Cidades', value]
    df_aux.set_index('Cidades', inplace=True)
    st.dataframe(df_aux.head(number_cities), use_container_width=True)

#container 3 e 4 -- Cidades com restaurantes bem/mal avaliados (gráfico de barras)
def cities_rate(df1, rating, number_cities):
    df_aux = (df1[df1['aggregate_rating'] >= rating].groupby(['city'])
              .restaurant_id
              .nunique()
              .sort_values(ascending=False)
              .reset_index())
    df_aux.columns = ['Cidades', 'Restaurantes']
    fig = px.bar(df_aux.head(number_cities), x='Restaurantes', y='Cidades', text_auto='.1s')
    fig.update_traces(marker_color='#cc232b')
    st.plotly_chart(fig, use_container_width=True)
    return fig

#---Funções tab2
#container 1 -- Cidades com maior variedade em culinárias (gráfico de barras)
def cities_cuisine(df1, number_cities):
    df_aux = (df1.groupby('city')
              .cuisines
              .nunique()
              .sort_values(ascending=False)
              .reset_index())
    df_aux.columns=['Cidades', 'Culinárias']
    fig = px.bar(df_aux.head(number_cities), x='Culinárias', y='Cidades',text_auto='.2s')
    fig.update_traces(marker_color='#cc232b')
    st.plotly_chart(fig, use_container_width=True) 
    return fig

#---container 2 -- Cidades que aceitam reservas/entregam/aceitam pedidos (tabelas)
def cities_reservation(df, reservation_col, number_cities):
    df_aux = (df[df[reservation_col] == 1].groupby('city')
              .restaurant_id
              .nunique()
              .sort_values(ascending=False)
              .reset_index())
    df_aux.columns = ['Cidades', 'Restaurantes']
    df_aux.set_index('Cidades', inplace=True)
    st.dataframe(df_aux.head(number_cities), use_container_width=True)
    return df_aux



#=================================================
# Barra lateral
#=================================================


st.header('🏙️ Visão Cidades')
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

number_cities = st.sidebar.slider(
    "Selecione a quantidade de Cidades que deseja visualizar",
    value=10,
    min_value=1,
    max_value=20)

def filter_cities(df, number_cities):
    return df.head(number_cities)

st.sidebar.header('', divider='red')
st.sidebar.markdown('### Powered by Karol Uchôa')

#Filtro de países
if 'Todos os Países' not in paises:
    linhas_selecionadas = df1['name_country'].isin(paises)
    df1 = df1.loc[linhas_selecionadas, :]

#Filtro de cidades
df_aux = filter_cities(df1, number_cities)




#=================================================
# Layout no Streamlit
#=================================================
tab1, tab2 = st.tabs( ['Visão 1', 'Visão 2'] )

with tab1:
    
#---container 1 -- Cidades com mais/menos restaurantes (gráfico de barras)
    with st.container():
        st.markdown('#### Cidades com mais restaurantes')
        top_cities_restaurant(df1, top_asc=False) 
        
    with st.container():
        st.markdown('#### Cidades com menos restaurantes')
        top_cities_restaurant(df1, top_asc=True)

#---container 2 -- Cidades com maior valor de prato para 2 (tabelas)
    with st.container():
        col1, col2 = st.columns(2)
    
        with col1:
            st.markdown('#### Cidades com maior valor de prato para dois')
            cities_plates(df1, 'average_cost_for_two', number_cities, value = 'Valor médio')
          
        with col2:
            st.markdown('#### Cidades com maior valor de prato para dois em Reais')
            cities_plates(df1, 'exchange_cost_for_two', number_cities, value = 'Valor médio em Reais')

#---container 3 e 4 -- Cidades com restaurantes bem/mal avaliados (gráfico de barras)
    with st.container():
            st.markdown('#### Top cidades com restaurantes avaliados com nota excelente')
            cities_rate(df1, rating=4, number_cities=number_cities)
        
    with st.container():
            st.markdown('#### Top cidades com restaurantes avaliados com nota baixa')
            cities_rate(df1, rating=2.5, number_cities=number_cities)

with tab2:
#---container 1 -- Cidades com maior variedade em culinárias (gráfico de barras)
    with st.container():
        st.markdown('#### Cidades com maior variedade de culinárias')
        cities_cuisine(df1, number_cities)                                  

#---container 2 -- Cidades que aceitam reservas/entregam/aceitam pedidos (tabelas)
    with st.container():
        st.markdown('## Top cidades com restaurantes que:')
        col1, col2, col3 = st.columns(3)    
        with col1:
            st.markdown('#### fazem reservas')
            cities_reservation(df1, 'has_table_booking', number_cities)
            
        
        with col2:
            st.markdown('#### fazem entregas')
            cities_reservation(df1, 'is_delivering_now', number_cities)
        
        with col3:
            st.markdown('#### aceitam pedidos online')            
            cities_reservation(df1, 'has_online_delivery', number_cities)