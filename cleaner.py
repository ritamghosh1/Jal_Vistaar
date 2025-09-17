import pandas as pd
df = pd.read_excel("groundwater_data.xlsx")

df = df.fillna(-1)   # replaces all missing values with -1
df.to_excel("groundwater_data_cleaned.xlsx", index=False)
