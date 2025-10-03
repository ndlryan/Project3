import pandas as pd

df = pd.read_csv('movies-clean.csv')

duplicate = df[df.duplicated("id", keep = False)]
print(duplicate)

df.drop_duplicates("id", keep = "first", inplace = True)

df.to_csv('clean-data.csv', index = False)