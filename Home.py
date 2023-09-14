#bibliotecas
import pandas as pd
import numpy as np
import inflection
import plotly.express as px
import requests
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

st.set_page_config(page_title='Visão Geral', page_icon='🌎', layout='wide')

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
rating_colors = {
    '3F7E00': 'darkgreen',
    '5BA829': 'green',
    '9ACD32': 'lightgreen',
    'CDD614': 'orange',
    'FFBA00': 'red',
    'CBCBC8': 'darkred',
    'FF7800': 'darkred',
}


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
df1['rating_color'] = df1['rating_color'].map(rating_colors)
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

image_path='zomato.png'
image = Image.open(image_path)

st.sidebar.image (image, width=180)
st.sidebar.markdown('''# :red[Zomato]''')
st.sidebar.header('Better food for more people', divider='red')

st.sidebar.markdown('### Filtros:')

#Filtro multiselect de escolha de países
paises = st.sidebar.multiselect(
    'Escolha os países que deseja visualizar as informações:',
    ['Todos os Países'] + sorted(['Philippines', 'Brazil', 'Australia', 
    'United States of America','Canada', 'Singapure', 'United Arab Emirates',
    'India','Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa','Sri Lanka', 'Turkey']),
    default = ['Todos os Países'])

st.sidebar.header('', divider='red')

st.sidebar.markdown('### Powered by Karol Uchôa')

#Lógica do Filtro de países
if 'Todos os Países' not in paises:
    linhas_selecionadas = df1['name_country'].isin(paises)
    df1 = df1.loc[linhas_selecionadas, :]

#=================================================
# Layout no Streamlit
#=================================================
with st.container():
    st.markdown('# Zomato')
    st.markdown('## :red[O Melhor lugar para encontrar seu mais novo restaurante favorito!]')
    
#-------> MÉTRICAS
    col1, col2, col3, col4, col5 = st.columns(5)    
    
    with col1:
        df_aux = df1['restaurant_id'].nunique()
        col1.metric("Restaurantes", df_aux)
        
    with col2:
        df_aux = df1['name_country'].nunique()
        col2.metric("Países", df_aux)
    
    with col3:
        df_aux = df1['city'].nunique()
        col3.metric("Cidades", df_aux)
        
    with col4:
        df_aux = df1['votes'].sum() / 1000
        col4.metric("Avaliações", f"{round(df_aux)}k")
    
    with col5:
        df_aux = df1['cuisines'].nunique()
        col5.metric("Culinárias", df_aux)
        
#-------> MAPA
with st.container():
    mapa = folium.Map(location=[df1['latitude'].median(), df1['longitude'].median()], zoom_start=1)
    marker_cluster = MarkerCluster()

    for i, restaurant_info in df1.iterrows():
        rating_color = restaurant_info['rating_color']

        popup_text = f"Restaurante: {restaurant_info['restaurant_name']}<br>Culinária: {restaurant_info['cuisines']}<br>Nota Média: {restaurant_info['aggregate_rating']}"        
        folium.Marker(
            location=[restaurant_info['latitude'], restaurant_info['longitude']],
            icon=folium.Icon(color=rating_color),
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(marker_cluster)

    marker_cluster.add_to(mapa)
    folium_static(mapa, width=800)


