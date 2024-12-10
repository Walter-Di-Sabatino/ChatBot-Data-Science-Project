import pandas as pd

# Carica i due file CSV
df1 = pd.read_csv('lookup_files/genres_names.csv', header=None)
df2 = pd.read_csv('lookup_files/tags_names.csv', header=None)

# Confronta le righe della colonna dei due file
differenze1 = df1[~df1[0].isin(df2[0])]

# Stampa le righe che non sono presenti nell'altro file
print("Righe in file1 che non sono in file2:")
print(differenze1)

# Solo Accounting c'è di pù quindi gestisco tag come genre