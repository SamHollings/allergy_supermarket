
# %%
import pandas as pd

# %%
products_raw = pd.read_json("..///data//products.json")

products_normalized = pd.json_normalize(products_raw['products'])

# %%

products_normalized.to_csv("data//products_normalized.csv", index=False)

# %%
len(products_normalized)

# %%
for each in products_normalized.columns:
        print(each)

# %%
products_normalized[['id','name','metaData.product_description.ALLERGEN_CONTAINS']]


# Need to simplify the data and make a nut free flag, based on the contents of the text fields

# %%
# list of fields in which there could be Food Allergen information:
allergen_fields = [
    'allergen_text'
]

##products_normalized['nut_free'] = 

# %%
allergen_text_nut_mask = products_normalized['allergen_text'].str.contains('nuts|frutta a guscio', case=False, na=False)
# %%

nut_mask = products_normalized[['id']]
nut_mask['allergen_text'] = allergen_text_nut_mask

# %%
nut_mask


# %%
def get_allergens_from_text(text: str) -> list:
    """
    Extracts allergens from a given text string.

    Args:
        text (str): The input text containing allergen information.

    Returns:
        list: A list of allergens found in the text.   

    """

    allergens = []  # Default to 'None' if no allergens are found
    if pd.isna(text):
        return allergens

    # Define a list of known allergens
    known_allergens = [
        'Frutta a guscio', 'Arachidi', 'Latte', 'Uova', 'Pesce', 'Crostacei', 
        'Molluschi', 'Soia', 'Glutine', 'Sesamo', 'Senape', 'Sedano'
    ]

    # Check for each known allergen in the text
    for allergen in known_allergens:
        if allergen.lower() in text.lower():
            allergens.append(allergen)

    if allergens == []:
        allergens.append('None')  # Add 'None' if no allergens are found

    return allergens

# %%
df_allergens = products_normalized[['id']].assign(allergens=products_normalized['allergen_text'].apply(get_allergens_from_text))
df_allergens['allergens_list'] = df_allergens['allergens']
df_allergens_long = df_allergens.explode('allergens')

# %%
pd.merge(products_normalized, df_allergens_long, on='id', how='left').to_csv("..//data//products_frontend.csv", index=False)


#ToDo - add 'None' to the list of allergens for products that have no allergens listed, so that they can be filtered in the front end
# %%
