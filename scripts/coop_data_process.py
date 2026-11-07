
# %%
import pandas as pd

# %%
products_raw = pd.read_json("data//products.json")

products_normalized = pd.json_normalize(products_raw['products'])

# %%

products_normalized.to_csv("data//products_normalized.csv", index=False)

# %%
