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

0. Collect
 - Dataset downloaded from:
https://raw.githubusercontent.com/yinghaoz1/tmdb-movie-dataset-analysis/master/tmdb-movies.csv
