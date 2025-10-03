import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("clean-data.csv")

# Create profit column
df["profit"] = df["revenue_adj"] - df["budget_adj"]

# Drop rows with missing popularity or profit
df_clean = df.dropna(subset=["profit", "popularity"])

# Select top 100 movies by popularity
top100 = df_clean.sort_values(by="popularity", ascending=False).head(100)

# Scatter plot: Profit vs Popularity
plt.figure(figsize=(10, 6))
plt.scatter(top100["popularity"], top100["profit"], alpha=0.7)
plt.title("Profit vs Popularity (Top 100 Most Popular Movies)")
plt.xlabel("Popularity")
plt.ylabel("Profit (Adjusted)")
plt.grid(True)
plt.show()

# Calculate correlation (Pearson's r)
correlation = top100["popularity"].corr(top100["profit"])
print(f"Correlation between Popularity and Profit (Top 100 movies): {correlation:.3f}")
