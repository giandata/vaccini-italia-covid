import streamlit as st
import os

import pandas as pd

base_url = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/"

data_url = ["anagrafica-vaccini-summary-latest.csv",
            "consegne-vaccini-latest.csv",
            "punti-somministrazione-latest.csv",
            "somministrazioni-vaccini-latest.csv",
            "somministrazioni-vaccini-summary-latest.csv",
            "vaccini-summary-latest.csv"]


st.title ("Tracking vaccinazioni Covid-19")

tabs = ["Esploratore","Tracciamento"]

page = st.sidebar.selectbox("Pagine",tabs)

if page == "Esploratore":
    for url in data_url:
        full_url = base_url + url
        url_without_ext = os.path.splitext(url)[0]
        url_clean = url_without_ext.split("-")
        url_readable = " ".join(url_clean)
        st.subheader(url_readable.upper())
        if st.checkbox("Vedere dati",key = url_readable):
            df = pd.read_csv(full_url,index_col=0,parse_dates=[0])
            st.dataframe(df)

if page == "Tracciamento":
    st.balloons()




        
