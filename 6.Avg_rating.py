import pandas as pd

df = pd.read_csv('clean-data.csv')

filtered = df[df['vote_average'] >= 7.5]

df_sorted = filtered.sort_values(by = "vote_average", ascending = False)

print(df_sorted[["original_title", "vote_average"]])

df.to_csv('avg_rate.csv', index = False)