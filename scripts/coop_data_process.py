
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


