import logging
from datetime import datetime

from my_pages import *
from utils import oracle
from utils.fit_kit_generation import create_fit_id_df
from utils.oracle import OracleDB
from utils.screening_subject_page_searcher import verify_subject_event_status_by_nhs_no


def test_compartment_3(page: Page) -> None:
    page.goto("/")
    BcssLoginPage(page).login_as_user("BCSS401")

    # (STEP - 4) Run two stored procedures to process any kit queue records at status BCSS_READY
    # (processKitQueue function in selenium tests)

    logging.info("start: oracle.OracleDB.execute_stored_procedure")

    # Run stored procedure 1 - validate kit queue
    oracle.OracleDB.execute_stored_procedure(OracleDB,"PKG_TEST_KIT_QUEUE.p_validate_kit_queue")

    # Run stored procedure 2 - calculate result
    oracle.OracleDB.execute_stored_procedure(OracleDB,"PKG_TEST_KIT_QUEUE.p_calculate_result")

    logging.info("exit: oracle.OracleDB.execute_stored_procedure")

    # (STEP - 5) Check the results of the processed FIT kits have correctly updated the status of the associated subjects
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
