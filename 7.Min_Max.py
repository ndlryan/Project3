import pandas as pd

df = pd.read_csv('clean-data.csv')

#pandas automatically ignores NaN for min()/max()
min_rev = df["revenue_adj"].min()
max_rev = df["revenue_adj"].max()

min_rev_row = df[df["revenue_adj"] == min_rev] [["original_title", "revenue_adj"]]
max_rev_row = df[df["revenue_adj"] == max_rev] [["original_title", "revenue_adj"]]

print("Lowest revenue:")
print(min_rev_row)
print("\nHighest revenue:")
print(max_rev_row)

df.to_csv('Min_max.csv', index = False)