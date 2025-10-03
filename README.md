# 🎬 TMDB Movie Dataset Analysis

## 📊 Executive Summary
 - Dataset Source: TMDB Movies Dataset
 - Dataset Size (raw): 10,866 movies (1960–2015)
 - Cleaning Results:
   * Found 1 duplicate (based on id)
   * After cleaning, 10,865 movies ready for analysis
   * Additional suspicious records flagged (e.g., short original titles) for manual review
     
## 🔑 Key Findings
 - Popularity ≠ Profitability → Correlation only 0.17
 - Risk-Taking (Big Budgets) ≠ Predictable Success → Some of the most expensive movies lost money
 - Few Companies Dominate Profits → A handful of production studios capture the bulk of total profit
 - High-Rated Films (≥7.5) span both small and large budgets → quality does not equal commercial scale

## 🎯 Takeaway
Profitability in movies is not guaranteed by budget, fame, or popularity. Success requires strategic execution, distribution, and cultural resonance — not just spending power.


# 🛠️ Workflow

## 0. Collect
 - Dataset downloaded from: https://raw.githubusercontent.com/yinghaoz1/tmdb-movie-dataset-analysis/master/tmdb-movies.csv

## 1. Prepare & Clean
### 1.1. Index & Character Check
  - Performed index-checking on the raw CSV.
  - Generated "unusual_characters_report.tsv" to log unexpected characters.
  - Defined whitelists for specific columns (e.g., URL fields follow standard RFC 3986 patterns).
  - Assigned proper data types for each column.

### 1.2. Handling Dates (release_date)
  - Release_date field contained ambiguous 2-digit years (e.g., 11/68/31, 01/05/99).
  - Applied logic with bounds [1900, 2015]:
    * "68" → 1968
    * "99" → 1999
    * "15" → 2015
    * "00–15" interpreted as 2000–2015, not 1900–1915.
  - Rule: Closer to the present takes priority.
  - Any unresolvable dates were preserved but marked as missing (NaT).

### 1.3. Suspicious Records
  - Titles with very short original_title were extracted into "suspicious_records.csv"
  - These records were not removed #  from the main dataset, ensuring no analysis bias.

### 1.4. Deduplication
  - Checked primary key: id.
  - Found and removed 1 duplicate, saving as "clean-data.csv"
  - This file is the base dataset for all analyses.

### 1.5. Headers
  - Extracted and stored column headers for later reference.


## 2. Analysis 
##### We used the _adj (inflation-adjusted) columns (budget_adj, revenue_adj) to ensure fair comparisons across decades. This ensures we’re comparing apples to apples
### 2.1. Release Date DESC 
    df_sorted = df.sort_values(by = ["release_date"], ascending = False)

### 2.2. Movies with rating ≥ 7.5 
    filtered = df[df['vote_average'] >= 7.5]
    df_sorted = filtered.sort_values(by = "vote_average", ascending = False)

### 2.3. Revenue Extremes 
    min_rev = df["revenue_adj"].min()
    max_rev = df["revenue_adj"].max()
    
    min_rev_row = df[df["revenue_adj"] == min_rev] [["original_title", "revenue_adj"]]
    max_rev_row = df[df["revenue_adj"] == max_rev] [["original_title", "revenue_adj"]]  

### 2.4. Total Revenue (raw/absolute revenue)
    total_revenue = df["revenue"].sum()

### 2.5. Top 10 Profit Movies
    df["profit"] = df["revenue_adj"] - df["budget_adj"]
    
    #remove Null records
    df_clean = df.dropna(subset=["profit"]) 
    
    df_sorted = df_clean.sort_values(by=["profit"], ascending=False)

    print(df_sorted[["original_title", "profit"]].head(10))

### 2.6. Director / Actor
#### 2.6.1 Director
    #Split
    directors_exploded = df['director'].str.split('|').explode().str.strip()

    #Count
    director_count = directors_exploded.value_counts()

    #Sort
    print("Top Director:")
    print(director_count.head(1))
#### 2.6.1 Actor
    #Split
    cast_exploded = df['cast'].str.split('|').explode().str.strip()

    #Count
    cast_count = cast_exploded.value_counts()

    #Sort
    print("Top Actor:")
    print(cast_count.head(1))

### 2.7. Genres
    #Split
    genres_exploded = df['genres'].str.split('|').explode().str.strip()

    #Count
    genres_count = genres_exploded.value_counts()

### 2.8. [Extra] Top P&L
    df["profit"] = df["revenue_adj"] - df["budget_adj"]

    #remove N/A
    df_clean = df.dropna(subset = ["budget_adj", "profit"]) 

    #ensure no data bias (extremely high profit / negative profit)
    df_clean = df_clean[(df_clean["budget_adj"] > 0) & (df_clean["revenue_adj"] > 0)] 

    top_winners = df_clean.nlargest(10, "profit") [["original_title", "profit", "budget_adj", "revenue_adj"]]
    top_losers = df_clean.nsmallest(10, "profit") [["original_title", "profit", "budget_adj", "revenue_adj"]]

### 2.9. Company with most movies / profit
    #Split by "|"
    companies_exploded = (
    df.assign(production_companies=df["production_companies"].str.split("|"))
      .explode("production_companies")
      .dropna(subset=["production_companies"])

    #Strip whitespace
    companies_exploded["production_companies"] = companies_exploded["production_companies"].str.strip()
#### 2.9.1 Most movies
    top10_movies = (
    companies_exploded["production_companies"]
    .value_counts()
    .head(10)
#### 2.9.2 Most profit
top10_profit = (
    companies_exploded.groupby("production_companies")["profit"]
    .sum()
    .sort_values(ascending=False)
    .head(10)


## 3. The Viz
### 3.1 Profit vs Popularity (scatter plot): 
   <img width="1000" height="600" alt="Figure_1" src="https://github.com/user-attachments/assets/3db20e3e-1044-4e91-bdc6-8eae3c8ee022" />
  
  - Top 100 most popular movies.
    
  - Correlation coefficient ≈ 0.17 (very weak).

  - Insight: Popularity ≠ Profitability.

### 3.2 Budget vs Profit (scatter plot): 
   <img width="1200" height="700" alt="Figure_2" src="https://github.com/user-attachments/assets/fedd225d-b4a8-4ce1-b4b5-51baffcbe2a2" />

  - Scatter plot across dataset.

  - Shows that higher budgets do not guarantee higher profits.

  - Insight: Risk-taking ≠ Predictable. Only a few companies consistently convert spend into return.

## 4. Key Insights
  - Popular ≠ Profitable
  - Many widely known movies failed to earn strong profits. Popularity alone is a weak predictor of financial success.

  - Risk-taking (budget) ≠ Predictable
  - High budgets create high stakes but not guaranteed returns. Only certain studios manage to convert spend into reliable profits.
