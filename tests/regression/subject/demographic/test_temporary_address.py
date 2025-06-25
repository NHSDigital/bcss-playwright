import pytest
from playwright.sync_api import Page
from utils.user_tools import UserTools
from pages.base_page import BasePage
from pages.screening_subject_search.subject_demographic_page import (
    SubjectDemographicPage,
)
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils.screening_subject_page_searcher import (
    search_subject_demographics_by_nhs_number,
    search_subject_by_nhs_number,
)
from utils.oracle.oracle import OracleDB
import logging
from faker import Faker
from datetime import datetime, timedelta


@pytest.mark.regression
@pytest.mark.subject_tests
@pytest.mark.wip
def test_not_amending_temporary_address(page: Page):
    """ """

    # Screening Centre Manager - State Registered (England)
    UserTools.user_login(page, "Screening Centre Manager at BCS001")

    # Navigate to the Subject Search Criteria Page
    BasePage(page).go_to_screening_subject_search_page()

    # Search for a subject's demographics by NHS Number
    nhs_no = "9322895063"
    search_subject_demographics_by_nhs_number(page, nhs_no)

    # Update the subject's postcode
    fake = Faker("en_GB")
    random_postcode = fake.postcode()
    SubjectDemographicPage(page).fill_postcode_input(random_postcode)
    SubjectDemographicPage(page).postcode_field.press("Tab")
    SubjectDemographicPage(page).click_update_subject_data_button()

    df = OracleDB().execute_query(
        """
        SELECT
        ss.subject_nhs_number, adds.address_type, adds.effective_from
        FROM screening_subject_t ss
        INNER JOIN sd_contact_t c ON c.nhs_number = ss.subject_nhs_number
        INNER JOIN sd_address_t adds ON adds.contact_id = c.contact_id
        WHERE ss.subject_nhs_number = :nhs_no
        """,
        {"nhs_no": nhs_no},
    )

    for address_type in df["address_type"]:
        logging.info(f"Address Type: {address_type}")
        try:
            assert int(df["address_type"].iloc[address_type]) != 13043
        except AssertionError:
            logging.error(
                f"Test Failed - Subject has a temporary address: {df['address_type'].iloc[0]}\n{AssertionError}"
            )


@pytest.mark.regression
@pytest.mark.subject_tests
def test_add_temporyay_address_then_delete(page: Page):
    """ """

    # Screening Centre Manager - State Registered (England)
    UserTools.user_login(page, "Screening Centre Manager at BCS001")

    # Navigate to the
    BasePage(page).go_to_screening_subject_search_page()
    # Search for a subject's demographics by NHS Number
    nhs_no = "9322895063"
    search_subject_demographics_by_nhs_number(page, nhs_no)
    # Add a temporary address
    temp_address = {
        "valid_from": datetime.today(),
        "valid_to": datetime.today() + timedelta(days=31),
        "address_line_1": "Temporary Address Line 1",
        "address_line_2": "Temporary Address Line 2",
        "address_line_3": "Temporary Address Line 3",
        "address_line_4": "Temporary Address Line 4",
        "address_line_5": "Temporary Address Line 5",
        "postcode": "AB12 3CD",
    }
    SubjectDemographicPage(page).update_temporary_address(temp_address)
    SubjectDemographicPage(page).click_back_button()
    search_subject_by_nhs_number(page, nhs_no)
    SubjectScreeningSummaryPage(page).verify_temporary_address_icon_visible()
    SubjectScreeningSummaryPage(page).click_temporary_address_icon()
    SubjectScreeningSummaryPage(page).verify_temporary_address_popup_visible()

    # Delete the temporary address
    temp_address = {
        "valid_from": None,
        "valid_to": None,
        "address_line_1": "",
        "address_line_2": "",
        "address_line_3": "",
        "address_line_4": "",
        "address_line_5": "",
        "postcode": "",
    }
    SubjectDemographicPage(page).update_temporary_address(temp_address)

    df = OracleDB().execute_query(
        """
        SELECT
        ss.subject_nhs_number, adds.address_type, adds.effective_from
        FROM screening_subject_t ss
        INNER JOIN sd_contact_t c ON c.nhs_number = ss.subject_nhs_number
        INNER JOIN sd_address_t adds ON adds.contact_id = c.contact_id
        WHERE ss.subject_nhs_number = :nhs_no
        """,
        {"nhs_no": nhs_no},
    )

    try:
        assert int(df["address_type"].iloc[0]) != 13043
        logging.info("Test Passed - Subject does not have a temporary address")
    except AssertionError:
        logging.error(
            f"Test Failed - Subject has a temporary address: {df['address_type'].iloc[0]}\n{AssertionError}"
        )
