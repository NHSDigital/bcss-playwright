import logging
from datetime import datetime

from jaydebeapi import connect

from my_pages import *
from utils import get_nhs_no_from_batch_id
from utils.fit_kit_generation import create_fit_id_df
from utils.oracle import OracleDB
from utils.screening_subject_page_searcher import verify_subject_event_status_by_nhs_no


def test_compartment_3(page: Page) -> None:
    # (STEP - 4) Run two stored procedures to process any kit queue records at status BCSS_READY
    # (processKitQueue function in selenium tests)

    logging.info("start: KitServiceManagementRepository.process_kit_queue")

    # Create entity manager
    entity_manager = EntityManagerFactory.create_entity_manager()

    # Connect to DB
    connection = connect('com.mysql.cj.jdbc.Driver', 'jdbc:mysql://localhost:3306/your_database',
                         ['username', 'password'], 'com.mysql.cj.jdbc.Driver')
    entity_manager['jdbcUrl'] = connection.url
    entity_manager['username'] = connection.username
    entity_manager['password'] = connection.password

    entity_manager['transaction'] = entity_manager.get('entityManager').raw_connection.begin()

    # Run stored procedure 1 - validate kit queue
    logging.info("entityManager.createStoredProcedureQuery('PKG_TEST_KIT_QUEUE.p_validate_kit_queue')")
    sp_query = entity_manager['entityManager'].createStoredProcedureQuery(
        "PKG_TEST_KIT_QUEUE.p_validate_kit_queue")

    logging.info("call stored procedure")
    sp_query.execute()

    # Run stored procedure 2 - calculate result
    logging.info("entityManager.createStoredProcedureQuery('PKG_TEST_KIT_QUEUE.p_calculate_result')")
    sp_query = entity_manager['entityManager'].createStoredProcedureQuery(
        "PKG_TEST_KIT_QUEUE.p_calculate_result")

    logging.info("call stored procedure")
    sp_query.execute()

    # Commit transaction and close
    logging.info("commit transaction and close")
    entity_manager['transaction'].commit()
    entity_manager['entityManager'].close()

    logging.info("exit: KitServiceManagementRepository.process_kit_queue")

    # (STEP - 5) Check the results of the processed FIT kits have correctly updated the status of the associated subjects
    page.goto("/")
    BcssLoginPage(page).login_as_user("BCSS401")

    MainMenu(page).go_to_fit_test_kits_page()
    FITTestKits(page).go_to_log_devices_page()
    subjectdf = create_fit_id_df()

    for subject in range(4):
        fit_device_id = subjectdf["fit_device_id"].iloc[subject]
        LogDevices(page).fill_fit_device_id_field(fit_device_id)
        sample_date = datetime.now().strftime("%#d %b %Y")
        LogDevices(page).fill_sample_date_field(sample_date)
        LogDevices(page).verify_successfully_logged_device_text()

    normal_result_batch_id = ""
    abnormal_result_batch_id = ""

    # Retrieve NHS numbers from FIT normal test results
    normal_test_result_nhs_number = get_nhs_no_from_batch_id.get_nhs_no_from_batch_id(normal_result_batch_id)
    for index, row in normal_test_result_nhs_number.iterrows():
        OracleDB().exec_bcss_timed_events(row["subject_nhs_number"])

    # Retrieve NHS numbers from FIT abnormal test results
    abnormal_test_result_nhs_number = get_nhs_no_from_batch_id.get_nhs_no_from_batch_id(abnormal_result_batch_id)
    for index, row in abnormal_test_result_nhs_number.iterrows():
        OracleDB().exec_bcss_timed_events(row["subject_nhs_number"])

    # Check statuses of 'normal' FIT kit subjects has moved to S2
    nhs_no = subjectdf["subject_nhs_number"].iloc[0]
    verify_subject_event_status_by_nhs_no(page, nhs_no, "S2 - Normal")

    # Check status of 'abnormal' FIT kit subjects has moved to A8
    nhs_no = subjectdf["subject_nhs_number"].iloc[0]
    verify_subject_event_status_by_nhs_no(page, nhs_no, "A8 - Abnormal")
