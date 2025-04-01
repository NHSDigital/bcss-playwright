from utils.click_helper import click
from playwright.sync_api import Page


# Reports page main menu links
def go_to_failsafe_reports_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Failsafe Reports"))


def go_to_operational_reports_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Operational Reports"))


def go_to_strategic_reports_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Strategic Reports"))


def go_to_cancer_waiting_times_reports_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Cancer Waiting Times Reports"))


def go_to_dashboard(page: Page) -> None:
    click(page, page.get_by_role("link", name="Dashboard"))


# Failsafe Reports menu links
def go_to_date_report_last_requested_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Date Report Last Requested"))


def go_to_screening_subjects_with_inactive_open_episode_link_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Screening Subjects With"))


def go_to_subjects_ceased_due_to_date_of_birth_changes_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Subjects Ceased Due to Date"))


def go_to_allocate_sc_for_patient_movements_within_hub_boundaries_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Allocate SC for Patient Movements within Hub Boundaries"))


def go_to_allocate_sc_for_patient_movements_into_your_hub_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Allocate SC for Patient Movements into your Hub"))


def go_to_identify_and_link_new_gp_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Identify and link new GP"))


# Operational Reports menu links
def go_to_appointment_attendance_not_updated_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Appointment Attendance Not"))


def go_to_fobt_kits_logged_but_not_read_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="FOBT Kits Logged but Not Read"))


def go_to_demographic_update_inconsistent_with_manual_update_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Demographic Update"))


def go_to_screening_practitioner_6_weeks_availability_not_set_up_report_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Screening Practitioner 6"))


def go_to_screening_practitioner_appointments_page(page: Page) -> None:
    click(page, page.get_by_role("link", name="Screening Practitioner Appointments"))
