import pandas as pd

df = pd.read_excel('mts.xlsx', sheet_name=0)
print("Форма файла:", df.shape)
print("\nПервые 10 строк:")
print(df.head(10))
print("\nНазвания колонок:")
print(df.columns.tolist())