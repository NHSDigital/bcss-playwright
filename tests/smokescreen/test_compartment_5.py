import pytest
from playwright.sync_api import Page
from pages.logout.log_out_page import Logout
from pages.base_page import BasePage
from pages.screening_practitioner_appointments.screening_practitioner_appointments import (
    ScreeningPractitionerAppointmentsPage,
)
from pages.datasets.subject_datasets_page import (
    SubjectDatasetsPage,
)
from pages.datasets.colonoscopy_dataset_page import (
    ColonoscopyDatasetsPage,
    FitForColonoscopySspOptions,
    AsaGradeOptions,
)
from pages.screening_subject_search.subject_screening_summary import (
    SubjectScreeningSummary,
)
from pages.screening_subject_search.advance_fobt_screening_episode_page import (
    AdvanceFOBTScreeningEpisode,
)
from pages.screening_practitioner_appointments.screening_practitioner_day_view import (
    ScreeningPractitionerDayView,
)
from pages.screening_practitioner_appointments.appointment_detail_page import (
    AppointmentDetail,
)
from pages.screening_practitioner_appointments.appointment_calendar_page import (
    AppointmentCalendar,
)
from pages.screening_subject_search.attend_diagnostic_test_page import (
    AttendDiagnosticTest,
)
from utils.user_tools import UserTools
from utils.load_properties_file import PropertiesFile
from utils.screening_subject_page_searcher import verify_subject_event_status_by_nhs_no
from utils.calendar_picker import CalendarPicker
from utils.oracle.oracle_specific_functions import get_subjects_with_booked_appointments
from datetime import datetime, timedelta
import logging


@pytest.fixture
def smokescreen_properties() -> dict:
    return PropertiesFile().get_smokescreen_properties()


@pytest.mark.vpn_required
@pytest.mark.smokescreen
@pytest.mark.compartment5
def test_compartment_5(page: Page, smokescreen_properties: dict) -> None:
    """
    This is the main compartment 5 method
    It involves marking the attendance of subjects to their screening practitioner appointments
    Then it invites them for colonoscopy
    Then it marks post investigation appointment as not required
    """

    subjects_df = get_subjects_with_booked_appointments(
        smokescreen_properties["c5_eng_number_of_screening_appts_to_attend"]
    )

    UserTools.user_login(page, "Screening Centre Manager at BCS001")

    for subject_num in range(subjects_df.shape[0]):

        date_from_util = subjects_df["appointment_date"].iloc[subject_num].date()

        name_from_util = f"{str(subjects_df["person_given_name"].iloc[subject_num]).upper()} {str(subjects_df["person_family_name"].iloc[subject_num]).upper()}"

        nhs_no = subjects_df["subject_nhs_number"].iloc[subject_num]

        logging.info(
            f"\nAttending appointment for:\nSubject Name: {name_from_util}\nSubject NHS no: {nhs_no}\nSubject Appointment Date: {date_from_util}"
        )

        BasePage(page).go_to_screening_practitioner_appointments_page()
        ScreeningPractitionerAppointmentsPage(page).go_to_view_appointments_page()
        AppointmentCalendar(page).select_appointment_type_dropdown(
            smokescreen_properties["c5_eng_appointment_type"]
        )
        AppointmentCalendar(page).select_screening_centre_dropdown(
            smokescreen_properties["c5_eng_screening_centre"]
        )
        AppointmentCalendar(page).select_site_dropdown(
            smokescreen_properties["c5_eng_site"]
        )

        AppointmentCalendar(page).click_view_appointments_on_this_day_button()

        ScreeningPractitionerDayView(page).select_practitioner_dropdown_option(
            ["(all)", "(all having slots)"]
        )
        ScreeningPractitionerDayView(page).click_calendar_button()
        CalendarPicker(page).v1_calender_picker(date_from_util)

        logging.info(f"Looking for {name_from_util}")
        try:
            ScreeningPractitionerDayView(page).click_patient_link(name_from_util)
            logging.info(f"Found and clicked {name_from_util}")
        except Exception as e:
            pytest.fail(f"Unable to find {name_from_util}: {e}")

        AppointmentDetail(page).check_attendance_radio()
        AppointmentDetail(page).check_attended_check_box()
        AppointmentDetail(page).click_calendar_button()
        CalendarPicker(page).v1_calender_picker(datetime.today() - timedelta(1))
        AppointmentDetail(page).click_save_button()
        try:
            AppointmentDetail(page).verify_text_visible("Record updated")
            logging.info(
                f"Subject attended appointment - Record successfully updated for: {name_from_util}"
            )
        except Exception:
            pytest.fail(
                f"Subject not attended appointment - Record unsuccessfully updated for: {name_from_util}"
            )
        BasePage(page).click_main_menu_link()

    for subject_num in range(subjects_df.shape[0]):

        nhs_no = subjects_df["subject_nhs_number"].iloc[subject_num]
        name_from_util = f"{str(subjects_df["person_given_name"].iloc[subject_num]).upper()} {str(subjects_df["person_family_name"].iloc[subject_num]).upper()}"

        logging.info(
            f"\nUpdating dataset for:\nSubject Name: {name_from_util}\nSubject NHS no: {nhs_no}"
        )

        verify_subject_event_status_by_nhs_no(
            page, nhs_no, "J10 - Attended Colonoscopy Assessment Appointment"
        )

        SubjectScreeningSummary(page).click_datasets_link()
        SubjectDatasetsPage(page).click_colonoscopy_show_datasets()

        ColonoscopyDatasetsPage(page).select_asa_grade_option(AsaGradeOptions.FIT.value)
        ColonoscopyDatasetsPage(page).select_fit_for_colonoscopy_option(
            FitForColonoscopySspOptions.YES.value
        )
        ColonoscopyDatasetsPage(page).click_dataset_complete_radio_button_yes()
        ColonoscopyDatasetsPage(page).save_dataset()
        BasePage(page).click_back_button()
        BasePage(page).click_back_button()

        SubjectScreeningSummary(page).click_advance_fobt_screening_episode_button()
        AdvanceFOBTScreeningEpisode(page).click_suitable_for_endoscopic_test_button()

        AdvanceFOBTScreeningEpisode(page).click_calendar_button()
        CalendarPicker(page).v1_calender_picker(datetime.today())

        AdvanceFOBTScreeningEpisode(page).select_test_type_dropdown_option(
            "Colonoscopy"
        )

        logging.info(f"Inviting {name_from_util} to diagnostic test")
        AdvanceFOBTScreeningEpisode(page).click_invite_for_diagnostic_test_button()
        SubjectScreeningSummary(page).verify_latest_event_status_value(
            "A59 - Invited for Diagnostic Test"
        )

        logging.info(f"{name_from_util} attended diagnostic test")
        AdvanceFOBTScreeningEpisode(page).click_attend_diagnostic_test_button()

        AttendDiagnosticTest(page).select_actual_type_of_test_dropdown_option(
            "Colonoscopy"
        )
        AttendDiagnosticTest(page).click_calendar_button()
        CalendarPicker(page).v1_calender_picker(datetime.today())
        AttendDiagnosticTest(page).click_save_button()
        SubjectScreeningSummary(page).verify_latest_event_status_value(
            "A259 - Attended Diagnostic Test"
        )

        SubjectScreeningSummary(page).click_advance_fobt_screening_episode_button()

        AdvanceFOBTScreeningEpisode(page).click_other_post_investigation_button()
        AdvanceFOBTScreeningEpisode(page).verify_latest_event_status_value(
            "A361 - Other Post-investigation Contact Required"
        )

        AdvanceFOBTScreeningEpisode(
            page
        ).click_record_other_post_investigation_contact_button()

        page.locator("#UI_DIRECTION").select_option(label="To patient")
        page.locator("#UI_CALLER_ID").select_option(index=1)
        page.get_by_role("button", name="Calendar").click()
        CalendarPicker(page).v1_calender_picker(datetime.today())
        page.locator("#UI_START_TIME").click()
        page.locator("#UI_START_TIME").fill("11:00")
        page.locator("#UI_END_TIME").click()
        page.locator("#UI_END_TIME").fill("12:00")
        page.locator("#UI_COMMENT_ID").click()
        page.locator("#UI_COMMENT_ID").fill("Test Automation")
        page.locator("#UI_OUTCOME").select_option(
            label="Post-investigation Appointment Not Required"
        )
        page.get_by_role("button", name="Save").click()

        verify_subject_event_status_by_nhs_no(
            page, nhs_no, "A323 - Post-investigation Appointment NOT Required"
        )

    Logout(page).log_out()
