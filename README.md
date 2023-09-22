# Zomato

## Problema de Negócio

A Zomato é um marketplace de restaurantes, cujo objetivo principal é facilitar o encontro e as negociações entre clientes e restaurantes. Os restaurantes registram suas informações na plataforma da Zomato, incluindo endereço, tipo de culinária, disponibilidade de reservas, serviço de entrega e avaliações dos serviços e produtos. Para melhor compreender o negócio e tomar decisões estratégicas mais informadas, é crucial realizar uma análise aprofundada dos dados da empresa e criar dashboards que respondam às seguintes perguntas:

### Visão Geral

- Quantos restaurantes únicos estão registrados?
- Quantos países únicos estão registrados?
- Quantas cidades únicas estão registradas?
- Qual é o total de avaliações feitas?
- Qual é o total de tipos de culinária registrados?

### Visão Países

- Quantas cidades únicas estão registradas por país?
- Quantos restaurantes únicos estão registrados por país?
- Quais países têm os preços mais elevados?
- Qual é a quantidade de avaliações por país
- Qual é a quantidade de restaurantes que aceitam reservas por país?
- Quais são os países com as maiores notas médias?
- Quais são os países com as menores notas médias?
- Qual é a média de avaliações por país?
- Qual é a média de valor de prato para 2 por país?
- Quais países têm pratos 'gourmet' mais caros em Reais?
- Quais países possuem os pratos mais caros em Reais?
- Quais países possuem os pratos mais baratos em Reais?
- Quais tipos de preço têm a maior quantidade de restaurantes cadastrados por país?

### Visão Cidades

- Quais cidades possuem mais restaurantes cadastrados?
- Quais cidades possuem menos restaurantes cadastrados?
- Quais são as cidades com maior valor de prato para 2?
- Quais são as cidades com maior valor de prato para 2 em reais?
- Quais são as cidades com mais restaurantes avaliados com nota excelente?
- Quais são as cidades com mais restaurantes avaliados com nota baixa?
- Quais são as cidades com maior variedade de culinárias distintas?
- Quais cidades têm mais restaurantes que fazem reservas?
- Quais cidades têm mais restaurantes que fazem entregas?
- Quais cidades têm mais restaurantes que aceitam pedidos online?

### Visão Restaurantes

- Qual restaurante possui a maior nota? Em qual país está localizado?
- Qual restaurante possui a menor nota? Em qual país está localizado?
- Qual restaurante tem menos avaliações? Em qual país está localizado?
- Quais são os restaurantes com mais avaliações?
- Quais são os restaurantes com maior média de avaliação?
- Quais são os restaurantes com menor média de avaliação?
- Quais são os restaurantes que servem culinária brasileira com as maiores notas?
- Quais são os restaurantes com maior valor de prato para 2?
- Quais são os restaurantes com maior valor de prato para 2 em Reais?

### Visão Culinárias
- Entre os restaurantes com as maiores notas, quais são as culinárias e onde estão localizados?
- Quais são as culinárias com as maiores médias de notas?
- Quais são as culinárias com as menores médias de notas?
- Quais são as culinárias com os maiores valores médios de prato para 2?
- Quais são as culinárias com os maiores valores médios de prato para 2 em Reais?
- Quais culinárias possuem mais restaurantes que aceitam pedidos online e fazem entregas?

## Premissas do Negócio
- O modelo de negócio adotado é o de um marketplace.
- As três principais visões do negócio são: Visão Países, Visão Cidades, Visão Restaurantes e Visão Culinárias.

## 💻 Tecnologias Utilizadas

Este projeto foi desenvolvido utilizando as seguintes tecnologias e ferramentas:

- Linguagem de Programação: Phyton
- Bibliotecas de Análise de Dados: pandas, numpy, inflection, plotly, requests e folium          
- Ferramenta de Desenvolvimento de Dashboards: Streamlit
- Plataforma de Hospedagem em Nuvem: GitHub
- Banco de Dados: Kaggle (Zomato Restaurants)

<p align="center">
  <img width="60" height="60" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg"/><img width="60" height="60" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg"/><img width="60" height="60" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/numpy/numpy-original.svg"/><img width="60" height="60" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg"/><img width="60" height="60" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/kaggle/kaggle-original-wordmark.svg"/>
<svg viewBox="0 0 128 128"><g fill="#181616"><path fill-rule="evenodd" clip-rule="evenodd" d="M64 5.103c-33.347 0-60.388 27.035-60.388 60.388 0 26.682 17.303 49.317 41.297 57.303 3.017.56 4.125-1.31 4.125-2.905 0-1.44-.056-6.197-.082-11.243-16.8 3.653-20.345-7.125-20.345-7.125-2.747-6.98-6.705-8.836-6.705-8.836-5.48-3.748.413-3.67.413-3.67 6.063.425 9.257 6.223 9.257 6.223 5.386 9.23 14.127 6.562 17.573 5.02.542-3.903 2.107-6.568 3.834-8.076-13.413-1.525-27.514-6.704-27.514-29.843 0-6.593 2.36-11.98 6.223-16.21-.628-1.52-2.695-7.662.584-15.98 0 0 5.07-1.623 16.61 6.19C53.7 35 58.867 34.327 64 34.304c5.13.023 10.3.694 15.127 2.033 11.526-7.813 16.59-6.19 16.59-6.19 3.287 8.317 1.22 14.46.593 15.98 3.872 4.23 6.215 9.617 6.215 16.21 0 23.194-14.127 28.3-27.574 29.796 2.167 1.874 4.097 5.55 4.097 11.183 0 8.08-.07 14.583-.07 16.572 0 1.607 1.088 3.49 4.148 2.897 23.98-7.994 41.263-30.622 41.263-57.294C124.388 32.14 97.35 5.104 64 5.104z"></path><path d="M26.484 91.806c-.133.3-.605.39-1.035.185-.44-.196-.685-.605-.543-.906.13-.31.603-.395 1.04-.188.44.197.69.61.537.91zm2.446 2.729c-.287.267-.85.143-1.232-.28-.396-.42-.47-.983-.177-1.254.298-.266.844-.14 1.24.28.394.426.472.984.17 1.255zM31.312 98.012c-.37.258-.976.017-1.35-.52-.37-.538-.37-1.183.01-1.44.373-.258.97-.025 1.35.507.368.545.368 1.19-.01 1.452zm3.261 3.361c-.33.365-1.036.267-1.552-.23-.527-.487-.674-1.18-.343-1.544.336-.366 1.045-.264 1.564.23.527.486.686 1.18.333 1.543zm4.5 1.951c-.147.473-.825.688-1.51.486-.683-.207-1.13-.76-.99-1.238.14-.477.823-.7 1.512-.485.683.206 1.13.756.988 1.237zm4.943.361c.017.498-.563.91-1.28.92-.723.017-1.308-.387-1.315-.877 0-.503.568-.91 1.29-.924.717-.013 1.306.387 1.306.88zm4.598-.782c.086.485-.413.984-1.126 1.117-.7.13-1.35-.172-1.44-.653-.086-.498.422-.997 1.122-1.126.714-.123 1.354.17 1.444.663zm0 0"></path></g>
</svg>
          
<p/>


  
## Estratégia da Solução

O painel estratégico foi desenvolvido usando métricas que refletem as três principais visões do modelo de negócio da empresa:

1. Visão do Crescimento dos Países
2. Visão do Crescimento das Cidades
3. Visão do Crescimento dos Restaurantes
4. Visão do Crescimento das Culinárias

Cada visão é representada por um conjunto específico de métricas, fornecendo insights valiosos para a tomada de decisões estratégicas.

## Top 3 Insights de Dados

1. A Índia possui o maior número de restaurantes cadastrados, mas suas avaliações têm notas próximas às do Brasil, que possui menos restaurantes registrados.
2. Apesar do grande número de restaurantes na Índia, a Indonésia possui um número significativamente maior de avaliações na plataforma.
3. A culinária indiana não é a mais popular, apesar da Índia ter um grande número de restaurantes e cidades cadastrados na plataforma.

## Produto Final do Projeto

Desenvolvemos um painel online hospedado na nuvem, acessível a partir de qualquer dispositivo conectado à internet. Você pode acessar o painel através deste link: [Link do Painel](https://zomato.streamlit.app/)

## Conclusão

O objetivo deste projeto é criar um conjunto de gráficos e tabelas que apresentem métricas de forma eficaz para o CEO e outros interessados. As análises fornecem insights cruciais para a tomada de decisões estratégicas.

## Próximos Passos

1. Refinar o conjunto de métricas.
2. Adicionar filtros personalizados.
3. Incorporar novas visões de negócio.
4. Explorar a possibilidade de visualização em outras plataformas.

