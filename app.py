import streamlit as st
import pandas as pd

st.title("Allergy Supermarket")
st.write("Hello, world!")


df = pd.read_csv("data//products_normalized.csv")

st.dataframe(df)

#https://docs.streamlit.io/develop/api-reference/data/st.dataframe