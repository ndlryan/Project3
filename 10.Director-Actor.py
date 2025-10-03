import pandas as pd

df = pd.read_csv('clean-data.csv')

#-----Director-----
#Split
directors_exploded = df['director'].str.split('|').explode().str.strip()

#Count
director_count = directors_exploded.value_counts()

#Sort
print("Top Director:")
print(director_count.head(1))

#-----Actor-----
#Split
cast_exploded = df['cast'].str.split('|').explode().str.strip()

#Count
cast_count = cast_exploded.value_counts()

#Sort
print("Top Actor:")
print(cast_count.head(1))

df.to_csv('Dir-Act.csv', index = False)