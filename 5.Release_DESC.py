import pandas as pd

df = pd.read_csv('clean-data.csv')

df_sorted = df.sort_values(by = ["release_date"], ascending = False)

print(df_sorted[["original_title", "release_date"]])

df.to_csv('release_desc.csv', index = False)