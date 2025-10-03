import csv
import pandas as pd
import re
from io import StringIO

input_file = "tmdb-movies.csv"
output_file = "movies-clean.csv"
suspicious_file = "suspicious_records.csv"

# --- Step 1: Detect expected number of columns ---
with open(input_file, encoding="utf-8") as f:
    reader = csv.reader(f)
    lengths = [len(row) for row in reader]
expected_cols = max(set(lengths), key=lengths.count)
print(f"Expected columns: {expected_cols}")

# --- Step 2: Robust CSV parsing ---
fixed_rows = []
with open(input_file, encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    fixed_rows.append(header)

    for row in reader:
        if len(row) == expected_cols:
            fixed_rows.append(row)
        else:
            joined = ','.join(row)
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

# --- Step 3: Convert to DataFrame ---
df = pd.DataFrame(fixed_rows[1:], columns=fixed_rows[0])

# --- Step 4: Column-specific whitelist cleaning ---
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

# --- Step 5: Strip extra whitespace from original_title ---
df['original_title'] = df['original_title'].str.replace(r'\s+', ' ', regex=True).str.strip()

# --- Step 6: Fix ambiguous release dates ---
min_year = 1900
max_year = 2015


def fix_ambiguous_date(date_str):
    """
    Fix dates with ambiguous 2-digit years using min/max year bounds.
    """
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

        # swap month/day if month > 12
        if month > 12 and day <= 12:
            month, day = day, month

        # handle 2-digit years
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

# --- Step 7: Enforce proper types ---
df["id"] = df["id"].astype(str)
df["imdb_id"] = df["imdb_id"].astype(str)
df["popularity"] = df["popularity"].astype(str)
df["budget"] = pd.to_numeric(df["budget"], errors="coerce").fillna(0).astype(int)
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0).astype(int)
df["original_title"] = df["original_title"].astype(str)
df["cast"] = df["cast"].astype(str)
df["homepage"] = df["homepage"].astype(str)
df["director"] = df["director"].astype(str)
df["tagline"] = df["tagline"].astype(str)
df["keywords"] = df["keywords"].astype(str)
df["overview"] = df["overview"].astype(str)
df["runtime"] = pd.to_numeric(df["runtime"], errors="coerce").fillna(0).astype(int)
df["genres"] = df["genres"].astype(str)
df["production_companies"] = df["production_companies"].astype(str)
df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0).astype(int)
df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0.0).astype(float)
df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce").fillna(0).astype(int)
df["budget_adj"] = pd.to_numeric(df["budget_adj"], errors="coerce").fillna(0).astype(int)
df["revenue_adj"] = pd.to_numeric(df["revenue_adj"], errors="coerce").fillna(0).astype(int)

# --- Step 8: Extract suspicious titles (short/numeric/date-like) ---
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
print(f"⚠️ Suspicious records saved to '{suspicious_file}' ({len(suspicious_df)} rows)")

# --- Step 9: Save full clean CSV ---
df.to_csv(output_file, index=False, encoding="utf-8")
print(f"✅ Fully cleaned CSV saved as '{output_file}'")
