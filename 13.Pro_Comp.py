import pandas as pd

# Load dataset
df = pd.read_csv("clean-data.csv")

# Ensure profit is computed
df["profit"] = df["revenue_adj"] - df["budget_adj"]

# --- Step 1: Explode production_companies ---
companies_exploded = (
    df.assign(production_companies=df["production_companies"].str.split("|"))
      .explode("production_companies")
      .dropna(subset=["production_companies"])
)

# Strip whitespace
companies_exploded["production_companies"] = companies_exploded["production_companies"].str.strip()

# --- Step 2: Top 10 by number of movies ---
top10_movies = (
    companies_exploded["production_companies"]
    .value_counts()
    .head(10)
)

print("🎬 Top 10 Production Companies by Number of Movies:")
print(top10_movies)

# --- Step 3: Top 10 by total profit ---
top10_profit = (
    companies_exploded.groupby("production_companies")["profit"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n💰 Top 10 Production Companies by Total Profit:")
print(top10_profit)

df.to_csv("TopCompany.csv", index=False)