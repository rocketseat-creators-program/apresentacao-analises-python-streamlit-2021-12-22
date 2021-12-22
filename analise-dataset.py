# -*- coding: utf-8 -*-
from re import T
import pandas as pd
import pydeck as pdk
import numpy as np
import streamlit as st
# +----+-------+-------+-------+--------+-------+-------+--------+---------+--+-------+--------+---+---+------+
# |muni|codIbge| data  |semEpid|popEstim|confAcc|confAcc|obitoAcc|tipoLocal|uf|confDia|obitoDia|lat|lon|_merge|
# |    |       |       |       |        |       | 100k  |        |         |  |       |        |   |   |      |
# | 0  |   1   |  2    |   3   |   4    |   5   |   6   |    7   |    8    | 9|   10  |   11   | 12| 13|  14  |
# +----+-------+-------+-------+--------+-------+-------+--------+---------+--+-------+--------+---+---+------+
@st.cache(persist=True)
def load_dataset(arquivo):
    dataset = pd.read_csv(arquivo)
    dataset.dropna(subset = ['muni', 'codIbge'], inplace = True)
    dataset = dataset.reset_index(drop = True)
    return dataset

dataset = load_dataset('covid_dataset_v2.csv')
st.title("COVID-19 por municipio no Brasil")
st.markdown("Analise de dados do site brasil.io "
            "sobre ocorrencias de COVID-19 nos municipios brasileiros")
st.header("Casos de COVID-19 em Municípios")
ano = int(dataset['semEpid'].max()/100)
semana = int(dataset['semEpid'].max()%100)
st.subheader(f"Última Semana Epidemiológica: {ano}-{semana}")
st.subheader("Data: %s" % dataset['data'].max())
# Primeiro mapa
mediaDia = int(round(sum(dataset['confDia'])/len(dataset['confDia'])))
confNoDia = st.slider("Casos confirmados no dia", 0, mediaDia, 10, 2)
st.text('Deslize o cursor para selecionar o número de casos confirmados no dia')
st.text(' ')
semEpidem = st.slider("Semana Epidemiológica", int(dataset['semEpid'].min()), int(dataset['semEpid'].max()), int(dataset['semEpid'].max()))
st.text('Selecione a semana epidemiológica que deseja ver os dados')
temp_dataset = dataset.query("semEpid == @semEpidem")[["confDia", "lat", "lon"]].dropna(how="any")
st.map(temp_dataset.query("confDia >= @confNoDia")[["lat", "lon"]].dropna(how="any"))
st.text('Utilize o mouse para zoom ou mover o mapa')
# Segundo mapa
st.header("Novos casos por dia")
semanaEpidem = st.slider("Seleção da Semana Epidemiológica", int(dataset['semEpid'].min()), int(dataset['semEpid'].max()), int(dataset['semEpid'].max()))
st.text('A semana epidemiológica selecionada afeta os gráficos e tabela na sequência')
eval_data = dataset
eval_data = eval_data[eval_data['semEpid'] == semanaEpidem]
st.markdown(f"Novos casos de COVID-19 na semana {semanaEpidem}")
# Localizacao de algumas cidades
# Brasilia
BSB_LAT = -15.7934036
BSB_LON = -47.8823172
# Sao Paulo
SPO_LAT = -23.5506507
SPO_LON = -46.6333824
################################
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/outdoors-v11",
    initial_view_state={
        "latitude": BSB_LAT,                   
        "longitude": BSB_LON,
        "zoom": 4,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=eval_data[['confDia', 'lat', 'lon']],
        get_position=['lon', 'lat'],
        auto_highlight=True,
        radius=10000,
        extruded=True,
        pickable=True,
        elevation_scale=500,
        elevation_range=[0, 1500],
        ),
    ],
))
# Tabela de Municipios com mais casos selecionados pelo drop-down na semana 
# epidemiologica selecionada no grafico acima
st.header(f"Os municípios com mais casos - Semana {semEpidem}")
num_muni = st.slider("Número de Municípios para listar", 1 , 10, 6)
select = st.selectbox('Tipo de avaliação - selecione no dropdown', ['Casos confirmados', 'Casos por 100 mil habitantes',\
            'Óbitos no dia', 'Casos no dia'])
temp_data = dataset.query('semEpid == @semanaEpidem')[["muni", "uf", "popEstim", "semEpid", "confAcc", "confAcc100k",\
            "obitoAcc", "obitoDia", "confDia"]].dropna(how="any")
if select == 'Casos confirmados':
    option = 'confAcc'
    selected_case = (temp_data.query("confAcc >= 1")[["muni", "uf", "confAcc", "semEpid",\
            "popEstim"]].sort_values(by=['confAcc'], ascending=False).dropna(how="any")[:num_muni])
    selected_case["popEstim"] = selected_case["popEstim"].astype(int)
    selected_case.rename(columns={'muni':'Cidade', 'uf':'UF', 'confAcc':'Confirmados acum',\
            'semEpid':'Semana', 'popEstim':'População'}, inplace=True)
elif select == 'Casos por 100 mil habitantes':
    option = 'confAcc100k'
    selected_case = (temp_data.query("confAcc100k >= 1")[["muni", "uf", "confAcc100k", "semEpid",\
            "popEstim"]].sort_values(by=['confAcc100k'], ascending=False).dropna(how="any")[:num_muni])
    selected_case['confAcc100k'] = selected_case['confAcc100k'].astype(int)
    selected_case["popEstim"] = selected_case["popEstim"].astype(int)
    selected_case.rename(columns={'muni':'Cidade', 'uf':'UF', 'confAcc100k':'Conf.x 100k', 'semEpid':'Semana',\
            'popEstim':'População'}, inplace=True)
elif select == 'Óbitos no dia': 
    option = "obitoDia"
    selected_case = (temp_data.query("obitoAcc >= 0")[["muni", "uf", "obitoDia", "obitoAcc", "semEpid",\
            "popEstim"]].sort_values(by=['obitoAcc'], ascending=False).dropna(how="any")[:num_muni])
    selected_case["popEstim"] = selected_case["popEstim"].astype(int)
    selected_case.rename(columns={'muni':'Cidade', 'uf':'UF', 'obitoDia':'Óbitos no dia', 'obitoAcc': 'Óbitos Acumulados', \
            'semEpid':'Semana', 'popEstim':'População'}, inplace=True)
else:
    option = 'confDia'
    selected_case = (temp_data.query("confAcc >= 0")[["muni", "uf", "confDia", "confAcc", "semEpid",\
            "popEstim"]].sort_values(by=['confAcc'], ascending=False).dropna(how="any")[:num_muni])
    selected_case["popEstim"] = selected_case["popEstim"].astype(int)
    selected_case.rename(columns={'muni':'Cidade', 'uf':'UF', 'confDia':'Casos no Dia', 'semEpid':'Semana',\
            'popEstim':'População'}, inplace=True)

#print((selected_case))
selected_case.index = np.arange(1, len(selected_case) + 1)
#selected_case.reset_index(drop = True, inplace = True)
#print((selected_case))


st.write(selected_case)
# Historico de casos das opcoes acima em todas as semanas disponiveis com selecao de municipios apresentados
st.header(f"Evolução de {select} nos municípios")
st.subheader("Casos x Semana Epidemiológica")
for city_count in range ((selected_case.shape[0])):
    city_name = str(selected_case.iloc[city_count,0])
    hist_data = dataset.query('muni == @city_name')[['semEpid', option]]
    hist_data.drop_duplicates(subset=['semEpid'], inplace=True)
    hist_data = hist_data.set_index('semEpid')
    hist_data.rename(columns={option:city_name}, inplace=True)
    if city_count == 0: plot_data = hist_data
    else: plot_data = pd.concat([plot_data,hist_data], axis=1)
chart_data = pd.DataFrame(plot_data)
st.line_chart(chart_data)
st.subheader(" ")
st.text("Página criada por Sergio / Rocketseat")
