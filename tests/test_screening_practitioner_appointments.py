from gc import get_count
from os import environ
import pytest
import logging
from playwright.sync_api import Page, expect
from pages.login import BcssLoginPage
from pages.bcss_home_page import BcssHomePage
from pages.screening_practitioner_appointments import (
    ScreeningPractitionerAppointments,
)
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
expect.set_options(timeout=20_000)


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    username = environ.get("BCSS_USERNAME")
    password = environ.get("BCSS_PASSWORD")
    login_page = BcssLoginPage(page)
    login_page.login(username, password)


def get_to_screen(page: Page):
    homepage = BcssHomePage(page)
    expect(
        page.get_by_role("link", name="Screening Practitioner Appointments")
    ).to_be_visible()
    homepage.click_screening_pracitioners_appointments()
    expect(page.get_by_role("link", name="View appointments")).to_be_visible()


def test_view_appointments(page: Page) -> None:
    get_to_screen(page)
    screening_pracitioners_appointments = ScreeningPractitionerAppointments(page)
    screening_pracitioners_appointments.click_view_appointments()
    expect(page.get_by_text("Appointment Calendar")).to_be_visible()
    button_locator = page.query_selector("#BTN_VIEW_LIST")
    button_locator.click()
    expect(page.get_by_text("Screening Practitioner Day View")).to_be_visible()
    table_locator = page.locator("table#displayRS tbody tr")
    row_count = table_locator.count()
    assert row_count > 0


def test_patients_that_require_colonoscopy_assessment_appointments(page: Page) -> None:
    get_to_screen(page)
    screening_pracitioners_appointments = ScreeningPractitionerAppointments(page)
    screening_pracitioners_appointments.click_patients_that_require_colonoscopy_assessment_appointments()
    expect(
        page.get_by_text("Patients that Require Colonoscopy Assessment Appointments")
    ).to_be_visible()
    table_locator = page.locator("table#booking tbody tr")
    child_count = table_locator.count()
    assert child_count > 0


# def test_patients_that_require_colonoscopy_assessment_appointments_bowel_scope(
#     page: Page,
# ) -> None:
#     get_to_screen(page)
#     # homepage = BcssHomePage(page)
#     screening_pracitioners_appointments = ScreeningPractitionerAppointments(page)
#     # homepage.click_screening_pracitioners_appointments()
#     # expect(page.get_by_role("link", name="View appointments")).to_be_visible()
#     screening_pracitioners_appointments.click_patients_that_require_colonoscopy_assessment_appointments_bowl_scope()
#     expect(
#         page.get_by_text(
#             "Patients that Require Colonoscopy Assessment Appointment Booking"
#         )
#     ).to_be_visible()
#     # table_locator = page.locator("table#displayInputParameters tbody tr")
#     # child_count = table_locator.count()
#     # assert child_count > 0


# def test_patients_that_require_surveillance_appointments(
#     page: Page,
# ) -> None:
#     get_to_screen(page)
#     screening_pracitioners_appointments = ScreeningPractitionerAppointments(page)
#     screening_pracitioners_appointments.click_patients_that_require_surveillance_appointments()
# expect(
#     page.get_by_text("Patients that Require Surveillance Appointments")
# ).to_be_visible()
# table_locator = page.locator("table#displayInputParameters tbody tr")
# child_count = table_locator.count()
# assert child_count > 0


# def test_view_appointments(page: Page) -> None:
#     homepage = BcssHomePage(page)

#     # Check the show and hide sub menu works
#     homepage.click_sub_menu_link()
#     expect(page.get_by_role("link", name="Organisation Parameters")).to_be_visible()
#     homepage.click_hide_sub_menu_link()
#     expect(page.get_by_role("cell", name="Alerts", exact=True)).to_be_visible()

# def test_homepage_select_org(page: Page) -> None:
#     homepage = BcssHomePage(page)

#     # check the select org link works and then go back to homepage
#     homepage.click_select_org_link()
#     expect(page.locator("form")).to_contain_text("Choose an Organisation")
#     homepage.click_back_button()
#     expect(page.get_by_role("cell", name="Alerts", exact=True)).to_be_visible()

# def test_homepage_release_notes(page: Page) -> None:
#     homepage = BcssHomePage(page)

#     # Click release notes link
#     homepage.click_release_notes_link()
#     expect(page.locator("#page-title")).to_contain_text("Release Notes")

# def test_homepage_help(page: Page) -> None:
#     homepage = BcssHomePage(page)

#     # check the help link works
#     with page.expect_popup() as popup_info:
#         homepage.click_help_link()
#         help_page = popup_info.value
#         expect(help_page.get_by_text("Bowel Cancer Screening System Help")).to_be_visible


# <input type="button" id="BTN_VIEW_LIST"
# value="View appointments on this day"
# onclick="inhibitOnXXXXXFunctionFor2MonthCalendar = false;
# return doSubmit();">


# def test_homepage_select_org(page: Page) -> None:
#     homepage = BcssHomePage(page)

#     # check the select org link works
#     homepage.click_select_org_link()
#     expect(page.locator("form[action*='/changeorg']")).to_contain_text("Choose an Organisation")
#     # Check there is at least one entry in the organisation list
#     table_locator = page.locator("table#organisations tr")
#     row_count = table_locator.count()
#     assert row_count > 0
#     # Go back to the home page and make sure it loaded
#     homepage.click_back_button()
#     expect(page.get_by_role("cell", name="Alerts", exact=True)).to_be_visible()
