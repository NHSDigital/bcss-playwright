import logging
import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page
from classes.repositories.general_repository import GeneralRepository
from pages.base_page import BasePage
from pages.datasets.colonoscopy_dataset_page import (
    ColonoscopyDatasetsPage,
    FitForColonoscopySspOptions,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.logout.log_out_page import LogoutPage
from pages.screening_practitioner_appointments.appointment_detail_page import (
    AppointmentDetailPage,
)
from pages.screening_subject_search.advance_lynch_surveillance_episode_page import (
    AdvanceLynchSurveillanceEpisodePage,
)
from pages.screening_subject_search.contact_with_patient_page import (
    ContactWithPatientPage,
)
from pages.screening_subject_search.episode_events_and_notes_page import (
    EpisodeEventsAndNotesPage,
)
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils import screening_subject_page_searcher
from utils.appointments import book_appointments
from utils.batch_processing import batch_processing
from utils.calendar_picker import CalendarPicker
from utils.lynch_utils import LynchUtils
from utils.oracle.oracle import OracleDB
from utils.subject_assertion import subject_assertion
from utils.user_tools import UserTools


@pytest.mark.usefixtures("setup_org_and_appointments")
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.lynch_regression_tests
def test_lynch_scenario_7(page: Page) -> None:
    """
    Scenario: 7 - Discharge patient choice (no result)

    G1-G2-G3-A183-A25-J10-A99-A59-A306-A396-A392-A350-C203 Lynch in age [SSCL13b(A350)]

    This scenario tests where the subject is invited for a diagnostic test, but cancels the test (giving an episode result of "No result") and decides not to continue.

    Scenario summary:

    > Process Lynch diagnosis for a new in-age subject suitable for immediate invitation
    > Run Lynch invitations > G1 (5.1)
    > Process G1 letter batch > G2 (5.1)
    > Run timed events > G3 (5.1)
    > Book appointment > A183 (1.11)
    > Process A183 letter batch > A25 (1.11)
    > Attend appointment > J10 (1.12)
    > Suitable for Endoscopic Test > A99 (2.1)
    > Invite for Diagnostic Test > A59 (2.1)
    > Cancel Diagnostic Test > A306 (2.1)
    > Close Episode - Patient Choice > A396 (2.3)
    > Process A396 letter batch > A392 (2.3)
    > Process A392 letter batch > A350 (2.3)
    > Check recall [SSCL13b(A350)]
    """
    # Given I log in to BCSS "England" as user role "Hub Manager"
    user_role = UserTools.user_login(
        page, "Hub Manager State Registered at BCS01", return_role_type=True
    )
    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    # When I receive Lynch diagnosis "MSH6" for a new subject in my hub aged "35" with diagnosis date "1 year ago" and no last colonoscopy date
    nhs_no = LynchUtils(page).insert_validated_lynch_patient_from_new_subject_with_age(
        age="35",
        gene="MSH6",
        when_diagnosis_took_place="1 year ago",
        when_last_colonoscopy_took_place="unknown",
        user_role=user_role,
    )

    # Then Comment: NHS number
    assert nhs_no is not None
    logging.info(f"[SUBJECT CREATION] Created Lynch subject with NHS number: {nhs_no}")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "Calculated FOBT due date": "Null",
            "Calculated lynch due date": "Null",
            "Calculated surveillance due date": "Null",
            "Lynch due date": "Null",
            "Lynch due date date of change": "Null",
            "Lynch due date reason": "Null",
            "Previous screening status": "Null",
            "Screening due date": "Null",
            "Screening due date date of change": "Null",
            "Screening due date reason": "Null",
            "Subject has lynch diagnosis": "Yes",
            "Subject lower FOBT age": "Default",
            "Subject lower lynch age": "35",
            "Screening status": "Lynch Surveillance",
            "Screening status date of change": "Today",
            "Screening status reason": "Eligible for Lynch Surveillance",
            "Subject age": "35",
            "Surveillance due date": "Null",
            "Surveillance due date date of change": "Null",
            "Surveillance due date reason": "Null",
        },
        user_role,
    )

    # When I set the Lynch invitation rate for all screening centres to 50
    LynchUtils(page).set_lynch_invitation_rate(rate=50)

    # And I run the Lynch invitations process
    GeneralRepository().run_lynch_invitations()

    # And my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "Calculated FOBT due date": "Null",
            "Calculated lynch due date": "Unchanged",
            "Calculated surveillance due date": "Null",
            "Lynch due date": "35th birthday",
            "Lynch due date date of change": "Today",
            "Lynch due date reason": "Selected for Lynch Surveillance",
            "Previous screening status": "Null",
            "Screening due date": "Null",
            "Screening due date date of change": "Null",
            "Screening due date reason": "Null",
            "Subject has an open episode": "Yes",
            "Subject has lynch diagnosis": "Yes",
            "Subject lower FOBT age": "Default",
            "Subject lower lynch age": "35",
            "Screening status": "Lynch Surveillance",
            "Screening status date of change": "Today",
            "Screening status reason": "Eligible for Lynch Surveillance",
            "Subject age": "35",
            "Surveillance due date": "Null",
            "Surveillance due date date of change": "Null",
            "Surveillance due date reason": "Null",
        },
    )

    # And there is a "G1" letter batch for my subject with the exact title "Lynch Surveillance Pre-invitation"
    # When I process the open "G1" letter batch for my subject
    batch_processing(page, "G1", "Lynch Surveillance Pre-invitation")

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"latest event status": "G2 Lynch Pre-invitation Sent"})

    # When I run Timed Events for my subject
    OracleDB().exec_bcss_timed_events(nhs_number=nhs_no)

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "G3 Lynch Surveillance Colonoscopy Assessment Appointment Required"
        },
    )

    logging.info("Progress the episode through to closure")

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the practitioner appointment booking screen
    SubjectScreeningSummaryPage(page).click_book_practitioner_clinic_button()

    # And I select "BCS001" as the screening centre where the practitioner appointment will be held
    # And I set the practitioner appointment date to "today"
    # And I book the "earliest" available practitioner appointment on this date
    book_appointments(
        page,
        "BCS001 - Wolverhampton Bowel Cancer Screening Centre",
        "The Royal Hospital (Wolverhampton)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A183 1st Colonoscopy Assessment Appointment Requested",
        },
    )

    # And there is a "A183" letter batch for my subject with the exact title "Practitioner Clinic 1st Appointment (Lynch)"
    # When I process the open "A183" letter batch for my subject
    batch_processing(page, "A183", "Practitioner Clinic 1st Appointment (Lynch)")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A25 1st Colonoscopy Assessment Appointment Booked, letter sent",
        },
    )

    # When I switch users to BCSS "England" as user role "Screening Centre Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(page, "Screening Centre Manager at BCS001", True)
    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page).expand_episodes_list()
    SubjectScreeningSummaryPage(page).click_first_lynch_surveillance_episode_link()

    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # And I attend the subject's practitioner appointment "yesterday"
    AppointmentDetailPage(page).mark_appointment_as_attended(
        datetime.today() - timedelta(days=1)
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "J10 Attended Colonoscopy Assessment Appointment",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I edit the Colonoscopy Assessment Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_colonoscopy_show_datasets()

    # And I update the Colonoscopy Assessment Dataset with the following values:
    ColonoscopyDatasetsPage(page).select_fit_for_colonoscopy_option(
        FitForColonoscopySspOptions.YES
    )
    ColonoscopyDatasetsPage(page).click_dataset_complete_radio_button_yes()

    # And I save the Colonoscopy Assessment Dataset
    ColonoscopyDatasetsPage(page).save_dataset()

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I advance the subject's episode for "Suitable for Endoscopic Test"
    SubjectScreeningSummaryPage(page).click_advance_lynch_surveillance_episode_button()
    AdvanceLynchSurveillanceEpisodePage(
        page
    ).click_suitable_for_endoscopic_test_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A99 Suitable for Endoscopic Test",
        },
    )

    # When I view the advance episode options
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_lynch_surveillance_episode_button()

    # And I select Diagnostic Test Type "Colonoscopy"
    AdvanceLynchSurveillanceEpisodePage(page).select_test_type_dropdown_option(
        "Colonoscopy"
    )

    # And I enter a Diagnostic Test First Offered Appointment Date of "today"
    AdvanceLynchSurveillanceEpisodePage(page).click_calendar_button()
    CalendarPicker(page).v1_calender_picker(datetime.today())

    # And I advance the subject's episode for "Invite for Diagnostic Test >>"
    AdvanceLynchSurveillanceEpisodePage(page).click_invite_for_diagnostic_test_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A59 Invited for Diagnostic Test",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I advance the subject's episode for "Cancel Diagnostic Test"
    SubjectScreeningSummaryPage(page).click_advance_lynch_surveillance_episode_button()
    AdvanceLynchSurveillanceEpisodePage(page).click_cancel_diagnostic_test_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A306 Cancel Diagnostic Test",
        },
    )

    # When I select the advance episode option for "Record Contact with Patient"
    AdvanceLynchSurveillanceEpisodePage(page).click_record_contact_with_patient_button()

    # And I record contact with the subject with outcome "Close Episode - Patient Choice"
    ContactWithPatientPage(page).record_contact("Close Episode - Patient Choice")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A396 Discharged from Screening Round - Patient Choice",
        },
    )

    # And there is a "A396" letter batch for my subject with the exact title "Discharge from screening round - patient decision (letter to patient) (Lynch)"
    # When I process the open "A396" letter batch for my subject
    batch_processing(
        page,
        "A396",
        "Discharge from screening round - patient decision (letter to patient) (Lynch)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A392 Patient Discharge Letter Printed - Patient Choice",
        },
    )

    # And there is a "A392" letter batch for my subject with the exact title "Discharge from screening round - patient decision (letter to GP) (Lynch)"
    # When I process the open "A392" letter batch for my subject
    batch_processing(
        page,
        "A392",
        "Discharge from screening round - patient decision (letter to GP) (Lynch)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "calculated fobt due date": "Null",
            "calculated lynch due date": "2 years from episode end",
            "calculated surveillance due date": "Null",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "No result",
            "latest episode recall calculation method": "Episode end date",
            "latest episode recall episode type": "Lynch Surveillance",
            "latest episode recall surveillance type": "Null",
            "latest episode status reason": "Informed dissent",
            "latest event status": "A350 Letter of Non-agreement to Continue with Investigation sent to GP",
            "lynch due date": "Calculated Lynch due date",
            "lynch due date date of change": "Today",
            "lynch due date reason": "Lynch Surveillance",
            "lynch incident episode": "Null",
            "screening due date": "Null",
            "screening due date date of change": "Unchanged",
            "screening due date reason": "Unchanged",
            "screening status": "Lynch Surveillance",
            "screening status date of change": "Unchanged",
            "screening status reason": "Lynch Surveillance",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Unchanged",
            "surveillance due date reason": "Unchanged",
        },
    )

    LogoutPage(page).log_out()
