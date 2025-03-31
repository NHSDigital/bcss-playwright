from utils.oracle.oracle_specific_functions import get_kit_id_from_db
import pandas as pd
from datetime import datetime
import logging


def create_fit_id_df():
    df = get_kit_id_from_db()
    df["fit_device_id"] = df["kitid"].apply(calculate_check_digit)
    df["fit_device_id"] = df["fit_device_id"].apply(convert_kit_id_to_fit_device_id)
    return df

def calculate_check_digit(kitID: str):
    logging.info(f"Calculating check digit for kit id: {kitID}")
    total = 0
    charString = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-. $/+%"
    for i in range(len(kitID)):
        total += charString.index(kitID[i - 1])
    check_digit = charString[total % 43]
    return f"{kitID}-{check_digit}"

def convert_kit_id_to_fit_device_id(kit_id: str):
    logging.info(f"Generating FIT Device ID from: {kit_id}")
    today = datetime.now()
    year = today.strftime("%y")  # Get the year from todays date in YY format
    return f"{kit_id}12{int(year) + 1}12345/KD00001"
