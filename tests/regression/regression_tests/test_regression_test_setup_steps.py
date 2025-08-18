import pytest
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.contacts_list.contacts_list_page import ContactsListPage
from pages.contacts_list.maintain_contacts_page import MaintainContactsPage
from pages.contacts_list.edit_contact_page import EditContactPage
from pages.contacts_list.resect_and_discard_accreditation_history_page import (
    ResectAndDiscardAccreditationHistoryPage,
)
from pages.logout.log_out_page import LogoutPage
from utils.user_tools import UserTools
from utils.oracle.oracle_specific_functions import (
    set_org_parameter_value,
    check_parameter,
)
from utils.dataset_field_util import DatasetFieldUtil

from utils.oracle.oracle import OracleDB


def test_allow_10_minute_colonsocopy_assessment_Appointments(page: Page) -> None:
    """
    Scenario: 1: Allow 10 minute colonoscopy assessment appointments between 7am and 8pm at BCS001

    Given I log in to BCSS "England" as user role "Screening Centre Manager"
        And I set the value of parameter 12 to "10" for my organisation with immediate effect
        And I set the value of parameter 28 to "07:00" for my organisation with immediate effect
        And I set the value of parameter 29 to "20:00" for my organisation with immediate effect
    """
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    param_12_set_correctly = check_parameter(12, "23162", "10")
    param_28_set_correctly = check_parameter(28, "23162", "07:00")
    param_29_set_correctly = check_parameter(29, "23162", "20:00")
    if not param_12_set_correctly:
        set_org_parameter_value(12, "10", "23162")
    if not param_28_set_correctly:
        set_org_parameter_value(28, "07:00", "23162")
    if not param_29_set_correctly:
        set_org_parameter_value(29, "20:00", "23162")

    LogoutPage(page).log_out()


def test_ensure_the_is_accredited_screening_colonoscopist_with_current_resect_and_discard_accreditation(
    page: Page,
) -> None:
    """
    Scenario: 2: Ensure there is an Accredited Screening Colonoscopist with current Resect & Discard accreditation
    """
    UserTools.user_login(page, "BCSS Bureau Staff at X26")
    BasePage(page).go_to_contacts_list_page()
    ContactsListPage(page).go_to_maintain_contacts_page()
    query = """
    SELECT
        prs.prs_id,
        prs.person_family_name,
        prs.person_given_name,
        prs.gmc_code,
        pio.pio_id,
        pio.role_id,
        org.org_code,
        org.org_name
    FROM person prs
    INNER JOIN person_in_org pio ON prs.prs_id = pio.prs_id
    INNER JOIN org ON org.org_id = pio.org_id
    WHERE 1=1
    AND pio.role_id = (SELECT valid_value_id FROM valid_values WHERE description = 'Accredited Screening Colonoscopist')
    AND org.org_code = 'BCS001'
    AND TRUNC(SYSDATE) BETWEEN TRUNC(pio.start_date) AND NVL(pio.end_date, SYSDATE)
    AND pio.is_bcss_user = 1
    ORDER BY prs.prs_id
    FETCH FIRST 1 ROWS ONLY
    """
    person_df = OracleDB().execute_query(query)
    surname = person_df.iloc[0]["person_family_name"]
    forename = person_df.iloc[0]["person_given_name"]
    MaintainContactsPage(page).fill_surname_input_field(surname)
    MaintainContactsPage(page).fill_forenames_input_field(forename)
    MaintainContactsPage(page).click_search_button()
    MaintainContactsPage(page).click_first_correct_link()
    EditContactPage(page).click_view_resect_and_discard_link()
    ResectAndDiscardAccreditationHistoryPage(page).verify_heading_is_correct()
    ResectAndDiscardAccreditationHistoryPage(
        page
    ).verify_add_accreditation_button_exists()
    yesterday = datetime.today() - timedelta(days=1)
    ResectAndDiscardAccreditationHistoryPage(
        page
    ).add_new_period_of_resect_and_discard_accerditation(date=yesterday)
    BasePage(page).click_back_button()
    end_date = yesterday + relativedelta(years=2)
    EditContactPage(page).assert_value_for_label_in_edit_contact_table(
        "Resect & Discard Accreditation?",
        f"Current: ends {end_date.strftime('%d/%m/%Y')}",
    )
    logging.info(f"Test person used in this scenario is: {forename} {surname}")
