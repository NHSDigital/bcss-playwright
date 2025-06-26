import pytest
from playwright.sync_api import Page
from utils.user_tools import UserTools
from classes.user import User
from classes.subject import Subject
from pages.base_page import BasePage
from pages.screening_subject_search.subject_demographic_page import (
    SubjectDemographicPage,
)
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils.screening_subject_page_searcher import (
    search_subject_demographics_by_nhs_number,
    search_subject_episode_by_nhs_number,
)
from utils.oracle.oracle import OracleDB
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
import logging
from faker import Faker
from datetime import datetime, timedelta


@pytest.mark.regression
@pytest.mark.subject_tests
def test_not_amending_temporary_address(page: Page):
    """
    Scenario: If not amending a temporary address, no need to validate it

    This test is checking that if a temporary address is not being amended,
    and the subject's postcode is updated.
    That the subject does not have a temporary address added to them.
    """

    criteria = {
        "subject age": "<= 80",
        "subject has temporary address": "no",
    }
    user = User()
    subject = Subject()

    builder = SubjectSelectionQueryBuilder()

    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=1
    )

    df = OracleDB().execute_query(query, bind_vars)
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"Selected NHS Number: {nhs_no}")

    # Screening Centre Manager - State Registered (England)
    UserTools.user_login(page, "Screening Centre Manager at BCS001")

    # Navigate to the Subject Search Criteria Page
    BasePage(page).go_to_screening_subject_search_page()

    # Search for a subject's demographics by NHS Number
    search_subject_demographics_by_nhs_number(page, nhs_no)

    # Update the subject's postcode
    fake = Faker("en_GB")
    random_postcode = fake.postcode()
    SubjectDemographicPage(page).fill_postcode_input(random_postcode)
    SubjectDemographicPage(page).postcode_field.press("Tab")
    SubjectDemographicPage(page).click_update_subject_data_button()

    check_subject_has_temporary_address(page, nhs_no, temporary_address=False)


@pytest.mark.regression
@pytest.mark.subject_tests
def test_add_temporyay_address_then_delete(page: Page):
    """
    Add a temporary address, then delete it.

    This test is checking that a temporary address can be added to a subject,
    and then deleted successfully, ensuring the temporary address icon behaves as expected.
    """
    criteria = {
        "subject age (y/d)": "<= 80",
        "subject has temporary address": "no",
    }
    user = User()
    subject = Subject()

    builder = SubjectSelectionQueryBuilder()

    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=1
    )

    df = OracleDB().execute_query(query, bind_vars)
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"Selected NHS Number: {nhs_no}")

    # Screening Centre Manager - State Registered (England)
    UserTools.user_login(page, "Screening Centre Manager at BCS001")

    # Navigate to the
    BasePage(page).go_to_screening_subject_search_page()
    # Search for a subject's demographics by NHS Number
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

    check_subject_has_temporary_address(page, nhs_no, temporary_address=True)

    SubjectScreeningSummaryPage(page).click_subject_demographics()

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

    check_subject_has_temporary_address(page, nhs_no, temporary_address=False)


def check_subject_has_temporary_address(
    page: Page, nhs_no: str, temporary_address: bool
) -> None:
    """
    Check if a subject has a temporary address in the database.
    Args:
        nhs_no (str): The NHS number of the subject.
    """

    BasePage(page).click_main_menu_link()
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_episode_by_nhs_number(page, nhs_no)
    if temporary_address:
        SubjectScreeningSummaryPage(page).verify_temporary_address_icon_visible()
        SubjectScreeningSummaryPage(page).click_temporary_address_icon()
        SubjectScreeningSummaryPage(page).verify_temporary_address_popup_visible()
        SubjectScreeningSummaryPage(page).click_close_button()
        logging.info(
            "Temporary address icon is visible and popup is displayed, as expected."
        )
    else:
        SubjectScreeningSummaryPage(page).verify_temporary_address_icon_not_visible()
        logging.info("Temporary address icon is not visible, as expected.")
