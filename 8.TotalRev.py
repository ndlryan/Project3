import pandas as pd

df = pd.read_csv('clean-data.csv')

total_revenue = df["revenue"].sum()

print(total_revenue)

