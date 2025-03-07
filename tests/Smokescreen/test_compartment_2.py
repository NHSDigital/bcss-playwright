import pytest
from playwright.sync_api import Page
from my_pages import *
from utils.batch_processing import batch_processing
from datetime import datetime
from utils.screening_subject_page_searcher import verify_subject_event_status_by_nhs_no
import pandas as pd

@pytest.mark.wip1
def test_example(page: Page) -> None:
    page.goto("/")
    BcssLoginPage(page).login_as_user_bcss401()

    MainMenu(page).go_to_fit_test_kits_page()
    FITTestKits(page).go_to_log_devices_page()
    subjectdf = pd.read_parquet('subject_kit_number.parquet', engine='fastparquet')
    for subject in range(4):
        fit_device_id = subjectdf["FIT_Device_ID"].iloc[subject-1]
        # log devices - fill device id field with fit_device_id
        sample_date = datetime.now().strftime("%#d %b %Y")
        # log devices - fill sample date field with sample_date
        # log devices - verify successfully logged device

    nhs_no = subjectdf["NHS_Number"].iloc[0]
    verify_subject_event_status_by_nhs_no(page, nhs_no, "S43 - Kit Returned and Logged (Initial Test)")

    NavigationBar(page).click_main_menu_link()
    MainMenu(page).go_to_fit_test_kits_page()
    FITTestKits(page).go_to_log_devices_page()
    spoilt_fit_device_id = subjectdf["FIT_Device_ID"].iloc[4]
    # log devices - fill device id field with spoilt_fit_device_id
    # log devices - click device spoilt button
    # log devices - select option from dropdown
    # log devices - click log as spoilt button
    # log devices = verify successfully logged device

    batch_processing(page, "S3", "Retest (Spoilt) (FIT)", "S11 - Retest Kit Sent (Spoilt)")
