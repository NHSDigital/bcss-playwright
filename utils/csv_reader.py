import pandas as pd

def csv_reader(file: str):
    csv_df = pd.read_csv(file)
    return csv_df
