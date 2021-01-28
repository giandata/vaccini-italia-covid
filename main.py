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

tabs = ["Tracciamento","Consulta Dati","Informazioni",]

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
    st.info(f"Totale dosi somministrate  {dosi_somministrate}  ( **{ratio_uso} %** )  delle dosi distribuite")


    vaccined_df = retrieve_data("anagrafica-vaccini-summary-latest.csv")
    vaccined_pop_complete = vaccined_df["seconda_dose"].sum()
    vaccined_pop_start = vaccined_df["prima_dose"].sum()
    
    ratio_pop_complete = round((vaccined_pop_complete/ita_pop)*100,2)

    ratio_pop_start = (round(((vaccined_pop_start)/ita_pop)*100,2))
    
    st.write ("Si considerano vaccinate le persone che hanno ricevuto la seconda dose entro a partire da 21 ed entro i 42 giorni successivi (3-6 settimane di distanza).")

   
    if ratio_pop_start >= 60:
        st.success(f"Popolazione che ha ricevuto prima dose: {ratio_pop_start} % ({vaccined_pop_start}) ")
        st.progress(ratio_pop_start/100)
    elif ratio_pop_start >= 30:
        st.warning(f"Popolazione che ha ricevuto prima dose: {ratio_pop_start}% ({vaccined_pop_start}) ")
        st.progress(ratio_pop_start/100)
    else:
        st.error(f"Popolazione che ha ricevuto prima dose: {ratio_pop_start} % ({vaccined_pop_start}) ")
        st.progress(ratio_pop_start/100)

    if ratio_pop_start >= 60:
        st.success(f"Popolazione vaccinata (doppia dose): {ratio_pop_complete} %  ({vaccined_pop_complete})")
        st.progress(ratio_pop_complete/100)
    elif ratio_pop_start >= 30:
        st.warning(f"Popolazione vaccinata (doppia dose): {ratio_pop_complete} % ({vaccined_pop_complete})")
        st.progress(ratio_pop_complete/100)
    else:
        st.error(f"Popolazione vaccinata (doppia dose): {ratio_pop_complete} % ({vaccined_pop_complete})")
        st.progress(ratio_pop_complete/100)
    
    

    
  

    st.subheader("Utilizzo dosi")
    df_somministrate = retrieve_data("somministrazioni-vaccini-latest.csv")
    ss_somministrate = df_somministrate[["prima_dose","seconda_dose"]].groupby(df_somministrate.index).sum()
    
    available_doses = dosi_consegnate - dosi_somministrate
    avg_daily = round(ss_somministrate.mean(),0).astype(int)
    total_avg_daily = avg_daily[0] + avg_daily[1]
    available_days = round(available_doses/total_avg_daily,0).astype(int)

    if available_days >= 10:
        st.success(f"A questo ritmo di somministrazione  sono disponibili dosi per altri **{available_days}** giorni")
    elif available_days >= 5:
        st.error(f"A questo ritmo di somministrazione sono disponibili dosi per altri **{available_days}** giorni")
    else:
        st.success(f"A questo ritmo di somministrazione sono disponibili dosi per altri **{available_days}** giorni")
    
    st.area_chart(ss_somministrate)
    st.text("Osservazioni")
    st.markdown("""All' approsimarsi dell'esaurimento delle scorte di dosi disponibili notiamo come la quantità di 'prima_dose', ovvero di nuove persone che ricevono il vaccino, diminuisce drasticamente (fine gennaio). Tale tendenza trova riscontro nel fatto che è necessario usare le dosi rimaste per garantire la seconda dose per le persone che hanno già ricevuto la prima dose in precedenza.
     In questo senso è importante che l'approviggionamento, la distribuzione e lo stoccaggio siano coordinati. Il rischio è di rendere completamente inefficace la somministrazione: qualora fosse impossibile completare il ciclo di vaccinazione iniziato per alcuni soggetti le dosi usate in prima istanza sarebbero state sprecate.""")
    
    #lookup -21
    st.write("")
    st.subheader("Consegne dosi")
    df_consegnate = retrieve_data("consegne-vaccini-latest.csv")
    ss_consegnate = df_consegnate.groupby(["data_consegna"]).sum()
    st.bar_chart(ss_consegnate)

    


    st.subheader("Stime preliminari")
    aggr_mean= st.selectbox("Media",["Giornaliera","Settimanale","Mensile"])
    pop_slider = st.slider("Percentuale popolazione vaccinata (%)",1,100)
    pop_perc = ita_pop * (pop_slider/100)
    if aggr_mean == "Giornaliera":
        avg_daily = round(ss_somministrate.mean(),0).astype(int)
        st.write(f"La media {aggr_mean} di **prime-dosi** somministrate è al momento **{avg_daily[0]}**. ")
        st.write(f"Con questo volume, raggiungeremo il **{pop_slider} %** della popolazione in **{round((pop_perc/avg_daily[0]),0).astype(int)}** giorni,ovvero in **{round((pop_perc/avg_daily[0])/365.25,2)}** anni.")
    elif aggr_mean == "Settimanale":
        weekly = (avg_daily[0])*7
        st.write(f"La media {aggr_mean} di **prime-dosi** somministrate è al momento **{weekly}**. ")
        st.write(f"Con questo volume, raggiungeremo il **{pop_slider} %** della popolazione in **{round(pop_perc/weekly,0).astype(int)}** settimane.") 
    else:
        monthly = ((avg_daily[0])*30.4375).astype(int)
        st.write(f"La media {aggr_mean} di **prime-dosi** somministrate è al momento **{monthly}**. ")
        st.write(f"Con questo volume, raggiungeremo il **{pop_slider/100} % ** della popolazione in **{round(pop_perc/monthly,0).astype(int)}** mesi.")     

    if st.checkbox ("Vedere serie storica"):
        st.dataframe(ss_somministrate)

    
    


 


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

if page == "Informazioni":

    st.image("fiore.jpg",width=700)

    st.write("Autori:")
    st.subheader("Giancarlo Di Donato")
    st.subheader("Francesco Di Donato")
    st.write("")
    st.write("Fonti:")
    st.markdown("""**[Developers Italia](https://github.com/italia/covid19-opendata-vaccini/tree/master/dati) **""")
    st.markdown("""[Worldometers](https://www.worldometers.info/world-population/italy-population/)""")
    
    st.markdown("""Codice: **[GitHub](https://github.com/giandata/streamlit) ** """)

    st.write("Creato: 23/01/2021")
    st.write("Versione 1.0.2")




