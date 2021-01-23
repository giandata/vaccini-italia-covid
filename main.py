import streamlit as st
import os

import pandas as pd
import numpy as np

base_url = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/"

data_url = ["vaccini-summary-latest.csv",
            "anagrafica-vaccini-summary-latest.csv",
            "consegne-vaccini-latest.csv",
            "somministrazioni-vaccini-latest.csv",
            "punti-somministrazione-latest.csv",
            "somministrazioni-vaccini-summary-latest.csv"
            ]

st.set_page_config(page_title="Vaccinazioni Covid-19",page_icon="favicon.ico")

title_style = """
<div style="background-color:#5ecc70",padding:4px;">
<h1 style ="color:black">Monitoraggio dati vaccinazioni Covid-19 </h1>
</div>
"""
st.markdown(title_style,unsafe_allow_html=True)

@st.cache(persist=True)
def retrieve_data(url):
    full_url = base_url + url
    return pd.read_csv(full_url,index_col=0,parse_dates=[0],header='infer')


def render_checkbox(url):
    if st.checkbox("Carica dati",key=url):
        return retrieve_data(url)

    else:
        return False   

def nice_header(string):
    url_without_ext = os.path.splitext(string)[0]
    url_clean = url_without_ext.split("-")
    url_readable = " ".join(url_clean)
    st.subheader(url_readable.upper())

tabs = ["Informazioni","Consulta Dati","Tracciamento"]

page = st.sidebar.selectbox("Pagine",tabs)

def filter_data(df,column,filter_all):
    cols=[]
    for col in df.columns:
        cols.append(col)
    
    options = sorted((filter_all,*list(df[column].unique())))
    
    filter = st.selectbox("Filtrare",options,key=(df,col)) 
    if filter == filter_all:
        st.dataframe(df)
    else:
        filter_df=df[df[column]==filter]
        st.dataframe(filter_df)


if page == "Informazioni":

    st.image("fiore.jpg",width=700)

    st.write("Autori:")
    st.subheader("Giancarlo Di Donato")
    st.subheader("Francesco Di Donato")

    
    st.markdown(""" Fonte: **[Developers Italia](https://github.com/italia/covid19-opendata-vaccini/tree/master/dati) **""")
    
    st.markdown("""Codice: **[GitHub](https://github.com/giandata/streamlit) ** """)

    st.write("Creato: 23/01/2021")
    st.write("Versione 1.0.0")

if page == "Consulta Dati":
    for url in data_url:
        nice_header(url)
        data = render_checkbox(url)
       
        if data is not False:
            if url in ["consegne-vaccini-latest.csv","somministrazioni-vaccini-latest.csv"]:
                filter_data(data,"fornitore","Tutti i fornitori")
            elif url == "punti-somministrazione-latest.csv":
                filter_data(data,"provincia","Tutte le province")
            else:
                st.dataframe(data)
            
        

if page == "Tracciamento":
    st.write("Sezione in costruzione")




        
