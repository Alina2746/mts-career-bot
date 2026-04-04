# -*- coding: utf-8 -*-
import pandas as pd
import json

df = pd.read_excel('mts.xlsx', sheet_name=0)

vacancies = []
current = None

for idx, row in df.iterrows():
    col0 = row.iloc[0] if len(row) > 0 else None
    col1 = row.iloc[1] if len(row) > 1 else None
    col2 = row.iloc[2] if len(row) > 2 else None
    
    first = str(col0) if pd.notna(col0) else ''
    second = str(col1) if pd.notna(col1) else ''
    third = str(col2) if pd.notna(col2) else ''
    
    skip_words = ['nan', 'None', '']
    
    if first not in skip_words and len(first) > 3:
        if current is not None:
            vacancies.append(current)
        current = {'title': first, 'requirements': [], 'responsibilities': []}
    
    if current is not None:
        if second not in skip_words and len(second) > 2:
            current['requirements'].append(second)
        if third not in skip_words and len(third) > 2:
            current['responsibilities'].append(third)

if current is not None:
    vacancies.append(current)

with open('vacancies.json', 'w', encoding='utf-8') as f:
    json.dump(vacancies, f, ensure_ascii=False, indent=2)

print('Done! Found:', len(vacancies))
for v in vacancies:
    print('-', v['title'])