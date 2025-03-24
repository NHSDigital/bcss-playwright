import logging
from datetime import datetime

from my_pages import *
from utils import fit_kit_logged
from utils.batch_processing import batch_processing
from utils.fit_kit_generation import create_fit_id_df
from utils.fit_kit_logged import process_kit_data, update_kit_service_management_entity
from utils.oracle import OracleDB
from utils.screening_subject_page_searcher import verify_subject_event_status_by_nhs_no


@pytest.mark.wip2
def test_compartment_3(page: Page) -> None:
    UserTools.user_login(page, "Hub Manager State Registered")

    # (STEP 1 ,2 & 3) find data , seperate it into normal and abnormal, Add results to the test records in the KIT_QUEUE table (i.e. mimic receiving results from the middleware)
    # and get device IDs and their flags
    device_ids = process_kit_data()
    # Retrieve NHS numbers for each device_id and determine normal/abnormal status
    nhs_numbers = []
    normal_flags = []

    for device_id, is_normal in device_ids:
        nhs_number = update_kit_service_management_entity(device_id, is_normal)
        nhs_numbers.append(nhs_number)
        normal_flags.append(is_normal)  # Store the flag (True for normal, False for abnormal)
    # (STEP - 4) Run two stored procedures to process any kit queue records at status BCSS_READY
    try:
        fit_kit_logged.execute_stored_procedures()
        logging.info("Stored procedures executed successfully.")
    except Exception as e:
        logging.error(f"Error executing stored procedures: {str(e)}")
        raise
    # (STEP - 5) Check the results of the processed FIT kits have correctly updated the status of the associated subjects
    # Verify subject event status based on normal or abnormal classification
    for nhs_number, is_normal in zip(nhs_numbers, normal_flags):
        expected_status = "S2 - Normal" if is_normal else "A8 - Abnormal"  # S2 for normal, A8 for abnormal
        logging.info(f"Verifying NHS number: {nhs_number} with expected status: {expected_status}")

        try:
            verify_subject_event_status_by_nhs_no(page, nhs_number, expected_status)
            logging.info(f"Successfully verified NHS number {nhs_number} with status {expected_status}")
        except Exception as e:
            logging.error(f"Verification failed for NHS number {nhs_number} with status {expected_status}: {str(e)}")
            raise


    # Navigate to log devices page
    MainMenu(page).go_to_fit_test_kits_page()
    FITTestKits(page).go_to_log_devices_page()

    # Get a fit device id
    subjectdf = create_fit_id_df()

    # Log fit device
    for subject in range(4):
        fit_device_id = subjectdf["fit_device_id"].iloc[subject]
        LogDevices(page).fill_fit_device_id_field(fit_device_id)
        sample_date = datetime.now().strftime("%#d %b %Y")
        LogDevices(page).fill_sample_date_field(sample_date)
        LogDevices(page).verify_successfully_logged_device_text()

    # Check statuses of 'normal' FIT kit subjects has moved to S2
    nhs_no = subjectdf["subject_nhs_number"].iloc[0]
    verify_subject_event_status_by_nhs_no(page, nhs_no, "S2 - Normal")

    # Check status of 'abnormal' FIT kit subjects has moved to A8
    nhs_no = subjectdf["subject_nhs_number"].iloc[0]
    verify_subject_event_status_by_nhs_no(page, nhs_no, "A8 - Abnormal")

    # (Step 12) - Process S2 batch
    # Run batch processing function on S2 batch
    batch_processing(page, "S2", "Normal", "S2 - Normal")
    nhs_number_df = batch_processing(page, "S2", "Normal", "S2 - Normal")
    for index, row in nhs_number_df.iterrows():
        OracleDB().exec_bcss_timed_events(row["subject_nhs_number"])

    # Verify Status of subject is updated to S158
    nhs_no = subjectdf["subject_nhs_number"].iloc[0]
    verify_subject_event_status_by_nhs_no(page, nhs_no, "S158")

    # (Step 13) - Process S158 batch
    # Run batch processing function on S158 batch
    batch_processing(page, "S158", "Normal result letter sent to subject", "S158 - Normal result letter sent to subject")
    nhs_number_df = batch_processing(page, "S158", "Normal result letter sent to subject", "S158 - Normal result letter sent to subject")
    for index, row in nhs_number_df.iterrows():
        OracleDB().exec_bcss_timed_events(row["subject_nhs_number"])

    # Verify Status of subject is updated to S159
    nhs_no = subjectdf["subject_nhs_number"].iloc[0]
    verify_subject_event_status_by_nhs_no(page, nhs_no, "S159 - Normal result letter sent to GP")

