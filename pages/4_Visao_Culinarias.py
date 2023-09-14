#bibliotecas
import pandas as pd
import numpy as np
import inflection
import plotly.express as px
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title='Visão Culinárias', page_icon='🍝', layout='wide')

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
#container 1 -- top restaurantes e (métricas)
def cuisines_metric(df1, indexador, col):
    df_aux = (df1.groupby('cuisines')
              .aggregate_rating
              .mean()
              .round(2)
              .sort_values(ascending=False)
              .reset_index())
    df_cuisine = df_aux.iloc[indexador]['cuisines']
    df_restaurant_info = df1[df1['cuisines'] == df_cuisine].nlargest(1, 'aggregate_rating')
    df_restaurant_name = df_restaurant_info.iloc[0]['restaurant_name']
    df_restaurant_country = df_restaurant_info.iloc[0]['name_country']
    df_note = df_restaurant_info.iloc[0]['aggregate_rating']
    col.metric(f"{df_restaurant_name}:\n\n {df_cuisine} - {df_restaurant_country}", df_note)

#container 2 -- Culinárias com melhor e pior nota média (gráfico de barras)
def cuisines_rating(df1, top_asc):
    df_aux = (df1.groupby('cuisines')
              .aggregate_rating
              .mean()
              .round(2)
              .sort_values(ascending=top_asc)
              .reset_index())
    df_aux.columns = ['Culinárias', 'Nota']
    fig = px.bar(df_aux.head(number_cuisines), x="Nota", y="Culinárias", color='Nota' , text='Nota', color_continuous_scale='OrRd')
    st.plotly_chart(fig, use_container_width=True)
    
#container 3 -- Culinárias com maior valor (tabela)
def cuisines_average(df1, coluna, number_cuisines, value):
    df_aux = (df1.groupby('cuisines')
              [coluna]
              .mean()
              .round(1)
              .sort_values(ascending=False)
              .reset_index())
    df_aux.columns = ['Culinárias', value]
    df_aux.set_index('Culinárias', inplace=True)
    st.dataframe(df_aux.head(number_cuisines), use_container_width=True)
    
#container 4 -- Culinárias com mais rest que entregam e aceitam pedidos (tabela)
def cuisines_delivery(df1):
    linhas = (df1['has_online_delivery'] == 1) & (df1['is_delivering_now'] == 1)
    df_aux = (df1.loc[linhas, ['cuisines', 'restaurant_id']]
              .groupby('cuisines')
              .count()
              .reset_index())
    df_aux = df_aux.sort_values(by='restaurant_id', ascending=False)
    df_aux.columns = ['Culinárias', 'Restaurantes']
    df_aux.set_index('Culinárias', inplace=True)
    st.dataframe(df_aux.head(number_cuisines), use_container_width=True)
    


#=================================================
# Barra lateral
#=================================================


st.markdown('# Visão Culinárias')
image = Image.open('zomato.png')

st.sidebar.image (image, width=180)
st.sidebar.markdown('''# :red[Zomato]''')
st.sidebar.header('Better food for more people', divider='red')

st.sidebar.markdown('## Filtros:')

#Filtro multiselect de escolha de países
paises = st.sidebar.multiselect(
    'Escolha os países que deseja visualizar as informações:',
    ['Todos os Países'] + sorted(['Philippines', 'Brazil', 'Australia', 
    'United States of America','Canada', 'Singapure', 'United Arab Emirates',
    'India','Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa','Sri Lanka', 'Turkey']),
    default = ['Todos os Países'])


#Filtro slider de número de culinárias
number_cuisines = st.sidebar.slider(
    "Selecione a quantidade de Culinárias que deseja visualizar",
    value=10,
    min_value=1,
    max_value=20)

def filter_cuisines(df, number_cuisines):
    return df.head(number_cuisines)

#Filtro multiselect de escolha de culinárias
cuisines_name = st.sidebar.multiselect(
    'Escolha os tipos de culinária:',
    ['Todas as Culinárias'] + sorted(['Italian', 'European', 'Filipino','American', 'Korean', 'Pizza',
       'Taiwanese', 'Japanese', 'Coffee', 'Chinese', 'Seafood',
       'Singaporean', 'Vietnamese', 'Latin American', 'Healthy Food',
       'Cafe', 'Fast Food', 'Brazilian', 'Argentine', 'Arabian', 'Bakery',
       'Tex-Mex', 'Bar Food', 'International', 'French', 'Steak',
       'German', 'Sushi', 'Grill', 'Peruvian', 'North Eastern',
       'Ice Cream', 'Burger', 'Mexican', 'Vegetarian', 'Contemporary',
       'Desserts', 'Juices', 'Beverages', 'Spanish', 'Thai', 'Indian',
       'Mineira', 'BBQ', 'Mongolian', 'Portuguese', 'Greek', 'Asian',
       'Author', 'Gourmet Fast Food', 'Lebanese', 'Modern Australian',
       'African', 'Coffee and Tea', 'Australian', 'Middle Eastern',
       'Malaysian', 'Tapas', 'New American', 'Pub Food', 'Southern',
       'Diner', 'Donuts', 'Southwestern', 'Sandwich', 'Irish',
       'Mediterranean', 'Cafe Food', 'Korean BBQ', 'Fusion', 'Canadian',
       'Breakfast', 'Cajun', 'New Mexican', 'Belgian', 'Cuban', 'Taco',
       'Caribbean', 'Polish', 'Deli', 'British', 'nan', 'California',
       'Others', 'Eastern European', 'Creole', 'Ramen', 'Ukrainian',
       'Hawaiian', 'Patisserie', 'Yum Cha', 'Pacific Northwest', 'Tea',
       'Moroccan', 'Burmese', 'Dim Sum', 'Crepes', 'Fish and Chips',
       'Russian', 'Continental', 'South Indian', 'North Indian', 'Salad',
       'Finger Food', 'Mandi', 'Turkish', 'Kerala', 'Pakistani',
       'Biryani', 'Street Food', 'Nepalese', 'Goan', 'Iranian', 'Mughlai',
       'Rajasthani', 'Mithai', 'Maharashtrian', 'Gujarati', 'Rolls',
       'Momos', 'Parsi', 'Modern Indian', 'Andhra', 'Tibetan', 'Kebab',
       'Chettinad', 'Bengali', 'Assamese', 'Naga', 'Hyderabadi', 'Awadhi',
       'Afghan', 'Lucknowi', 'Charcoal Chicken', 'Mangalorean',
       'Egyptian', 'Malwani', 'Armenian', 'Roast Chicken', 'Indonesian',
       'Western', 'Dimsum', 'Sunda', 'Kiwi', 'Asian Fusion', 'Pan Asian',
       'Balti', 'Scottish', 'Cantonese', 'Sri Lankan', 'Khaleeji',
       'South African', 'Drinks Only', 'Durban', 'World Cuisine',
       'Izgara', 'Home-made', 'Giblets', 'Fresh Fish', 'Restaurant Cafe',
       'Kumpir', 'Döner', 'Turkish Pizza', 'Ottoman', 'Old Turkish Bars',
       'Kokoreç']),
    default = ['Todas as Culinárias'])

st.sidebar.header('', divider='red')
st.sidebar.markdown('### Powered by Karol Uchôa')

#Lógica do Filtro de países
if 'Todos os Países' not in paises:
    linhas_selecionadas = df1['name_country'].isin(paises)
    df1 = df1.loc[linhas_selecionadas, :]

#Lógica do Filtro culinárias
if 'Todas as Culinárias' not in cuisines_name:
    linhas_selecionadas = df1['cuisines'].isin(cuisines_name)
    df1 = df1.loc[linhas_selecionadas, :]
    
    
#=================================================
# Layout no Streamlit
#=================================================
#---container 1 -- Top restaurantes por culinária (métricas)
with st.container():
    st.markdown('## Top Restaurantes por culinária')
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        cuisines_metric(df1, 0, col1)        
        
    with col2: 
        cuisines_metric(df1, 1, col2)
        
    with col3:
        cuisines_metric(df1, 2, col3)
        
    with col4:
        cuisines_metric(df1, 3, col4)
        
    with col5:
        cuisines_metric(df1, 4, col5)

#---container 2 -- Culinárias com melhor e pior nota média (gráfico de barras)
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('##### Culinárias com maior nota média')
        cuisines_rating(df1, top_asc=False)
        
    with col2:
        st.markdown('##### Culinárias com pior nota média')
        cuisines_rating(df1, top_asc=True)

#---container 3 -- Culinárias com maior valor (tabela)
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('##### Culinárias com maior valor médio de prato para 2')
        cuisines_average(df1, 'average_cost_for_two', number_cuisines, value = "Valor Médio")
        
        
    with col2:
        st.markdown('##### Culinárias com maior valor médio de prato para 2 em Reais')
        cuisines_average(df1, 'exchange_cost_for_two', number_cuisines, value = "Valor Médio em Reais")
        
#---container 4 -- Culinárias com mais rest que entregam e aceitam pedidos (tabela)
with st.container():
    st.markdown('#### Culinárias que possuem mais restaurantes que aceitam pedidos online e fazem entregas')
    cuisines_delivery(df1)
    
