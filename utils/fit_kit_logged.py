from oracle import OracleDB
import pandas as pd
from datetime import datetime
import logging



def process_kit_data():
    # Get test data for compartment 3
    kit_id_df = get_kit_id_logged_from_db()

    # Split dataframe into two different dataframes, normal and abnormal
    normal_fit_kit_df, abnormal_fit_kit_df = split_fit_kits(kit_id_df)

    # Prepare a list to store device IDs and their respective flags
    device_ids = []

    # Process normal kits (only 1)
    if not normal_fit_kit_df.empty:
        device_id = normal_fit_kit_df["device_id"].iloc[0]
        logging.info(f"Processing normal kit with Device ID: {device_id}")  # Logging normal device_id
        device_ids.append((device_id, True))  # Add to the list with normal flag
    else:
        logging.warning("No normal kits found for processing.")  # Log warning

        # Process abnormal kits (multiple, loop through)
    if not abnormal_fit_kit_df.empty:
        for index, row in abnormal_fit_kit_df.iterrows():
            device_id = row["device_id"]
            logging.info(f"Processing abnormal kit with Device ID: {device_id}")  # Logging abnormal device_id
            device_ids.append((device_id, False))  # Add to the list with abnormal flag
    else:
        logging.warning("No abnormal kits found for processing.")  # Log warning

    return device_ids


def get_kit_id_logged_from_db():
    kit_id_df = OracleDB().execute_query("""SELECT tk.kitid,tk.device_id,tk.screening_subject_id
FROM tk_items_t tk
INNER JOIN kit_queue kq ON kq.device_id = tk.device_id
INNER JOIN ep_subject_episode_t se ON se.screening_subject_id = tk.screening_subject_id
WHERE tk.logged_in_flag = 'Y'
AND kq.test_kit_status IN ('LOGGED', 'POSTED')
AND se.episode_status_id = 11352
AND tk.tk_type_id = 3
AND se.latest_event_status_id = 11223
AND tk.logged_in_at = 23159
AND tk.reading_flag = 'N'
AND tk.test_results IS NULL
fetch first 10 rows only""")

    return kit_id_df


def split_fit_kits(kit_id_df):
    number_of_normal = 1
    number_of_abnormal = 9
    # Split dataframe into two dataframes
    normal_fit_kit_df = kit_id_df.iloc[:number_of_normal]
    abnormal_fit_kit_df = kit_id_df.iloc[number_of_normal:number_of_normal + number_of_abnormal]
    return normal_fit_kit_df, abnormal_fit_kit_df


def get_service_management_by_device_id(deviceid):
    get_service_management_df = OracleDB().execute_query(f"""SELECT kq.device_id, kq.test_kit_name, kq.test_kit_type, kq.test_kit_status,
    CASE WHEN tki.logged_in_flag = 'Y' THEN kq.logged_by_hub END AS logged_by_hub,
    CASE WHEN tki.logged_in_flag = 'Y' THEN kq.date_time_logged END AS date_time_logged,
    tki.logged_in_on AS tk_logged_date_time, kq.test_result, kq.calculated_result,
    kq.error_code,
    (SELECT vvt.description
    FROM tk_analyser_t tka
    INNER JOIN tk_analyser_type_error tkate ON tkate.tk_analyser_type_id = tka.tk_analyser_type_id
    INNER JOIN valid_values vvt ON tkate.tk_analyser_error_type_id = vvt.valid_value_id
    WHERE tka.analyser_code = kq.analyser_code AND tkate.error_code = kq.error_code)
    AS analyser_error_description, kq.analyser_code, kq.date_time_authorised,
    kq.authoriser_user_code, kq.datestamp, kq.bcss_error_id,
    REPLACE(mt.description, 'ERROR - ', '') AS error_type,
    NVL(mta.allowed_value, 'N') AS error_ok_to_archive,
    kq.post_response, kq.post_attempts, kq.put_response,
    kq.put_attempts, kq.date_time_error_archived,
    kq.error_archived_user_code, sst.screening_subject_id,
    sst.subject_nhs_number, tki.test_results, tki.issue_date,
    o.org_code AS issued_by_hub
    FROM kit_queue kq
    LEFT OUTER JOIN tk_items_t tki ON tki.device_id = kq.device_id
    OR (tki.device_id IS NULL AND tki.kitid = pkg_test_kit.f_get_kit_id_from_device_id(kq.device_id))
    LEFT OUTER JOIN screening_subject_t sst ON sst.screening_subject_id = tki.screening_subject_id
    LEFT OUTER JOIN ep_subject_episode_t ep ON ep.subject_epis_id = tki.subject_epis_id
    LEFT OUTER JOIN message_types mt ON kq.bcss_error_id = mt.message_type_id
    LEFT OUTER JOIN valid_values mta ON mta.valid_value_id = mt.message_attribute_id AND mta.valid_value_id = 305482
    LEFT OUTER JOIN ORG o ON ep.start_hub_id = o.org_id
    LEFT OUTER JOIN ORG lo ON lo.org_code = kq.logged_by_hub
    WHERE kq.test_kit_type = 'FIT' AND kq.device_id = '{deviceid}'
    """)
    return get_service_management_df


def execute_stored_procedures():
    db_instance = OracleDB()  # Create an instance of the OracleDB class
    logging.info("start: oracle.OracleDB.execute_stored_procedure")
    db_instance.execute_stored_procedure('PKG_TEST_KIT_QUEUE.p_validate_kit_queue') # Run stored procedure - validate kit queue
    db_instance.execute_stored_procedure('PKG_TEST_KIT_QUEUE.p_calculate_result') # Run stored procedure - calculate result
    logging.info("exit: oracle.OracleDB.execute_stored_procedure")



def update_kit_service_management_entity(device_id, normal):
    get_service_management_df = get_service_management_by_device_id(device_id)

    # Extract the NHS number from the DataFrame
    subject_nhs_number = get_service_management_df["subject_nhs_number"].iloc[0]
    test_kit_name = get_service_management_df["test_kit_name"].iloc[0]
    test_kit_type = get_service_management_df["test_kit_type"].iloc[0]
    logged_by_hub = get_service_management_df["logged_by_hub"].iloc[0]
    date_time_logged = get_service_management_df["date_time_logged"].iloc[0]
    calculated_result = get_service_management_df["calculated_result"].iloc[0]
    post_response = get_service_management_df["post_response"].iloc[0]
    post_attempts = get_service_management_df["post_attempts"].iloc[0]
    put_response = get_service_management_df["put_response"].iloc[0]
    put_attempts = get_service_management_df["put_attempts"].iloc[0]
    # format date
    date_time_authorised = datetime.now().strftime("%d-%b-%y %H.%M.%S.") + f"{datetime.now().microsecond:06d}000"
    if normal:
        test_result = 75
    else:
        test_result = 150
        # Parameterized query
    update_query = """
    UPDATE kit_queue kq
    SET kq.test_kit_name = :test_kit_name,
    kq.test_kit_type = :test_kit_type,
    kq.test_kit_status =:test_kit_status,
    kq.logged_by_hub = :logged_by_hub,
    kq.date_time_logged = :date_time_logged,
    kq.test_result = :test_result,
    kq.calculated_result = :calculated_result,
    kq.error_code = NULL,
    kq.analyser_code = '3Wjvy',
    kq.date_time_authorised = TO_TIMESTAMP(:date_time_authorised, 'DD-Mon-YY HH24.MI.SS.FF9'),
    kq.authoriser_user_code = 'AUTO1',
    kq.post_response = :post_response,
    kq.post_attempts = :post_attempts,
    kq.put_response = :put_response,
    kq.put_attempts = :put_attempts
    WHERE kq.device_id = :device_id
    """

    # Parameters dictionary
    params = {
    "test_kit_name": test_kit_name,
    "test_kit_type": test_kit_type,
    "test_kit_status": 'BCSS_READY',
    "logged_by_hub": logged_by_hub,
    "date_time_logged": date_time_logged,
    "test_result": int(test_result),
    "calculated_result": calculated_result,
    "date_time_authorised": str(date_time_authorised),
    "post_response":int(post_response)if post_response is not None else 0,
    "post_attempts":int(post_attempts)if post_attempts is not None else 0,
    "put_response": put_response,
    "put_attempts": put_attempts,
    "device_id": device_id
    }

    # Execute query
    print("Parameters before execution:", params)
    rows_affected = OracleDB().update_or_insert_data_to_table(update_query, params)
    print(f"Rows affected: {rows_affected}")
 # Return the subject NHS number
    return subject_nhs_number



