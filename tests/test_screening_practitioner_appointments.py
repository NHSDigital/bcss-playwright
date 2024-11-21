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