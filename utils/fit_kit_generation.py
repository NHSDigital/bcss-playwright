from oracle import OracleDB
import pandas as pd
from datetime import datetime
import logging


def create_fit_id_df():
    df = get_kit_id_from_db()
    df["fit_device_id"] = df["kitid"].apply(calculate_check_digit)
    df["fit_device_id"] = df["fit_device_id"].apply(convert_kit_id_to_fit_device_id)
    return df


def get_kit_id_from_db():
    logging.info("Retrieving useable test kit ids")
    kit_id_df = OracleDB().execute_query("""select tk.kitid, tk.screening_subject_id, sst.subject_nhs_number
    from tk_items_t tk
    inner join ep_subject_episode_t se on se.screening_subject_id = tk.screening_subject_id
    inner join screening_subject_t sst on (sst.screening_subject_id = tk.screening_subject_id)
    inner join sd_contact_t sdc on (sdc.nhs_number = sst.subject_nhs_number)
    where tk.tk_type_id = 2
    and tk.logged_in_flag = 'N'
    and sdc.hub_id = 23159
    and device_id is null
    and tk.invalidated_date is null
    and se.latest_event_status_id in (11198, 11213)
    fetch first 10 rows only""")

    return kit_id_df


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
