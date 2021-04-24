import csv
import pandas as pd
from pathlib import Path

CSV_PATH = '/Users/Alex/Desktop/Test_Export v2.csv'

df = pd.read_csv(CSV_PATH)

duplicate_rows_df = df[df.duplicated(['ID'])]
print(duplicate_rows_df['ID'])