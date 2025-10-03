import pandas as pd
from mypy.modulefinder import unique

df = pd.read_csv('clean-data.csv')

#Split
genres_exploded = df['genres'].str.split('|').explode().str.strip()

#Count
genres_count = genres_exploded.value_counts()

print("Movies by Genres:")
print(genres_count)

df.to_csv('genres.csv', index=False)