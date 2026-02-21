import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data")

for file in os.listdir(DATA_PATH):
    if file.endswith(".csv"):
        df = pd.read_csv(os.path.join(DATA_PATH, file))
        print(f"{file} → Shape: {df.shape}")
        print(df.head())
        print("\n")