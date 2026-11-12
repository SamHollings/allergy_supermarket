import streamlit as st
import pandas as pd

st.title("Allergy Supermarket")
st.write("Hello, world!")

known_allergens = [
    'Frutta a guscio', 'Arachidi', 'Latte', 'Uova', 'Pesce', 'Crostacei', 
    'Molluschi', 'Soia', 'Glutine', 'Sesamo', 'Senape', 'Sedano', 'None'
]
#ToDo - add 'None' to the list of allergens for products that have no allergens listed, so that they can be filtered in the front end

options = st.multiselect(
    "Allergen Filter",
    known_allergens,
    default=known_allergens,
)

st.write("You selected:", options)

df = pd.read_csv("data//products_frontend.csv")[['id', 'name', 'shortDescr', 'description', 'allergens_list', 'allergens']]

df_output_filtered = df[df['allergens'].isin(options)].drop(columns=['allergens']).drop_duplicates()
# need to filter the output by the selected allergens

st.dataframe(df_output_filtered)

#https://docs.streamlit.io/develop/api-reference/data/st.dataframe