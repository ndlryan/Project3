import pandas as pd

df = pd.read_csv('clean-data.csv')

df["profit"] = df["revenue_adj"] - df["budget_adj"]

df_clean = df.dropna(subset=["profit"]) #remove Null records

df_sorted = df_clean.sort_values(by=["profit"], ascending=False)

print(df_sorted[["original_title", "profit"]].head(10))

df.to_csv('top10_profit.csv', index=False)