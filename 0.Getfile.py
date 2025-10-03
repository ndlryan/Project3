import pandas as pd

url = "https://raw.githubusercontent.com/yinghaoz1/tmdb-movie-dataset-analysis/master/tmdb-movies.csv"
df = pd.read_csv(url)

df.to_csv('tmdb-movies.csv', index=False)

print("Saved as tmdb-movies.csv")
