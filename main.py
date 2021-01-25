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

#@st.cache(persist=True)
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

def chart(df):
    st.linechart()


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
    
    chart1 = retrieve_data("vaccini-summary-latest.csv")
    max_date = chart1["ultimo_aggiornamento"][0]
    st.text("")
        
    st.subheader(f"Statistiche generali - Dati aggiornati al **{max_date}**")    

    dosi_consegnate = chart1["dosi_consegnate"].sum()
    dosi_somministrate = chart1["dosi_somministrate"].sum()
    ratio_uso = round((dosi_somministrate / dosi_consegnate)*100,1)

    ita_pop = 60411237
    #explore API worldometer

    st.info(f"Totale dosi consegnate  {dosi_consegnate}")
    st.success(f"Totale dosi somministrate  {dosi_somministrate}  ( **{ratio_uso} %** )  delle dosi distribuite")
    
    vaccined_df = retrieve_data("anagrafica-vaccini-summary-latest.csv")
    vaccined_pop_complete = vaccined_df["seconda_dose"].sum()
    vaccined_pop_start = vaccined_df["prima_dose"].sum()
    
    ratio_pop_complete = round((vaccined_pop_complete/ita_pop)*100,3)

    ratio_pop_start = (round(((vaccined_pop_start-vaccined_pop_complete)/ita_pop)*100,3))
    
    st.write ("Si considerano vaccinate le persone che abbiano ricevuto 2 dosi a distanza di 3 settimane...")
    st.warning(f"Popolazione in corso di vaccinazione: {ratio_pop_start} % ")
    st.progress(ratio_pop_start/100)
    st.error(f"Popolazione vaccinata: {ratio_pop_complete} % ")
    st.progress(ratio_pop_complete/100)
    
    #daily/weekly/monthly average vaccined people 

    
    st.write("")
    st.subheader("Consegne dosi")
    df_consegnate = retrieve_data("consegne-vaccini-latest.csv")
    ss_consegnate = df_consegnate.groupby(["data_consegna"]).sum()
    st.bar_chart(ss_consegnate)

    st.subheader("Utilizzo dosi")
    df_somministrate = retrieve_data("somministrazioni-vaccini-latest.csv")
    ss_somministrate = df_somministrate[["prima_dose","seconda_dose"]].groupby(df_somministrate.index).sum()
    st.area_chart(ss_somministrate)
    
     
    st.write("")


    choice_chart = st.radio(label="Aggruppare dati per",options=("Regioni","Fascia anagrafica","Fornitore"))
    if choice_chart == "Regioni":
        uso_region = df_somministrate.groupby(["area"]).sum()
        st.bar_chart(uso_region[["prima_dose","seconda_dose"]])
    elif choice_chart == "Fascia anagrafica":
        uso_anagrafica = df_somministrate[["prima_dose","seconda_dose"]].groupby(df_somministrate["fascia_anagrafica"]).sum()
        st.bar_chart(uso_anagrafica)
    elif choice_chart == "Fornitore":
        uso_fornitore =  df_somministrate[["prima_dose","seconda_dose"]].groupby(df_somministrate["fornitore"]).sum()    
        st.bar_chart(uso_fornitore)
    


    # uso_region["totale"] = uso_region["prima_dose"] + uso_region["seconda_dose"]
    # uso_region_sorted = uso_region.sort_values(by=["totale"],ascending = False)
    # st.dataframe(uso_region_sorted)


   




