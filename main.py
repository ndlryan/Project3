#!/usr/bin/env python3
# main.py
"""
TMDB Movie Deep Clean Analysis - Combined Main Script
Integrates all 15 analysis scripts into a single sequential pipeline.
"""

import pandas as pd
import csv
import re
from io import StringIO
import logging
import sys
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------
# Configure Logging
# ------------------------------

logging.basicConfig(
    filename="tmdb_analysis.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------------------
# Step 0: Download / Read Dataset
# ------------------------------

def get_file():
    logging.info("Step 0: Downloading dataset...")
    try:
        url = "https://raw.githubusercontent.com/yinghaoz1/tmdb-movie-dataset-analysis/master/tmdb-movies.csv"
        df = pd.read_csv(url)
        df.to_csv("tmdb-movies.csv", index=False)
        logging.info(f"Dataset downloaded and saved as tmdb-movies.csv, shape: {df.shape}")
        return df
    except Exception as e:
        logging.error(f"Failed to download/load dataset: {e}")
        sys.exit(1)

# ------------------------------
# Step 1: Unusual Character Report
# ------------------------------

def index_check(df):
    logging.info("Step 1: Generating unusual character report...")
    base_whitelist = re.compile(r"[a-zA-Z0-9\s\.\,\-\(\):]")
    report_rows = []

    for col in df.columns:
        if df[col].dtype == "object":
            joined = " ".join(df[col].dropna().astype(str).values)
            unusual_chars = [ch for ch in set(joined) if not base_whitelist.match(ch)]
            if unusual_chars:
                freq = pd.Series(list(joined)).value_counts()
                for ch in unusual_chars:
                    report_rows.append({
                        "column": col,
                        "character": ch,
                        "occurrences": freq[ch]
                    })

    report_df = pd.DataFrame(report_rows)
    report_df.to_csv("unusual_characters_report.tsv", sep="\t", index=False, encoding="utf-8")
    logging.info(f"Unusual character report saved, rows found: {len(report_df)}")
    return df

# ------------------------------
# Step 2: Index Clean / Full CSV Cleaning
# ------------------------------

def index_clean(df):
    logging.info("Step 2: Cleaning CSV data...")
    input_file = "tmdb-movies.csv"
    output_file = "movies-clean.csv"
    suspicious_file = "suspicious_records.csv"

    with open(input_file, encoding="utf-8") as f:
        reader = csv.reader(f)
        lengths = [len(row) for row in reader]
    expected_cols = max(set(lengths), key=lengths.count)

    fixed_rows = []
    with open(input_file, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        fixed_rows.append(header)
        for row in reader:
            if len(row) == expected_cols:
                fixed_rows.append(row)
            else:
                joined = ",".join(row)
                try:
                    temp_df = pd.read_csv(StringIO(joined), header=None)
                    if temp_df.shape[1] == expected_cols:
                        fixed_rows.append(temp_df.iloc[0].tolist())
                    else:
                        row_fixed = row[:expected_cols] + ['']*(expected_cols-len(row))
                        fixed_rows.append(row_fixed)
                except Exception:
                    row_fixed = row[:expected_cols] + ['']*(expected_cols-len(row))
                    fixed_rows.append(row_fixed)

    df = pd.DataFrame(fixed_rows[1:], columns=fixed_rows[0])

    # Column-specific whitelist cleaning
    def clean_column(series, whitelist_pattern):
        regex = re.compile(f"[^{whitelist_pattern}]")
        return series.fillna("").astype(str).apply(lambda x: regex.sub("", x))

    column_whitelists = {
        "cast": r"a-zA-Z0-9\s\|",
        "homepage": r"a-zA-Z0-9:/?#\[\]@!$&'()*+,;=\-._~",
        "director": r"a-zA-Z0-9\s\|",
        "tagline": r"a-zA-Z0-9\s,\"\!\?",
        "keywords": r"a-zA-Z0-9\s\|",
        "overview": r"a-zA-Z0-9\s\'!\?.,\-():",
        "genres": r"a-zA-Z0-9\s\|",
        "production_companies": r"a-zA-Z0-9\s/\-&|.,()",
        "original_title": r"a-zA-Z0-9\s!\'.,\-():",
    }

    for col, pattern in column_whitelists.items():
        if col in df.columns:
            df[col] = clean_column(df[col], pattern)

    df['original_title'] = df['original_title'].str.replace(r'\s+', ' ', regex=True).str.strip()

    # Fix release dates
    min_year = 1900
    max_year = 2015
    def fix_ambiguous_date(date_str):
        if pd.isna(date_str) or not date_str.strip():
            return pd.NaT
        parts = date_str.split('/')
        if len(parts) != 3:
            return pd.NaT
        month, day, year = parts
        try:
            month = int(month)
            day = int(day)
            year = int(year)
            if month > 12 and day <= 12:
                month, day = day, month
            if year < 100:
                year_2000 = 2000 + year
                year_1900 = 1900 + year
                if min_year <= year_2000 <= max_year:
                    year = year_2000
                elif min_year <= year_1900 <= max_year:
                    year = year_1900
                else:
                    return pd.NaT
            return pd.to_datetime(f"{year}-{month:02d}-{day:02d}")
        except Exception:
            return pd.NaT

    df["release_date"] = df["release_date"].apply(fix_ambiguous_date)
    df["release_date"] = df["release_date"].dt.strftime("%Y-%m-%d")

    # Enforce proper types
    numeric_cols = ["budget", "revenue", "runtime", "vote_count", "vote_average",
                    "release_year", "budget_adj", "revenue_adj"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    str_cols = ["id","imdb_id","original_title","cast","homepage","director",
                "tagline","keywords","overview","genres","production_companies","popularity"]
    for col in str_cols:
        df[col] = df[col].astype(str)

    # Suspicious titles
    def is_suspicious_title(title):
        t = str(title).strip()
        if len(t) <= 2 or t.isdigit() or re.match(r'\d{4}-\d{2}-\d{2}', t):
            return True
        return False

    suspicious_df = df[df["original_title"].apply(is_suspicious_title)].copy()
    suspicious_df["suspicious_aspect"] = suspicious_df["original_title"].apply(
        lambda t: "short/numeric/date-like"
    )
    suspicious_df.to_csv(suspicious_file, index=False, encoding="utf-8")
    logging.info(f"Suspicious records saved: {len(suspicious_df)} rows")

    df.to_csv(output_file, index=False, encoding="utf-8")
    logging.info(f"Cleaned CSV saved as {output_file}")
    return df

# ------------------------------
# Step 3: Deduplication
# ------------------------------

def remove_duplicates(df):
    logging.info("Step 3: Removing duplicates...")
    df.drop_duplicates("id", keep="first", inplace=True)
    df.to_csv("clean-data.csv", index=False)
    return df

# ------------------------------
# Step 4: Review Headers
# ------------------------------

def clean_headers(df):
    logging.info("Step 4: Reviewing headers...")
    print(df.columns.tolist())
    return df

# ------------------------------
# Step 5: Movies Release Date Desc
# ------------------------------

def release_desc(df):
    logging.info("Step 5: Sort by release date descending...")
    df_sorted = df.sort_values(by=["release_date"], ascending=False)
    print(df_sorted[["original_title", "release_date"]].head(10))
    df.to_csv("release_desc.csv", index=False)
    return df

# ------------------------------
# Step 6: Movie Avg Rate
# ------------------------------

def avg_rating(df):
    logging.info("Step 6: Filter top rated movies...")
    filtered = df[df['vote_average'] >= 7.5]
    df_sorted = filtered.sort_values(by="vote_average", ascending=False)
    print(df_sorted[["original_title", "vote_average"]].head(10))
    df.to_csv("avg_rate.csv", index=False)
    return df

# ------------------------------
# Step 7: Min/Max Revenue
# ------------------------------

def min_max(df):
    logging.info("Step 7: Min/Max Revenue...")
    min_rev = df["revenue_adj"].min()
    max_rev = df["revenue_adj"].max()
    print("Lowest revenue:")
    print(df[df["revenue_adj"] == min_rev][["original_title", "revenue_adj"]])
    print("Highest revenue:")
    print(df[df["revenue_adj"] == max_rev][["original_title", "revenue_adj"]])
    df.to_csv("Min_max.csv", index=False)
    return df

# ------------------------------
# Step 8: Total Movies Revenue
# ------------------------------

def total_revenue(df):
    logging.info("Step 8: Total revenue calculation...")
    total_revenue_val = df["revenue"].sum()
    print(f"Total revenue: {total_revenue_val}")
    return df

# ------------------------------
# Step 9: Top 10 Profit Movies
# ------------------------------

def top_profit(df):
    logging.info("Step 9: Top 10 profit movies...")
    df["profit"] = df["revenue_adj"] - df["budget_adj"]
    df_clean = df.dropna(subset=["profit"])
    df_sorted = df_clean.sort_values(by="profit", ascending=False)
    print(df_sorted[["original_title", "profit"]].head(10))
    df.to_csv("top10_profit.csv", index=False)
    return df

# ------------------------------
# Step 10: Top Director / Actor
# ------------------------------

def top_dir_actor(df):
    logging.info("Step 10: Top director and actor...")
    directors_exploded = df['director'].str.split('|').explode().str.strip()
    director_count = directors_exploded.value_counts()
    print("Top Director:")
    print(director_count.head(1))

    cast_exploded = df['cast'].str.split('|').explode().str.strip()
    cast_count = cast_exploded.value_counts()
    print("Top Actor:")
    print(cast_count.head(1))

    df.to_csv("Dir-Act.csv", index=False)
    return df

# ------------------------------
# Step 11: Movies by Genres
# ------------------------------

def movies_by_genres(df):
    logging.info("Step 11: Movies by genres...")
    genres_exploded = df['genres'].str.split('|').explode().str.strip()
    genres_count = genres_exploded.value_counts()
    print("Movies by Genres:")
    print(genres_count)
    df.to_csv("genres.csv", index=False)
    return df

# ------------------------------
# Step 12: Top P&L Movies
# ------------------------------

def top_pnl(df):
    logging.info("Step 12: Top P&L movies...")
    df["profit"] = df["revenue_adj"] - df["budget_adj"]
    df_clean = df.dropna(subset=["budget_adj","profit"])
    df_clean = df_clean[(df_clean["budget_adj"] > 0) & (df_clean["revenue_adj"] > 0)]
    top_winners = df_clean.nlargest(10, "profit")[["original_title","profit","budget_adj","revenue_adj"]]
    top_losers = df_clean.nsmallest(10, "profit")[["original_title","profit","budget_adj","revenue_adj"]]
    print("\nTop 10 Most Profitable Movies:")
    print(top_winners.to_string(index=False))
    print("\nTop 10 Biggest Losses:")
    print(top_losers.to_string(index=False))
    df.to_csv("TopP&L.csv", index=False)
    return df

# ------------------------------
# Step 13: Top Company
# ------------------------------

def top_company(df):
    logging.info("Step 13: Top production companies...")
    df["profit"] = df["revenue_adj"] - df["budget_adj"]
    companies_exploded = (
        df.assign(production_companies=df["production_companies"].str.split("|"))
          .explode("production_companies")
          .dropna(subset=["production_companies"])
    )
    companies_exploded["production_companies"] = companies_exploded["production_companies"].str.strip()
    top10_movies = companies_exploded["production_companies"].value_counts().head(10)
    print("Top 10 Production Companies by Number of Movies:")
    print(top10_movies)
    top10_profit = companies_exploded.groupby("production_companies")["profit"].sum().sort_values(ascending=False).head(10)
    print("\nTop 10 Production Companies by Total Profit:")
    print(top10_profit)
    df.to_csv("TopCompany.csv", index=False)
    return df

# ------------------------------
# Step 14: Viz Popularity vs Profit
# ------------------------------

def viz_popularity_profit(df):
    logging.info("Step 14: Visualization of Popularity vs Profit")
    df["profit"] = df["revenue_adj"] - df["budget_adj"]
    df_clean = df.dropna(subset=["profit","popularity"])
    top100 = df_clean.sort_values(by="popularity", ascending=False).head(100)

    plt.figure(figsize=(10,6))
    plt.scatter(top100["popularity"], top100["profit"], alpha=0.7)
    plt.title("Profit vs Popularity (Top 100 Most Popular Movies)")
    plt.xlabel("Popularity")
    plt.ylabel("Profit (Adjusted)")
    plt.grid(True)
    plt.show()

    correlation = top100["popularity"].corr(top100["profit"])
    print(f"Correlation between Popularity and Profit (Top 100 movies): {correlation:.3f}")
    return df

# ------------------------------
# Step 15: Viz Budget vs Profit
# ------------------------------

def viz_budget_profit(df):
    logging.info("Step 15: Visualization of Budget vs Profit")
    df["profit"] = df["revenue_adj"] - df["budget_adj"]
    df_clean = df.dropna(subset=["budget_adj","profit"])
    df_clean = df_clean[df_clean["budget_adj"] > 0]

    plt.figure(figsize=(12,7))
    plt.scatter(df_clean["budget_adj"], df_clean["profit"], alpha=0.5, s=20)
    plt.xscale("log")
    plt.title("Budget vs Profit (All Movies)")
    plt.xlabel("Budget (log scale, Adjusted)")
    plt.ylabel("Profit (Adjusted)")
    plt.grid(True, linestyle="--", alpha=0.7)

    x = np.log10(df_clean["budget_adj"])
    y = df_clean["profit"]
    coef = np.polyfit(x, y, 1)
    trend = np.poly1d(coef)
    plt.plot(df_clean["budget_adj"], trend(np.log10(df_clean["budget_adj"])), color="red", linewidth=2, label="Trend line")

    top_winners = df_clean.nlargest(3, "profit")
    top_losers = df_clean.nsmallest(3, "profit")
    for _, row in pd.concat([top_winners, top_losers]).iterrows():
        plt.annotate(
            row["original_title"],
            (row["budget_adj"], row["profit"]),
            textcoords="offset points",
            xytext=(5,5),
            ha="left",
            fontsize=8,
            color="darkred" if row["profit"] < 0 else "darkgreen"
        )
    plt.legend()
    plt.show()
    return df

# ------------------------------
# Main Execution
# ------------------------------

def main():
    df = get_file()
    df = index_check(df)
    df = index_clean(df)
    df = remove_duplicates(df)
    df = clean_headers(df)
    df = release_desc(df)
    df = avg_rating(df)
    df = min_max(df)
    df = total_revenue(df)
    df = top_profit(df)
    df = top_dir_actor(df)
    df = movies_by_genres(df)
    df = top_pnl(df)
    df = top_company(df)
    df = viz_popularity_profit(df)
    df = viz_budget_profit(df)
    logging.info("All steps completed successfully.")

if __name__ == "__main__":
    main()
