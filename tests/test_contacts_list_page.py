import logging
import pytest
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pages.contacts_list.contacts_list_page import ContactsListPage
from pages.contacts_list.view_contacts_page import ViewContactsPage
from pages.contacts_list.edit_my_contact_details_page import EditMyContactDetailsPage
from pages.contacts_list.maintain_contacts_page import MaintainContactsPage
from pages.contacts_list.my_preference_settings_page import MyPreferenceSettingsPage
from utils.user_tools import UserTools


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the contacts list page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")

    # Go to contacts list page
    BasePage(page).go_to_contacts_list_page()


@pytest.mark.smoke
def test_contacts_list_page_navigation(page: Page) -> None:
    """
    Confirms all menu items are displayed on the contacts list page, and that the relevant pages
    are loaded when the links are clicked
    """
    # View contacts page loads as expected
    ContactsListPage(page).go_to_view_contacts_page()
    ViewContactsPage(page).verify_view_contacts_title()
    BasePage(page).click_back_button()

    # Edit my contact details page loads as expected
    ContactsListPage(page).go_to_edit_my_contact_details_page()
    EditMyContactDetailsPage(page).verify_edit_my_contact_details_title()
    BasePage(page).click_back_button()

    # Maintain contacts page loads as expected
    ContactsListPage(page).go_to_maintain_contacts_page()
    MaintainContactsPage(page).verify_maintain_contacts_title()
    BasePage(page).click_back_button()

    # My preference settings page loads as expected
    ContactsListPage(page).go_to_my_preference_settings_page()
    MyPreferenceSettingsPage(page).verify_my_preference_settings_title()
    BasePage(page).click_back_button()

    # Other links are visible (Not clickable due to user role permissions)
    ContactsListPage(page).verify_extract_contact_details_page_visible()
    ContactsListPage(page).verify_resect_and_discard_accredited_page_visible()

    # Return to main menu
    BasePage(page).click_main_menu_link()
    BasePage(page).main_menu_header_is_displayed()


def test_view_contacts_accredited_screening_colonoscopist(page: Page) -> None:
    """
    Navigate to contact list, search for Accredited* role and BCS001 organisation and select the role link next to a contact.
    Expects the View Details page to have the role Accredited Screening Colonoscopist.
    """

    BasePage(page).go_to_page(["View Contacts"])
    ViewContactsPage(page).search_by_job_role_and_organisation_code(
        "Accredited*", "BCS001"
    )

    page.get_by_role(
        "row",
        name="Legroom Sensitive Accredited Screening Colonoscopist BCS001 Wolverhampton Bowel Cancer Screening Centre",
        exact=True,
    ).get_by_role("link").click()
    expect(page.locator('form[name="frm"]')).to_contain_text(
        "Accredited Screening Colonoscopist"
    )
    logging.info("results contain name Legroom Sensitive")
