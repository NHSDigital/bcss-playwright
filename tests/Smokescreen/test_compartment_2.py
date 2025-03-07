import pytest
from playwright.sync_api import Page
from my_pages import *
from utils.batch_processing import batch_processing
from datetime import datetime
from utils.screening_subject_page_searcher import verify_subject_event_status_by_nhs_no
import pandas as pd

@pytest.mark.wip1
def test_compartment_2(page: Page) -> None:
    page.goto("/")
    BcssLoginPage(page).login_as_user("BCSS401")

    MainMenu(page).go_to_fit_test_kits_page()
    FITTestKits(page).go_to_log_devices_page()
    subjectdf = pd.read_parquet('subject_kit_number.parquet', engine='fastparquet')
    os.remove('subject_kit_number.parquet')

    for subject in range(4):
        fit_device_id = subjectdf["FIT_Device_ID"].iloc[subject-1]
        LogDevices(page).fill_fit_device_id_field(fit_device_id)
        sample_date = datetime.now().strftime("%#d %b %Y")
        LogDevices(page).fill_sample_date_field(sample_date)
        LogDevices(page).verify_successfully_logged_device_text()

    nhs_no = subjectdf["NHS_Number"].iloc[0]
    verify_subject_event_status_by_nhs_no(page, nhs_no, "S43 - Kit Returned and Logged (Initial Test)")

    NavigationBar(page).click_main_menu_link()
    MainMenu(page).go_to_fit_test_kits_page()
    FITTestKits(page).go_to_log_devices_page()
    spoilt_fit_device_id = subjectdf["FIT_Device_ID"].iloc[4]
    LogDevices(page).fill_fit_device_id_field(spoilt_fit_device_id)
    LogDevices(page).click_device_spoilt_button()
    LogDevices(page).select_spoilt_device_dropdown_option()
    LogDevices(page).click_log_as_spoilt_button()
    LogDevices(page).verify_successfully_logged_device_text()

    batch_processing(page, "S3", "Retest (Spoilt) (FIT)", "S11 - Retest Kit Sent (Spoilt)")

    # Log out
    NavigationBar(page).click_log_out_link()
    Logout(page).verify_log_out_page()
    page.close()
