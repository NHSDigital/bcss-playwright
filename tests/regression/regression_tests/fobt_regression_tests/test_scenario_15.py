import pytest
import logging
from datetime import datetime, timedelta
from playwright.sync_api import Page
from classes.subject.subject import Subject
from classes.user.user import User
from utils.calendar_picker import CalendarPicker
from utils.user_tools import UserTools
from utils.subject_assertion import subject_assertion
from utils import screening_subject_page_searcher
from utils.batch_processing import batch_processing
from utils.fit_kit import FitKitLogged, FitKitGeneration
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from utils.appointments import book_appointments
from utils.oracle.oracle import OracleDB
from utils.investigation_dataset import InvestigationDatasetCompletion
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.screening_subject_search.diagnostic_test_outcome_page import (
    DiagnosticTestOutcomePage,
    OutcomeOfDiagnosticTest,
)
from pages.logout.log_out_page import LogoutPage
from pages.base_page import BasePage
from pages.screening_subject_search.episode_events_and_notes_page import (
    EpisodeEventsAndNotesPage,
)
from pages.screening_practitioner_appointments.appointment_detail_page import (
    AppointmentDetailPage,
)
from pages.screening_subject_search.advance_fobt_screening_episode_page import (
    AdvanceFOBTScreeningEpisodePage,
)
from pages.screening_subject_search.attend_diagnostic_test_page import (
    AttendDiagnosticTestPage,
)
from pages.screening_subject_search.record_diagnosis_date_page import (
    RecordDiagnosisDatePage,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.datasets.colonoscopy_dataset_page import (
    ColonoscopyDatasetsPage,
    FitForColonoscopySspOptions,
)
from pages.datasets.investigation_dataset_page import (
    InvestigationDatasetsPage,
    FailureReasonsOptions,
    DrugTypeOptions,
    BowelPreparationQualityOptions,
    ComfortOptions,
    EndoscopyLocationOptions,
    InsufflationOptions,
    LateOutcomeOptions,
    OutcomeAtTimeOfProcedureOptions,
    YesNoOptions,
    EndoscopyLocationOptions,
    CompletionProofOptions,
    PolypAccessOptions,
    PolypClassificationOptions,
    PolypInterventionDeviceOptions,
    PolypInterventionExcisionTechniqueOptions,
    PolypInterventionModalityOptions,
    PolypInterventionRetrievedOptions,
    PolypTypeOptions,
    AdenomaSubTypeOptions,
    PolypExcisionCompleteOptions,
    PolypDysplasiaOptions,
    YesNoUncertainOptions,
    ReasonPathologyLostOptions,
)
from pages.screening_subject_search.reopen_fobt_screening_episode_page import (
    ReopenFOBTScreeningEpisodePage,
)
from pages.screening_subject_search.contact_with_patient_page import (
    ContactWithPatientPage,
)
from classes.repositories.person_repository import PersonRepository
from classes.repositories.episode_repository import EpisodeRepository
from utils.sspi_change_steps import SSPIChangeSteps
from pages.organisations.organisations_page import OrganisationSwitchPage


@pytest.mark.wip
@pytest.mark.usefixtures("setup_org_and_appointments")
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.fobt_regression_tests
def test_scenario_15(page: Page) -> None:
    """
    Scenario: 15: High-risk findings result from accumulation of polyps

    S9-S10-S43-A8-A183-A25-J10-J15-J10-A99-A59-A259-A315-(A50)-(A167)-A360-A410-A415-A416-A316-A430-A395-A99-A59-A259-A315-A361-A323-A317-A318-A158-AC293 [SSCL53a]

    This scenario proves that an episode result of High-risk findings can be achieved by accumulating the polyps across more than one diagnostic test.  It also includes a redirect to establish suitability for diagnostic tests, the "further review" functionality of a colonoscopy assessment dataset, where the suitability chosen from the Advance Episode screen does not match with the suitability stored in the dataset.

    The second diagnostic test is carried out by a clinician accredited for Resect & Discard: the polyp category of a retrieved and resected & discarded polyp is checked as follows:
    > Polyp 1 (r&d) category is Premalignant: size < 10mm.

    Scenario summary:
    > Find an in-age subject at S9 whose episode started recently before today (1.1)
    > Run timed events > creates S9 letter (1.1)
    > Process S9 letter batch > S10 (1.1)
    > Log kit > S43 (1.2)
    > Read kit with ABNORMAL result > A8 (1.3)
    > Invite for colonoscopy assessment > A183 (1.11)
    > Process A183 appointment letter > A25 (1.11)
    > Attend assessment appointment > J10 (1.11)
    > Unsuitable for diagnostic tests > J15 (1.12)
    > Redirect to establish suitability for diagnostic tests > J10 (1.12)
    > Suitable for colonoscopy > A99 (1.12)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset – Abnormal (some polyps) (2.1)
    > Enter diagnostic test outcome – refer another test > A315 (2.1)
    > Record diagnosis date (A50)
    > Process A183 result letter (A167) (1.11)
    > Post-investigation appointment required > A360 (2.1)
    > Book post-investigation appointment > A410 (2.4)
    > Process A410 letter batch > A415 (2.4)
    > Attend post-investigation appointment > A416 > A316 > A430 (2.4)
    > Process A430 letter batch > A395 (2.4)
    > Record patient contact – contacted, suitable for colonoscopy > A99 (2.2)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset – more polyps now makes High-risk findings (2.1)
    > Enter diagnostic test outcome – investigation complete > A315 (2.1)
    > Post-investigation appointment not required > A361 (2.1)
    > Record patient contact – post-investigation appointment not required > A323 (2.1) > A317 > A318 (2.5)
    > Process A318 letter batch > A158 (2.5) > C203 (2.8, 1.13)
    > Check recall [SSCL53a]
    """
    # Given I log in to BCSS "England" as user role "Hub Manager"
    user_role = UserTools.user_login(
        page, "Hub Manager State Registered at BCS01", return_role_type=True
    )
    if user_role is None:
        raise ValueError("This user cannot be assigned to a UserRoleType")

    # And there is a subject who meets the following criteria:
    criteria = {
        "latest event status": "S9 Pre-Invitation Sent",
        "latest episode kit class": "FIT",
        "latest episode started": "Within the last 6 months",
        "latest episode type": "FOBT",
        "subject age": "Between 60 and 71",
        "subject has unprocessed sspi updates": "No",
        "subject has user dob updates": "No",
    }

    query, bind_vars = SubjectSelectionQueryBuilder().build_subject_selection_query(
        criteria=criteria,
        user=User(),
        subject=Subject(),
        subjects_to_retrieve=1,
    )

    nhs_no_df = OracleDB().execute_query(query=query, parameters=bind_vars)
    nhs_no = nhs_no_df["subject_nhs_number"].iloc[0]

    # Then Comment: NHS number
    logging.info(f"[SUBJECT RETRIEVAL] Retrieved subject's NHS number: {nhs_no}")

    # When I run Timed Events for my subject
    OracleDB().exec_bcss_timed_events(nhs_number=nhs_no)

    # Then there is a "S9" letter batch for my subject with the exact title "Invitation & Test Kit (FIT)"
    # When I process the open "S9" letter batch for my subject
    batch_processing(
        page,
        "S9",
        "Invitation & Test Kit (FIT)",
        "S10 - Invitation & Test Kit Sent",
    )

    # When I log my subject's latest unlogged FIT kit
    fit_kit = FitKitGeneration().get_fit_kit_for_subject_sql(
        nhs_no=nhs_no, logged=False, read=False
    )
    FitKitLogged().log_fit_kits(page=page, fit_kit=fit_kit, sample_date=datetime.now())

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "S43 Kit Returned and Logged (Initial Test)"},
    )

    # When I read my subject's latest logged FIT kit as "ABNORMAL"
    FitKitLogged().read_latest_logged_kit(
        user=user_role, kit_type=2, kit=fit_kit, kit_result="ABNORMAL"
    )

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"latest event status": "A8 Abnormal"})

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(
        page=page, nhs_no=nhs_no
    )

    # And I choose to book a practitioner clinic for my subject
    SubjectScreeningSummaryPage(page).click_book_practitioner_clinic_button()

    # And I select "BCS001" as the screening centre where the practitioner appointment will be held
    # And I set the practitioner appointment date to "today"
    # And I book the "earliest" available practitioner appointment on this date
    book_appointments(
        page=page,
        screening_centre="BCS001 - Wolverhampton Bowel Cancer Screening Centre",
        site="The Royal Hospital (Wolverhampton)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_number=nhs_no,
        criteria={
            "latest event status": "A183 1st Colonoscopy Assessment Appointment Requested"
        },
    )

    # And there is a "A183" letter batch for my subject with the exact title "Practitioner Clinic 1st Appointment"
    # When I process the open "A183 - Practitioner Clinic 1st Appointment" letter batch for my subject
    # Then my subject has been updated as follows:
    batch_processing(
        page,
        "A183",
        "Practitioner Clinic 1st Appointment",
        "A25 - 1st Colonoscopy Assessment Appointment Booked, letter sent",
    )

    # When I switch users to BCSS "England" as user role "Screening Centre Manager"
    LogoutPage(page).log_out(False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(page, "Screening Centre Manager at BCS001", True)
    if user_role is None:
        raise ValueError("User role is none")

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page).expand_episodes_list()
    SubjectScreeningSummaryPage(page).click_first_fobt_episode_link()

    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # And I attend the subject's practitioner appointment "2 days ago"
    AppointmentDetailPage(page).mark_appointment_as_attended(
        date=datetime.today() - timedelta(days=2)
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_number=nhs_no,
        criteria={
            "latest event status": "J10 Attended Colonoscopy Assessment Appointment",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(
        page=page, nhs_no=nhs_no
    )

    # And I edit the Colonoscopy Assessment Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_colonoscopy_show_datasets()

    # And I update the Colonoscopy Assessment Dataset with the following values:
    ColonoscopyDatasetsPage(page).select_fit_for_colonoscopy_option(
        option=FitForColonoscopySspOptions.NO
    )
    ColonoscopyDatasetsPage(page).click_dataset_complete_radio_button_yes()

    # And I save the Colonoscopy Assessment Dataset
    ColonoscopyDatasetsPage(page).save_dataset()

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(
        page=page, nhs_no=nhs_no
    )

    # And I advance the subject's episode for "Not Suitable for Diagnostic Tests"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(
        page
    ).click_not_suitable_for_diagnostic_tests_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_number=nhs_no,
        criteria={"latest event status": "J15 Not Suitable for Diagnostic Tests"},
    )

    # And I interrupt the subject's episode for "Redirect to Establish Suitability for Diagnostic Tests"
    AdvanceFOBTScreeningEpisodePage(page).check_exception_circumstances_checkbox()
    AdvanceFOBTScreeningEpisodePage(
        page
    ).click_redirect_to_reestablish_suitability_for_diagnostic_test_repatient_contact()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event code": "E175 Redirect to Establish Suitability for Diagnostic Tests",
            "latest event status": "J10 Attended Colonoscopy Assessment Appointment",
        },
    )

    # Then I get a confirmation prompt that "contains" "If there has been further discussion regarding the patient's suitability for a colonoscopy then the colonoscopy assessment dataset will be updated with this further review"
    AdvanceFOBTScreeningEpisodePage(page).assert_dialog_text(
        "If there has been further discussion regarding the patient's suitability for a colonoscopy then the colonoscopy assessment dataset will be updated with this further review",
        True,
    )

    # And I select the advance episode option for "Suitable for Endoscopic Test"
    AdvanceFOBTScreeningEpisodePage(page).click_suitable_for_endoscopic_test_button()

    LogoutPage(page).log_out()
