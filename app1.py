import streamlit as st
from github import Github

g = Github("giandata","password")

# g = Github("acces_token")

for repo in g.get_user().get_repos():
    repos=[]
    print(repo.name)
    return repos.append(repo.name)


st.title("Github connection App")

st.write

