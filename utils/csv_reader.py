import pandas as pd

def convert_csv_to_df(file: str):
    csv_df = pd.read_csv(file)
    return csv_df
