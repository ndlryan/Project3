import pandas as pd

df = pd.read_csv('clean-data.csv')

df["profit"] = df["revenue_adj"] - df["budget_adj"]

df_clean = df.dropna(subset = ["budget_adj", "profit"])
df_clean = df_clean[(df_clean["budget_adj"] > 0) & (df_clean["revenue_adj"] > 0)]

top_winners = df_clean.nlargest(10, "profit") [["original_title", "profit", "budget_adj", "revenue_adj"]]
top_losers = df_clean.nsmallest(10, "profit") [["original_title", "profit", "budget_adj", "revenue_adj"]]

print("\nTop 10 Most Profitable Movies:")
print(top_winners.to_string(index=False))

print("\nTop 10 Biggest Losses:")
print(top_losers.to_string(index=False))

df.to_csv('TopP&L.csv', index=False)