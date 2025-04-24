import logging
import pytest
from playwright.sync_api import Page, expect
from pages.logout.log_out_page import Logout
from pages.base_page import BasePage
from utils.user_tools import UserTools
from utils.load_properties_file import PropertiesFile
from utils.calendar_picker import CalendarPicker
from utils.batch_processing import batch_processing
from datetime import datetime
from utils.oracle.oracle_specific_functions import get_subjects_for_appointments
from utils.nhs_number_tools import NHSNumberTools


@pytest.fixture
def smokescreen_properties() -> dict:
    return PropertiesFile().get_smokescreen_properties()


@pytest.mark.vpn_required
@pytest.mark.smokescreen
@pytest.mark.compartment4
def test_compartment_4(page: Page, smokescreen_properties: dict) -> None:
    """
    This is the main compartment 4 method
    First it obtains the necessary test data from the DB
    Then it logs on as a Screening Centre Manager and sets the availablity of a practitioner from 09:00 to 17:15 from todays date for the next 6 weeks
    After It logs out an logs back in as a Hub Manager
    Once logging back in it books appointments for the subjects retrieved earlier
    Finally it processes the necessary batches to send out the letters and checks the subjects satus has been updated to what is expected
    """

    subjects_df = get_subjects_for_appointments(
        smokescreen_properties["c4_eng_number_of_appointments_to_book"]
    )

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_practitioner_appointments_page()
    page.get_by_role("link", name="Set Availability").click()
    page.get_by_role("link", name="Practitioner Availability -").click()
    page.locator("#UI_SITE_ID").select_option(index=1)
    page.locator("#UI_PRACTITIONER_ID").select_option(index=1)
    page.get_by_role("button", name="Calendar").click()
    CalendarPicker(page).select_day(
        datetime.today()
    )  # This will make it so that we can only run this test once a day, or we need to restore the DB back to the snapshot
    page.get_by_role("button", name="Show").dblclick()
    page.get_by_role("textbox", name="From:").click()
    page.get_by_role("textbox", name="From:").fill("09:00")
    page.get_by_role("textbox", name="To:").click()
    page.get_by_role("textbox", name="To:").fill("17:15")
    page.get_by_role("button", name="Calculate Slots").click()
    page.locator("#FOR_WEEKS").click()
    page.locator("#FOR_WEEKS").fill("6")
    page.locator("#FOR_WEEKS").press("Enter")
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Slots Updated for 6 Weeks")).to_be_visible()
    Logout(page).log_out()

    page.get_by_role("button", name="Log in").click()
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")
    BasePage(page).go_to_screening_practitioner_appointments_page()
    page.get_by_role("link", name="Patients that Require").click()
    # Add for loop to loop x times (depends on how many we want to run it for) 70 - 79
    nhs_number = subjects_df["subject_nhs_number"].iloc[0]
    nhs_number_spaced = NHSNumberTools().spaced_nhs_number(nhs_number)
    page.locator("#nhsNumberFilter").click()
    page.locator("#nhsNumberFilter").fill(nhs_number)
    page.locator("#nhsNumberFilter").press("Enter")
    page.get_by_role("link", name=nhs_number_spaced).click()
    page.get_by_label("Screening Centre ( All)").select_option("23162")
    page.locator("#UI_NEW_SITE").select_option("42808")
    page.locator('input[name="fri2"]').click()  # Todays date if available
    page.locator("#UI_NEW_SLOT_SELECTION_ID_359119").check()
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Appointment booked")).to_be_visible()

    batch_processing(
        page,
        "A183",
        "Practitioner Clinic 1st Appointment",
        "A25 - 1st Colonoscopy Assessment Appointment Booked, letter sent",
    )

    batch_processing(
        page,
        "A183",
        "GP Result (Abnormal)",
        "A25 - 1st Colonoscopy Assessment Appointment Booked, letter sent",
    )
    page.locator("#ID_LINK_EPISODES_img").click()
    page.get_by_role("link", name="FOBT Screening").click()
    expect(
        page.get_by_role("cell", name="A167 - GP Abnormal FOBT Result Sent", exact=True)
    ).to_be_visible()
    Logout(page).log_out()
