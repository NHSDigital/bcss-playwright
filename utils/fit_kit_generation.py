from utils.oracle.oracle_specific_functions import get_kit_id_from_db
import pandas as pd
from datetime import datetime
import logging


def create_fit_id_df() -> pd.DataFrame:
    df = get_kit_id_from_db()
    df["fit_device_id"] = df["kitid"].apply(calculate_check_digit)
    df["fit_device_id"] = df["fit_device_id"].apply(convert_kit_id_to_fit_device_id)
    return df

def calculate_check_digit(kit_id: str) -> str:
    logging.info(f"Calculating check digit for kit id: {kit_id}")
    total = 0
    char_string = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-. $/+%"
    for i in range(len(kit_id)):
        total += char_string.index(kit_id[i - 1])
    check_digit = char_string[total % 43]
    return f"{kit_id}-{check_digit}"

def convert_kit_id_to_fit_device_id(kit_id: str) -> str:
    logging.info(f"Generating FIT Device ID from: {kit_id}")
    today = datetime.now()
    year = today.strftime("%y")  # Get the year from todays date in YY format
    return f"{kit_id}12{int(year) + 1}12345/KD00001"
