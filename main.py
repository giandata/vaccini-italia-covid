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

@st.cache
def retrieve_data(url):
    full_url = base_url + url
    return pd.read_csv(full_url,index_col=0,parse_dates=[0])


def render_checkbox(url):
    if st.checkbox("Carica dati",key=url):
        data = retrieve_data(url)
        st.dataframe(data)

def nice_header(string):
    url_without_ext = os.path.splitext(string)[0]
    url_clean = url_without_ext.split("-")
    url_readable = " ".join(url_clean)
    st.subheader(url_readable.upper())


st.title ("Tracking vaccinazioni Covid-19")

tabs = ["Informazioni","Esploratore","Tracciamento"]

page = st.sidebar.selectbox("Pagine",tabs)


if page == "Informazioni":

    st.write("Autori:")
    st.text("Giancarlo Di Donato")
    st.text("Francesco Di Donato")


if page == "Esploratore":
    for url in data_url:
        nice_header(url)
        render_checkbox(url)

if page == "Tracciamento":
    st.balloons()




        
