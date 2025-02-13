import logging
from os import environ

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

from pages.bcss_home_page import BcssHomePage
from pages.login import BcssLoginPage
from pages.screening_practitioner_appointments import (
    ScreeningPractitionerAppointments,
)

load_dotenv()
logger = logging.getLogger(__name__)
expect.set_options(timeout=20_000)


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page) -> None:
    username = environ.get("BCSS_USERNAME")
    password = environ.get("BCSS_PASSWORD")
    login_page = BcssLoginPage(page)
    login_page.login(username, password)


def get_to_screen(page: Page) -> None:
    homepage = BcssHomePage(page)
    expect(page.get_by_role("link", name="Screening Practitioner Appointments")).to_be_visible()
    homepage.click_screening_pracitioners_appointments()
    expect(page.get_by_text("Screening Practitioner Appointments")).to_be_visible()
    page.screenshot(path="test-results/screening/main_screen.png")


def test_view_appointments(page: Page) -> None:
    get_to_screen(page)
    screening_pracitioners_appointments = ScreeningPractitionerAppointments(page)
    screening_pracitioners_appointments.click_view_appointments()
    expect(page.get_by_text("Appointment Calendar")).to_be_visible()
    button_locator = page.query_selector("#BTN_VIEW_LIST")
    if button_locator == None:
        logging.error("Appointment Calendar element not found")
        raise ValueError("Appointment Calendar element not found")
    else:
        button_locator.click()
    expect(page.get_by_text("Screening Practitioner Day View")).to_be_visible()
    table_locator = page.locator("table#displayRS tbody tr")
    row_count = table_locator.count()
    page.screenshot(path="test-results/screening/view_appointments.png")
    assert row_count > 0


def test_patients_that_require_colonoscopy_assessment_appointments(page: Page) -> None:
    get_to_screen(page)
    page.locator("#menuOp2").click()
    page.screenshot(path="test-results/screening/patients_requiring_appointments.png")
    expect(page.get_by_text("Patients that Require Colonoscopy Assessment Appointments")).to_be_visible()

    page.screenshot(path="test-results/screening/patients_requiring_appointments.png")
    table_locator = page.locator("table#booking tbody tr")
    child_count = table_locator.count()

    assert child_count > 0
