import streamlit as st
from github import Github
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("TOKEN")

g = Github(token)

st.title("Github Connection App")

user = g.get_user()
username = user.login

st.subheader("User: {}".format(username))

repos = user.get_repos()

st.subheader("Current Repos")

for repo in repos:
    st.write(repo.name) 

import pandas as pd
url = 'https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/anagrafica-vaccini-summary-latest.csv'
df = pd.read_csv(url,index_col=0,parse_dates=[0])

st.write(df.head())