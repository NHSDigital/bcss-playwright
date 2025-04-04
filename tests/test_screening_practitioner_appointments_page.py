import pytest
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pages.screening_practitioner_appointments import ScreeningPractitionerAppointmentsPage
from pages.bowel_scope_appointments_page import BowelScopeAppointments
from pages.colonoscopy_assessment_appointments_page import ColonoscopyAssessmentAppointments
from utils.user_tools import UserTools


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the
    screening_practitioner_appointments page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered")

    # Go to screening practitioner appointments page
    BasePage(page).go_to_screening_practitioner_appointments_page()


@pytest.mark.smokeee
def test_screening_practitioner_appointments_page_navigation(page: Page) -> None:
    """
    Confirms screening_practitioner_appointments page loads and the expected links are visible
    and clickable (where the user has required permissions).
    """
    # Verify View appointments page opens as expected
    ScreeningPractitionerAppointmentsPage(page).go_to_view_appointments_page()
    BowelScopeAppointments(page).verify_page_title()
    BowelScopeAppointments(page).click_back_button()

    # Verify Patients that Require Colonoscopy Assessment Appointments page opens as expected
    ScreeningPractitionerAppointmentsPage(page).go_to_patients_that_require_page()
    ColonoscopyAssessmentAppointments(page).verify_page_header()

    ColonoscopyAssessmentAppointments(page).click_back_button()

    expect(ScreeningPractitionerAppointmentsPage(page).patients_that_require_colonoscopy_assessment_appointments_bowel_scope_link).to_be_visible()
    expect(ScreeningPractitionerAppointmentsPage(page).patients_that_require_surveillance_appointment_link).to_be_visible()
    expect(ScreeningPractitionerAppointmentsPage(page).patients_that_require_post).to_be_visible()
    expect(ScreeningPractitionerAppointmentsPage(page).set_availability_link).to_be_visible()

    # Return to main menu
    ScreeningPractitionerAppointmentsPage(page).click_main_menu_link()
    ScreeningPractitionerAppointmentsPage(page).main_menu_header_is_displayed()
