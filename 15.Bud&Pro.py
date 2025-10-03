import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load dataset
df = pd.read_csv("clean-data.csv")

# Create profit column
df["profit"] = df["revenue_adj"] - df["budget_adj"]

# Drop rows with missing values
df_clean = df.dropna(subset=["budget_adj", "profit"])
df_clean = df_clean[df_clean["budget_adj"] > 0]

# Scatter plot
plt.figure(figsize=(12, 7))
plt.scatter(df_clean["budget_adj"], df_clean["profit"], alpha=0.5, s=20)

plt.xscale("log")
plt.title("Budget vs Profit (All Movies)")
plt.xlabel("Budget (log scale, Adjusted)")
plt.ylabel("Profit (Adjusted)")
plt.grid(True, linestyle="--", alpha=0.7)

# Regression line (using log(budget) to match scale)
x = np.log10(df_clean["budget_adj"])
y = df_clean["profit"]

# Fit linear regression in log scale
coef = np.polyfit(x, y, 1)
trend = np.poly1d(coef)

plt.plot(
    df_clean["budget_adj"],
    trend(np.log10(df_clean["budget_adj"])),
    color="red",
    linewidth=2,
    label="Trend line"
)

# Identify top winners and losers
top_winners = df_clean.nlargest(3, "profit")
top_losers = df_clean.nsmallest(3, "profit")

# Annotate outliers
for _, row in pd.concat([top_winners, top_losers]).iterrows():
    plt.annotate(
        row["original_title"],
        (row["budget_adj"], row["profit"]),
        textcoords="offset points",
        xytext=(5, 5),
        ha="left",
        fontsize=8,
        color="darkred" if row["profit"] < 0 else "darkgreen"
    )

plt.legend()
plt.show()
