import streamlit as st
import pandas as pd

st.title("Allergy Supermarket")
st.write("Hello, world!")

options = st.multiselect(
    "Allergen Filter",
    ["Frutta a guscio", "Arachidi"],
    default=["Frutta a guscio"],
)

st.write("You selected:", options)

df = pd.read_csv("data//products_normalized.csv")[['id', 'name', 'shortDescr', 'description', 'metaData.product_description.ALLERGEN_CONTAINS']]

df['Frutta a guscio'] = 0
df.iloc[0,-1]=1

# need to filter the output by the selected allergens

st.dataframe(df)

#https://docs.streamlit.io/develop/api-reference/data/st.dataframe