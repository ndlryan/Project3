import pandas as pd
import csv
import re

filename = "tmdb-movies.csv"
output_file = "unusual_characters_report.tsv"

# --- Step 1: Check column consistency ---
with open(filename, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    lengths = [len(row) for row in reader]

expected = max(set(lengths), key=lengths.count)  # most common length
bad_rows = [i for i, l in enumerate(lengths) if l != expected]

print(f"✅ Expected columns: {expected}")
print(f"📊 Total rows: {len(lengths)}")
print(f"⚠️ Problematic rows (wrong number of columns): {len(bad_rows)}")
if bad_rows:
    print("   Sample bad row indices:", bad_rows[:10])
print("-" * 80)

# --- Step 2: Load safely with pandas ---
df = pd.read_csv(filename, engine="python", on_bad_lines="warn")

# --- Step 3: Character diagnostics per column ---
base_whitelist = re.compile(r"[a-zA-Z0-9\s\.\,\-\(\):]")

# Prepare a DataFrame to store results
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

# Convert to DataFrame and save as TSV
report_df = pd.DataFrame(report_rows)
report_df.to_csv(output_file, sep="\t", index=False, encoding="utf-8")

print(f"✅ Unusual character report saved to '{output_file}'")
