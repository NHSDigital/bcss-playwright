import pytest
from playwright.sync_api import Page, expect
<<<<<<< HEAD
=======
from sys import platform
>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))
from pages.base_page import BasePage
from pages.reports.reports_page import ReportsPage
from utils.date_time_utils import DateTimeUtils
from utils.user_tools import UserTools
from jproperties import Properties
<<<<<<< HEAD
import os
=======
>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))


@pytest.fixture
def tests_properties() -> dict:
    """
    Reads the 'bcss_tests.properties' file and populates a 'Properties' object.
    Returns a dictionary of properties for use in tests.

    Returns:
        dict: A dictionary containing the values loaded from the 'bcss_tests.properties' file.
    """
<<<<<<< HEAD
    path = f"{os.getcwd()}/tests/bcss_tests.properties"
    configs = Properties()
    with open(path, "rb") as read_prop:
        configs.load(read_prop)
=======
    configs = Properties()
    if platform == "win32":  # File path from content root is required on Windows OS
        with open("tests/bcss_tests.properties", "rb") as read_prop:
            configs.load(read_prop)
    elif platform == "darwin":  # Only the filename is required on macOS
        with open("bcss_tests.properties", "rb") as read_prop:
            configs.load(read_prop)
>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))
    return configs.properties


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the
    reports page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")

    # Open reports page
    BasePage(page).go_to_reports_page()


@pytest.mark.smoke
def test_reports_page_navigation(page: Page) -> None:
    """
    Confirms all menu items are displayed on the reports page, and that the relevant pages
    are loaded when the links are clicked
    """
<<<<<<< HEAD

    # Bureau reports link is visible
    expect(ReportsPage(page).bureau_reports_link).to_be_visible()

    # Failsafe reports page opens as expected
    ReportsPage(page).go_to_failsafe_reports_page()
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Failsafe Reports"
    )
=======
    bureau_reports_link = page.get_by_text("Bureau Reports")
    qa_report_data_completion_link = page.get_by_text("QA Report : Dataset Completion")

    # Bureau reports link is visible
    expect(bureau_reports_link).to_be_visible()

    # Failsafe reports page opens as expected
    ReportsPage(page).go_to_failsafe_reports_page()
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Failsafe Reports"
    )
    BasePage(page).click_back_button()

    # Operational reports page opens as expected
    ReportsPage(page).go_to_operational_reports_page()
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Operational Reports"
    )
    BasePage(page).click_back_button()

    # Strategic reports page opens as expected
    ReportsPage(page).go_to_strategic_reports_page()
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Strategic Reports"
    )
    BasePage(page).click_back_button()

    # "Cancer waiting times reports" page opens as expected
    ReportsPage(page).go_to_cancer_waiting_times_reports_page()
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Cancer Waiting Times Reports"
    )
    BasePage(page).click_back_button()

    # Dashboard opens as expected TODO - this step may be failing legitimately
    # ReportsPage(page).go_to_dashboard()
    # BasePage(page).bowel_cancer_screening_page_title_contains_text("Dashboard")
    # BasePage(page).click_back_button()

    # QA Report : Dataset Completion link is visible
<<<<<<< HEAD
    expect(ReportsPage(page).qa_report_dataset_completion_link).to_be_visible()
=======
    expect(qa_report_data_completion_link).to_be_visible()
>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))

    # Return to main menu
    BasePage(page).click_main_menu_link()
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text("Main Menu")


# Failsafe Reports
def test_failsafe_reports_date_report_last_requested(page: Page) -> None:
    """
    Confirms 'date_report_last_requested' page loads, 'generate report' and 'refresh' buttons work as expected
    and the timestamp updates to current date and time when refreshed
    """
<<<<<<< HEAD
=======
    report_timestamp_element = page.locator("b")
>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))

    # Go to failsafe reports page
    ReportsPage(page).go_to_failsafe_reports_page()

    # Click 'date report last requested' link
    ReportsPage(page).go_to_date_report_last_requested_page()

    # Verify 'Date Report Last Requested' is the page title
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Date Report Last Requested"
    )

    # Click 'generate report' button
    ReportsPage(page).click_generate_report_button()
    # Verify timestamp has updated (equals current date and time)
    report_timestamp = DateTimeUtils.report_timestamp_date_format()
<<<<<<< HEAD
    expect(ReportsPage(page).common_report_timestamp_element).to_contain_text(
        report_timestamp
    )
=======
    expect(report_timestamp_element).to_contain_text(report_timestamp)
>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))

    # Click 'refresh' button
    ReportsPage(page).click_refresh_button()

    # Verify timestamp has updated (equals current date and time)
    report_timestamp = DateTimeUtils.report_timestamp_date_format()
<<<<<<< HEAD
    expect(ReportsPage(page).common_report_timestamp_element).to_contain_text(
        report_timestamp
    )
=======
    expect(report_timestamp_element).to_contain_text(report_timestamp)
>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))


def test_failsafe_reports_screening_subjects_with_inactive_open_episode(
    page: Page,
) -> None:
    """
    Confirms 'screening_subjects_with_inactive_open_episode' page loads, 'generate report' button works as expected
    and that a screening subject record can be opened
    """
    nhs_number_link = page.get_by_role(
        "cell", name="7652"
    )  # This value is specific to this test only

    # Go to failsafe reports page
    ReportsPage(page).go_to_failsafe_reports_page()

    # Click screening subjects with inactive open episode link
    ReportsPage(page).go_to_screening_subjects_with_inactive_open_episode_link_page()

    # Verify "Screening Subjects With Inactive Open Episode" is the page title
    BasePage(page).bowel_cancer_screening_page_title_contains_text(
        "Screening Subjects With Inactive Open Episode"
    )

    # Click 'Generate Report' button
    ReportsPage(page).click_generate_report_button()

    # Open a screening subject record
<<<<<<< HEAD
    ReportsPage(page).click_nhs_number_link(page)

    # Verify the page title is "Subject Screening Summary"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Subject Screening Summary"
    )
=======
    nhs_number_link.click()

    # Verify "Subject Screening Summary" is the page title
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Subject Screening Summary"
    )


def test_failsafe_reports_subjects_ceased_due_to_date_of_birth_changes(
    page: Page,
) -> None:
    """
    Confirms 'subjects_ceased_due_to_date_of_birth_changes' page loads,
    the datepicker and 'generate report' button works as expected
    the timestamp updates to current date and time when refreshed and
    a screening subject record can be opened
    """

    nhs_number_link = page.locator(
        "#listReportDataTable > tbody > tr.oddTableRow > td:nth-child(1) > a"
    )
    report_timestamp_element = page.locator(
        "#displayGenerateDate > tbody > tr > td > b"
    )

    # Go to failsafe reports page
    ReportsPage(page).go_to_failsafe_reports_page()

    # Click on "Subjects Ceased Due to Date Of Birth Changes" link
    ReportsPage(page).go_to_subjects_ceased_due_to_date_of_birth_changes_page()

    # Select a "report start date" from the calendar
    page.get_by_role("button", name="Calendar").click()
    page.get_by_text("«").click()
    page.get_by_role("cell", name="18", exact=True).click()

    # Click "Generate Report"
    ReportsPage(page).click_generate_report_button()
    # Verify timestamp has updated to current date and time
    report_timestamp = DateTimeUtils.report_timestamp_date_format()
<<<<<<< HEAD
    expect(ReportsPage(page).subject_ceased_report_timestamp_element).to_contain_text(
        report_timestamp
    )

    # Open a screening subject record from the search results
    ReportsPage(page).click_nhs_number_link(page)

    # Verify page title is "Subject Demographic"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Subject Demographic"
    )


def test_failsafe_reports_allocate_sc_for_patient_movements_within_hub_boundaries(
    page: Page, tests_properties: dict
=======
    expect(report_timestamp_element).to_contain_text(report_timestamp)

    # Open a screening subject record from the search results
    nhs_number_link.click()

    # Verify page title is "Subject Demographic"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Subject Demographic"
    )


def test_failsafe_reports_allocate_sc_for_patient_movements_within_hub_boundaries(
    page: Page, tests_properties: dict
) -> None:
    """
    Confirms 'allocate_sc_for_patient_movements_within_hub_boundaries' page loads,
    the 'generate report' button works as expected
    the timestamp updates to current date and time when refreshed
    a screening subject record can be opened and
    a different SC can be allocated to a patient record
    """

<<<<<<< HEAD
=======
    report_timestamp_element = page.locator("b")
    nhs_number_link = page.locator("//*[@id='listReportDataTable']/tbody/tr[3]/td[1]")
    set_patients_screening_centre_dropdown = page.locator("#cboScreeningCentre")

>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))
    # Go to failsafe reports page
    failsafe_report_page = ReportsPage(page)
    failsafe_report_page.go_to_failsafe_reports_page()

    # Click on the "Allocate SC for Patient Movements within Hub Boundaries" link
    failsafe_report_page.go_to_allocate_sc_for_patient_movements_within_hub_boundaries_page()

    # Verify page title is "Allocate SC for Patient Movements within Hub Boundaries"
    failsafe_report_page.bowel_cancer_screening_ntsh_page_title_contains_text(
        "Allocate SC for Patient Movements within Hub Boundaries"
    )

    # Click "Generate Report"
    failsafe_report_page.click_generate_report_button()

    # Verify timestamp has updated to current date and time
<<<<<<< HEAD
    # report_timestamp = DateTimeUtils.report_timestamp_date_format()
    # expect(ReportsPage(page).common_report_timestamp_element).to_contain_text(
    #     report_timestamp
    # )

    # Open a screening subject record from the first row/first cell of the table
    ReportsPage(page).click_nhs_number_link(page)

    # Verify page title is "Set Patient's Screening Centre"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Set Patient's Screening Centre"
    )

    # Select another screening centre
    ReportsPage(page).set_patients_screening_centre_dropdown.select_option(
        tests_properties["coventry_and_warwickshire_bcs_centre"]
    )
=======
    report_timestamp = DateTimeUtils.report_timestamp_date_format()
    expect(report_timestamp_element).to_contain_text(report_timestamp)

    # Open a screening subject record from the first row/first cell of the table
    nhs_number_link.click()

    # Verify page title is "Set Patient's Screening Centre"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Set Patient's Screening Centre"
    )

    # Select another screening centre
    set_patients_screening_centre_dropdown.select_option(
        tests_properties["coventry_and_warwickshire_bcs_centre"]
    )

    # Click update
    failsafe_report_page.click_reports_pages_update_button()

    # Verify new screening centre has saved
    expect(ReportsPage(page).set_patients_screening_centre_dropdown).to_have_value(
        tests_properties["coventry_and_warwickshire_bcs_centre"]
    )


def test_failsafe_reports_allocate_sc_for_patient_movements_into_your_hub(
    page: Page,
) -> None:
    """
    Confirms 'allocate_sc_for_patient_movements_into_your_hub' page loads,
    the 'generate report' and 'refresh' buttons work as expected and
    the timestamp updates to current date and time when refreshed
    """

<<<<<<< HEAD
=======
    report_timestamp_element = page.locator("b")

>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))
    # Go to failsafe reports page
    ReportsPage(page).go_to_failsafe_reports_page()

    # Click on "allocate sc for patient movements into your hub" link
    ReportsPage(page).go_to_allocate_sc_for_patient_movements_into_your_hub_page()

    # Verify page title is "Date Report Last Requested"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Allocate SC for Patient Movements into your Hub"
    )

    # Click "Generate Report" button
    ReportsPage(page).click_generate_report_button()

    # Verify timestamp has updated to current date and time
    report_timestamp = DateTimeUtils.report_timestamp_date_format()
<<<<<<< HEAD
    expect(ReportsPage(page).common_report_timestamp_element).to_contain_text(
        report_timestamp
    )
=======
    expect(report_timestamp_element).to_contain_text(report_timestamp)
>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))

    # Click "Refresh" button
    ReportsPage(page).click_refresh_button()

    # Verify timestamp has updated to current date and time
    report_timestamp = DateTimeUtils.report_timestamp_date_format()
<<<<<<< HEAD
    expect(ReportsPage(page).common_report_timestamp_element).to_contain_text(
        report_timestamp
    )
=======
    expect(report_timestamp_element).to_contain_text(report_timestamp)
>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))


def test_failsafe_reports_identify_and_link_new_gp(page: Page) -> None:
    """
    Confirms 'identify_and_link_new_gp' page loads,
    the 'generate report' and 'refresh' buttons work as expected
    the timestamp updates to current date and time when refreshed
    a screening subject record can be opened and the Link GP practice to Screening Centre page
    can be opened from here
    """

    nhs_number_cell_link = page.locator(
        "//*[@id='listReportDataTable']/tbody/tr[3]/td[2]"
    )
    report_timestamp_element = page.locator("b")

>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))
    # Go to failsafe reports page
    ReportsPage(page).go_to_failsafe_reports_page()

    # Click on "Identify and link new GP" link
    ReportsPage(page).go_to_identify_and_link_new_gp_page()

    # Verify page title is "Identify and link new GP practices"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Identify and link new GP practices"
    )

    # Click on "Generate Report"
    ReportsPage(page).click_generate_report_button()

    # Verify timestamp has updated to current date and time
    report_timestamp = DateTimeUtils.report_timestamp_date_format()
<<<<<<< HEAD
    expect(ReportsPage(page).common_report_timestamp_element).to_contain_text(
        report_timestamp
    )
=======
    expect(report_timestamp_element).to_contain_text(report_timestamp)
>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))

    # Click "Refresh" button
    ReportsPage(page).click_refresh_button()

    # Verify timestamp has updated to current date and time
    report_timestamp = DateTimeUtils.report_timestamp_date_format()
<<<<<<< HEAD
    expect(ReportsPage(page).common_report_timestamp_element).to_contain_text(
        report_timestamp
    )

    # Open a screening subject record from the first row/second cell of the table
    ReportsPage(page).click_nhs_number_link(page)

    # Verify page title is "Link GP practice to Screening Centre"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Link GP practice to Screening Centre"
    )


# Operational Reports
def test_operational_reports_appointment_attendance_not_updated(
    page: Page, tests_properties: dict
) -> None:
=======
    expect(report_timestamp_element).to_contain_text(report_timestamp)

    # Open a screening subject record from the first row/second cell of the table
    nhs_number_cell_link.click()

    # Verify page title is "Link GP practice to Screening Centre"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Link GP practice to Screening Centre"
    )


# Operational Reports
def test_operational_reports_appointment_attendance_not_updated(
    page: Page, tests_properties: dict
) -> None:
    """
    Confirms 'appointment_attendance_not_updated' page loads,
    a SC can be selected from the dropdown
    the 'generate report' button works as expected
    the timestamp updates to current date and time when refreshed and
    an appointment record can be opened from here
    """

    nhs_number_link = page.locator(
        "#listReportDataTable > tbody > tr:nth-child(3) > td:nth-child(1) > a"
    )
    report_timestamp_element = page.locator("b")
    set_patients_screening_centre_dropdown = page.get_by_label("Screening Centre")

>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))
    # Go to operational reports page
    ReportsPage(page).go_to_operational_reports_page()

    # Go to "appointment attendance not updated" report page
    ReportsPage(page).go_to_appointment_attendance_not_updated_page()

    # Verify page title is "Appointment Attendance Not Updated"
<<<<<<< HEAD
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Appointment Attendance Not Updated"
    )

    # Select a screening centre from the drop-down options
    ReportsPage(
        page
    ).attendance_not_updated_set_patients_screening_centre_dropdown.select_option(
        tests_properties["coventry_and_warwickshire_bcs_centre"]
    )
=======
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text("Appointment Attendance Not Updated")

    # Select a screening centre from the drop-down options
    set_patients_screening_centre_dropdown.select_option(
        tests_properties["coventry_and_warwickshire_bcs_centre"]
    )

    # Click "Generate Report" button
    ReportsPage(page).click_generate_report_button()

    # Verify timestamp has updated to current date and time
    report_timestamp = DateTimeUtils.report_timestamp_date_format()
<<<<<<< HEAD
    expect(ReportsPage(page).common_report_timestamp_element).to_contain_text(
        report_timestamp
    )

    # Open an appointment record from the report
    ReportsPage(page).click_nhs_number_link(page)

    # Verify the page title is "Appointment Detail"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Appointment Detail"
    )
=======
    expect(report_timestamp_element).to_contain_text(report_timestamp)

    # Open an appointment record from the report
    nhs_number_link.click()

    # Verify the page title is "Appointment Detail"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Appointment Detail"
    )


def test_operational_reports_fobt_kits_logged_but_not_read(page: Page) -> None:
    """
    Confirms 'fobt_kits_logged_but_not_read' page loads,
    the 'refresh' button works as expected and
    the timestamp updates to current date and time when refreshed
    """

<<<<<<< HEAD
=======
    report_generated_timestamp = page.locator("#report-generated")

>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))
    # Go to operational reports page
    ReportsPage(page).go_to_operational_reports_page()

    # Go to "FOBT Kits Logged but Not Read" page
    ReportsPage(page).go_to_fobt_kits_logged_but_not_read_page()

    # Verify page title is "FOBT Kits Logged but Not Read - Summary View"
    BasePage(page).bowel_cancer_screening_page_title_contains_text(
        "FOBT Kits Logged but Not Read - Summary View"
    )

    # Click refresh button
    ReportsPage(page).click_refresh_button()

    # Verify timestamp has updated to current date and time
    report_timestamp = (
        DateTimeUtils.fobt_kits_logged_but_not_read_report_timestamp_date_format()
    )
    expect(report_generated_timestamp).to_contain_text(
        f"Report generated on {report_timestamp}."
    )


def test_operational_reports_demographic_update_inconsistent_with_manual_update(
    page: Page,
) -> None:
    """
    Confirms 'demographic_update_inconsistent_with_manual_update' page loads,
    the 'refresh' button works as expected and
    the timestamp updates to current date and time when refreshed
    """
    # Go to operational reports page
    ReportsPage(page).go_to_operational_reports_page()

    # Go to "Demographic Update Inconsistent With Manual Update" page
    ReportsPage(page).go_to_demographic_update_inconsistent_with_manual_update_page()

    # Verify page title is "Demographic Update Inconsistent With Manual Update"
    BasePage(page).bowel_cancer_screening_page_title_contains_text(
        "Demographic Update Inconsistent With Manual Update"
    )


def test_operational_reports_screening_practitioner_6_weeks_availability_not_set_up(
    page: Page, tests_properties: dict
) -> None:
    """
    Confirms 'screening_practitioner_6_weeks_availability_not_set_up_report' page loads,
    a SC can be selected
    the 'generate report' and 'refresh' buttons work as expected and
    the timestamp updates to current date and time when refreshed
    """

<<<<<<< HEAD
=======
    set_patients_screening_centre_dropdown = page.get_by_label("Screening Centre")
    report_generated_timestamp_element = page.locator("#displayGenerateDate")

>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))
    # Go to operational reports page
    ReportsPage(page).go_to_operational_reports_page()

    # Go to "Screening Practitioner 6 Weeks Availability Not Set Up" page
<<<<<<< HEAD
    ReportsPage(
        page
    ).go_to_screening_practitioner_6_weeks_availability_not_set_up_report_page()

    # Verify page title is "Screening Practitioner 6 Weeks Availability Not Set Up"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Screening Practitioner 6 Weeks Availability Not Set Up"
    )

    # Select a screening centre
    ReportsPage(
        page
    ).six_weeks_availability_not_set_up_set_patients_screening_centre_dropdown.select_option(
        tests_properties["coventry_and_warwickshire_bcs_centre"]
    )
=======
    ReportsPage(page).go_to_screening_practitioner_6_weeks_availability_not_set_up_report_page()

    # Verify page title is "Screening Practitioner 6 Weeks Availability Not Set Up"
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Screening Practitioner 6 Weeks Availability Not Set Up"
    )

    # Select a screening centre
    set_patients_screening_centre_dropdown.select_option(
        tests_properties["coventry_and_warwickshire_bcs_centre"]
    )

    # Click "Generate Report"
    ReportsPage(page).click_generate_report_button()

    # Verify timestamp has updated to current date and time
    report_timestamp = DateTimeUtils.report_timestamp_date_format()
<<<<<<< HEAD
    ReportsPage(
        page
    ).six_weeks_availability_not_set_up_report_timestamp_element.to_contain_text(
        report_timestamp
    )
=======
    expect(report_generated_timestamp_element).to_contain_text(report_timestamp)
>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))

    # Click "Refresh" button
    ReportsPage(page).click_refresh_button()

    # Verify timestamp has updated to current date and time
    report_timestamp = DateTimeUtils.report_timestamp_date_format()
<<<<<<< HEAD
    ReportsPage(
        page
    ).six_weeks_availability_not_set_up_report_timestamp_element.to_contain_text(
        report_timestamp
    )


def test_operational_reports_screening_practitioner_appointments(
    page: Page, tests_properties: dict
) -> None:
=======
    expect(report_generated_timestamp_element).to_contain_text(report_timestamp)


@pytest.mark.only
def test_operational_reports_screening_practitioner_appointments(
    page: Page, tests_properties: dict
) -> None:
    """
    Confirms 'screening_practitioner_appointments' page loads,
    a SC and Screening Practitioner can be selected
    the 'generate report' button works as expected and
    the timestamp updates to current date and time when refreshed
    """

<<<<<<< HEAD
=======
    set_patients_screening_centre_dropdown = page.get_by_label("Screening Centre")
    screening_practitioner_dropdown = page.locator("#A_C_NURSE")
    generate_report_button = page.locator(
        "#submitThisForm"
    )  # The locator appears to be unique to this generate report button
    report_timestamp_element = page.locator("b")

>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))
    # Go to operational reports page
    ReportsPage(page).go_to_operational_reports_page()

    # Go to "Screening Practitioner Appointments" page
    ReportsPage(page).go_to_screening_practitioner_appointments_page()

    # Verify page title is "Screening Practitioner Appointments"
<<<<<<< HEAD
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text(
        "Screening Practitioner Appointments"
    )

    # Select a screening centre
    ReportsPage(
        page
    ).practitioner_appointments_set_patients_screening_centre_dropdown.select_option(
        tests_properties["coventry_and_warwickshire_bcs_centre"]
    )

    # Select a screening practitioner
    ReportsPage(page).screening_practitioner_dropdown.select_option(
        tests_properties["screening_practitioner_named_another_stubble"]
    )

    # Click "Generate Report"
    ReportsPage(page).operational_reports_sp_appointments_generate_report_button.click()

    # Verify timestamp has updated to current date and time
    report_timestamp = (
        DateTimeUtils.screening_practitioner_appointments_report_timestamp_date_format()
    )
    expect(ReportsPage(Page).common_report_timestamp_element).to_contain_text(
        report_timestamp
    )
=======
    BasePage(page).bowel_cancer_screening_ntsh_page_title_contains_text("Screening Practitioner Appointments")

    # Select a screening centre
    set_patients_screening_centre_dropdown.select_option(
        tests_properties["coventry_and_warwickshire_bcs_centre"]
    )

    # Select a screening practitioner
    screening_practitioner_dropdown.select_option(
        tests_properties["screening_practitioner_named_another_stubble"]
    )

    # Click "Generate Report"
    generate_report_button.click()

    # Verify timestamp has updated to current date and time
    report_timestamp = (
        DateTimeUtils.screening_practitioner_appointments_report_timestamp_date_format()
    )
    expect(report_timestamp_element).to_contain_text(report_timestamp)
>>>>>>> 9311a0b (BCSS-20020: Compartment 1 Smokescreen Tests (#7))
