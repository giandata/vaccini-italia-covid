import streamlit as st
import os

import pandas as pd
import numpy as np

import altair as alt

base_url = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/"

data_url = ["vaccini-summary-latest.csv",
            "anagrafica-vaccini-summary-latest.csv",
            "consegne-vaccini-latest.csv",
            "somministrazioni-vaccini-latest.csv",
            "punti-somministrazione-latest.csv",
            "somministrazioni-vaccini-summary-latest.csv"
            ]

st.set_page_config(page_title="Vaccinazioni Covid-19",page_icon="favicon.ico",layout="wide")

title_style = """
<div style="background-color:#3b84e3",padding:5px;">
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
st.sidebar.image("fiore.jpg",width=300)
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
    
    st.sidebar.write("Questa pagina contiene statistiche e visualizzazioni con gli ultimi dati disponibili delle vaccinazioni. Utilizzare i bottoni interattivi per personalizzare l'analisi.")
    df_somministrazioni = retrieve_data("vaccini-summary-latest.csv")
    max_date = df_somministrazioni["ultimo_aggiornamento"][0]
    st.text("")
        
    st.subheader(f"Statistiche generali - Dati aggiornati al **{max_date}**")    

    dosi_consegnate = df_somministrazioni["dosi_consegnate"].sum()
    dosi_somministrate = df_somministrazioni["dosi_somministrate"].sum()
    ratio_uso = round((dosi_somministrate / dosi_consegnate)*100,1)

    ita_pop = 60411237
    #explore API worldometer
    col1,col2=st.beta_columns(2)
    with col1:
        st.info(f"Totale dosi consegnate:  {dosi_consegnate}")
    with col2:
        st.info(f"Dosi somministrate  {dosi_somministrate}  (**{ratio_uso} %**) ")


    vaccined_df = retrieve_data("anagrafica-vaccini-summary-latest.csv")
    vaccined_pop_complete = vaccined_df["seconda_dose"].sum()
    vaccined_pop_start = vaccined_df["prima_dose"].sum()
    
    ratio_pop_complete = round((vaccined_pop_complete/ita_pop)*100,2)

    ratio_pop_start = (round(((vaccined_pop_start)/ita_pop)*100,2))
    
    st.write ("Si considerano vaccinate le persone che hanno ricevuto la seconda dose entro a partire da 21 ed entro i 42 giorni successivi (3-6 settimane di distanza).")

    col3,col4=st.beta_columns(2)
    with col3:
        if ratio_pop_start >= 60:
            st.success(f"Popolazione che ha ricevuto prima dose: {ratio_pop_start} % ({vaccined_pop_start}) ")
            st.progress(ratio_pop_start/100)
        elif ratio_pop_start >= 30:
            st.warning(f"Popolazione che ha ricevuto prima dose: {ratio_pop_start}% ({vaccined_pop_start}) ")
            st.progress(ratio_pop_start/100)
        else:
            st.error(f"Popolazione che ha ricevuto prima dose: {ratio_pop_start} % ({vaccined_pop_start}) ")
            st.progress(ratio_pop_start/100)
    with col4:
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
    
    df = ss_somministrate.reset_index(inplace = True)
    
    ss_somm_prima = ss_somministrate[["data_somministrazione","prima_dose"]]
    ss_somm_prima["Somministrazione"] = "Prima dose"
    ss_somm_prima.rename(columns={"prima_dose":"dosi"},inplace=True)
    
    ss_somm_seconda = ss_somministrate[["data_somministrazione","seconda_dose"]]
    ss_somm_seconda["Somministrazione"] = "Seconda dose"
    ss_somm_seconda.rename(columns={"seconda_dose":"dosi"},inplace=True)
    
    df_vertical = pd.concat([ss_somm_prima,ss_somm_seconda],axis=0)
    
    domain = ['Prima dose','Seconda dose']
    range_ = ['cyan','blue']
  
    chart = alt.Chart(df_vertical).mark_area(opacity=0.7).encode(
        x=alt.X("data_somministrazione",axis=alt.Axis(title="")),
        y=alt.Y("dosi",axis=alt.Axis(title="Dosi somministrate")),
        color=alt.Color("Somministrazione",scale=alt.Scale(domain=domain, range=range_),
        legend=alt.Legend(orient="top"))
        ).interactive()
    st.altair_chart(chart,use_container_width=True)
    
    with st.beta_expander("Analisi"):
        st.markdown("""All' approssimarsi dell'esaurimento delle scorte di dosi disponibili notiamo come la quantità di 'prima_dose', ovvero di nuove persone che ricevono il vaccino, diminuisce drasticamente (fine gennaio). Tale tendenza trova riscontro nel fatto che è necessario usare le dosi rimaste per garantire la seconda dose per le persone che hanno già ricevuto la prima dose in precedenza.""") 
        st.markdown("Per questo motivo è molto importante che le consegne, la distribuzione e lo stoccaggio siano ben coordinati. Il rischio è di rendere completamente inefficace la somministrazione: qualora fosse impossibile completare il ciclo di vaccinazione iniziato per alcuni soggetti le dosi usate in prima istanza sarebbero state sprecate.""")
    
    st.write("")
    st.subheader("Consegne dosi")
    df_consegnate = retrieve_data("consegne-vaccini-latest.csv")
    ss_consegnate = (df_consegnate.groupby(["data_consegna"]).sum())
    ss_consegnate = ss_consegnate["numero_dosi"]
    
    choice1 = st.radio("Dati",options=["Giornalieri","Cumulati"])
    if choice1 == "Giornalieri":
        chart_daily = alt.Chart(ss_consegnate.reset_index()).mark_bar().encode(
        x="data_consegna",
        y = "numero_dosi",
        color=alt.Color("numero_dosi",scale=alt.Scale(scheme='blues'),
        legend=alt.Legend(orient="top"))
        ).interactive()
        st.altair_chart(chart_daily,use_container_width=True)
    else:
        chart_cumulated = alt.Chart(ss_consegnate.cumsum().reset_index()).mark_bar().encode(
        x="data_consegna",
        y = "numero_dosi",
        color=alt.Color("numero_dosi",scale=alt.Scale(scheme='blues'),
        legend=alt.Legend(orient="top"))
        ).interactive()
    st.altair_chart(chart_cumulated,use_container_width=True)
    with st.beta_expander("Analisi"):
        st.markdown("Notare come le consegne avvengono a intervalli temporali irregolari: ci sono salti di anche 3-4 giorni tra una consegna e la successiva. Tuttavia le consegne si stanno stabilizzando durante i primi giorni della settimana, dal lunedì al mercoledì.")
        st.markdown("Per quanto riguarda il volume di dosi consegnate, possiamo vedere che il ritmo è piuttosto stabile, quindi almeno nelle prime settimane non stiamo assistendo ad un incremento progressivo delle consegne. Si è raggiunto il primo milione di dosi consegnate in 13 giorni (30 dicembre-11 gennaio), mentre per il secondo milione ci sono voluti 15 giorni (11 - 26 gennaio).  ")


    st.subheader("Stime preliminari")
    st.markdown(" Considerando l'andamento di dosi utilizzate finora e tenendo in conto l'attuale popolazione italiana **(60,4 Milioni)**, è possibile produrre una stima lineare di quanto tempo è necessario per arrivare alla soglia richiesta.")
    aggr_mean= st.selectbox("Media di dosi somministrate, aggregazione:",["Giornaliera","Settimanale","Mensile"])
    slider_start = float(ratio_pop_start)
    residual_pop = ita_pop - vaccined_pop_start
    st.markdown("""Selezionare la percentuale di popolazione su cui calcolare:""" )
    pop_slider = st.slider("",slider_start,float(100),value=70.0)
    pop_perc = residual_pop * (pop_slider/100)
    residual_days=  round(((pop_perc-vaccined_pop_start)/avg_daily[0])+1,0).astype(int)
    
    if aggr_mean == "Giornaliera": 
        avg_daily = round(ss_somministrate.mean(),0).astype(int)
        st.write(f"La media **{aggr_mean}** di **prime-dosi** somministrate è al momento **{avg_daily[0]}**. ")
        st.write(f"Con questo volume, raggiungeremo il **{pop_slider} %** della popolazione in **{residual_days}** giorni,ovvero in **{round(residual_days/365.25,2)}** anni.")
    elif aggr_mean == "Settimanale":
        weekly = (avg_daily[0])*7
        st.write(f"La media **{aggr_mean}** di **prime-dosi** somministrate è al momento **{weekly}**. ")
        st.write(f"Con questo volume, raggiungeremo il **{pop_slider} %** della popolazione in **{round(residual_days/7,0).astype(int)}** settimane.") 
    else:
        monthly = ((avg_daily[0])*30.4375).astype(int)
        st.write(f"La media **{aggr_mean}** di **prime-dosi** somministrate è al momento **{monthly}**. ")
        st.write(f"Con questo volume, raggiungeremo il **{pop_slider} % ** della popolazione in **{round(residual_days/30.4375,0).astype(int)}** mesi.")     

    if st.checkbox ("Vedere serie storica"):
        st.dataframe(ss_somministrate)
    
    st.write("")
    
    st.subheader("Ulteriori analisi")
    st.markdown("Selezionare la dimensione per cui aggregare i dati: ")
    choice_chart = st.radio(label="",options=("Regioni","Fascia anagrafica","Fornitore"))
    if choice_chart == "Regioni":
        uso_region = df_somministrate.groupby(["nome_area"]).sum()
        st.bar_chart(uso_region[["prima_dose","seconda_dose"]])
        
    elif choice_chart == "Fascia anagrafica":
        uso_anagrafica = df_somministrate[["prima_dose","seconda_dose"]].groupby(df_somministrate["fascia_anagrafica"]).sum()
        st.bar_chart(uso_anagrafica)
    elif choice_chart == "Fornitore":
        uso_fornitore =  df_somministrate[["prima_dose","seconda_dose"]].groupby(df_somministrate["fornitore"]).sum()    
        st.bar_chart(uso_fornitore)
    
if page == "Consulta Dati":
    st.sidebar.write("Questa pagina consente di visualizzare in forma tabulare i dati originali utilizzati in questa applicazione. ")
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
    st.sidebar.write("Riferimenti generali")

    
    st.write("")
    st.subheader("Fonti:")
    st.markdown("""**[Developers Italia](https://github.com/italia/covid19-opendata-vaccini/tree/master/dati) **""")
    st.markdown("""[Worldometers](https://www.worldometers.info/world-population/italy-population/)""")
    
    st.markdown("""Codice: **[GitHub](https://github.com/giandata/streamlit) ** """)
    st.subheader("Autori:")
    st.write("Giancarlo Di Donato")
    st.write("Francesco Di Donato")
    st.write("Creato: 23/01/2021")
    st.write("Ultimo aggiornamento: 01/02/2021")


 
    # coordinates =[['ABR',42.235347, 13.878107],
    #     ['BAS',40.610803, 16.083839],
    #     ['CAL',39.057941, 16.542682],
    #     ['CAM',40.845651, 14.269339],
    #     ['EMR',44.493665, 11.343094],
    #     ['FVG',46.065878, 13.237700],
    #     ['LAZ',41.890104, 12.493002],
    #     ['LIG',44.409843, 8.925506],
    #     ['LOM',45.464125, 9.190290],
    #     ['MAR',43.612374, 13.511463],
    #     ['MOL',41.920512, 14.801354],
    #     ['PAB',46.497633, 11.354615],
    #     ['PAT',46.071503, 11.115640],
    #     ['PIE',45.072623, 7.686570],
    #     ['PUG',41.120561, 16.869802],
    #     ['SAR',40.090803, 9.157500],
    #     ['SIC',37.542997, 14.188410],
    #     ['TOS',43.773038, 11.255479],
    #     ['UMB',43.113692, 12.387939],
    #     ['VDA',45.737887, 7.322980],
    #     ['VEN',45.492624, 12.185767]
    #     ]
    
    #df_coord = pd.DataFrame(coordinates,columns=["region","latitude","longitude"])
    #st.dataframe(df_coord)