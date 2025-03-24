import pytest
from playwright.sync_api import Page
from my_pages import *
from utils.batch_processing import batch_processing
from datetime import datetime
from utils.screening_subject_page_searcher import verify_subject_event_status_by_nhs_no
from utils.fit_kit_generation import create_fit_id_df

@pytest.mark.wip2
@pytest.mark.smokescreen
def test_compartment_2(page: Page) -> None:
    page.goto("/")
    BcssLoginPage(page).login_as_user("BCSS401")

    MainMenu(page).go_to_fit_test_kits_page()
    FITTestKits(page).go_to_log_devices_page()
    subjectdf = create_fit_id_df()

    for subject in range(4):
        fit_device_id = subjectdf["fit_device_id"].iloc[subject]
        LogDevices(page).fill_fit_device_id_field(fit_device_id)
        sample_date = datetime.now().strftime("%d %b %Y")
        LogDevices(page).fill_sample_date_field(sample_date)
        LogDevices(page).verify_successfully_logged_device_text()

    nhs_no = subjectdf["nhs_number"].iloc[0]
    verify_subject_event_status_by_nhs_no(page, nhs_no, "S43 - Kit Returned and Logged (Initial Test)")

    NavigationBar(page).click_main_menu_link()
    MainMenu(page).go_to_fit_test_kits_page()
    FITTestKits(page).go_to_log_devices_page()
    spoilt_fit_device_id = subjectdf["fit_device_id"].iloc[-1]
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
