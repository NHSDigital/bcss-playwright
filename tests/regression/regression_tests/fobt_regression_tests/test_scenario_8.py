import pytest
import logging
from datetime import datetime
from playwright.sync_api import Page
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from utils.oracle.subject_creation_util import CreateSubjectSteps
from utils.user_tools import UserTools
from utils.subject_assertion import subject_assertion
from utils.call_and_recall_utils import CallAndRecallUtils
from utils import screening_subject_page_searcher
from utils.batch_processing import batch_processing
from utils.fit_kit import FitKitLogged, FitKitGeneration
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils.appointments import book_appointments
from pages.logout.log_out_page import LogoutPage
from pages.base_page import BasePage
from pages.screening_subject_search.advance_fobt_screening_episode_page import (
    AdvanceFOBTScreeningEpisodePage,
)
from pages.screening_subject_search.record_diagnosis_date_page import (
    RecordDiagnosisDatePage,
)
from utils.appointments import AppointmentAttendance
from pages.datasets.colonoscopy_dataset_page import (
    ColonoscopyDatasetsPage,
    FitForColonoscopySspOptions,
)
from utils.sspi_change_steps import SSPIChangeSteps
from pages.screening_subject_search.reopen_fobt_screening_episode_page import (
    ReopenFOBTScreeningEpisodePage,
)
from utils.oracle.oracle import OracleDB
from utils.oracle.subject_selector import SubjectSelector
from classes.subject_selection_query_builder.subject_selection_criteria_key import (
    SubjectSelectionCriteriaKey as Key,
)


@pytest.mark.wip
@pytest.mark.usefixtures("setup_org_and_appointments")
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.fobt_regression_tests
def test_scenario_8(page: Page) -> None:
    """
    Scenario: 8: Discharge for no contact, diagnostic test result of "No result"

    S9-S10-S43-A8-A183-A25-J10-A100-A59-A172-(A167)-(A52)-A397-A391-A351-C203 [SSCL13a(A351)] A172-A100-A59-A259-A315-A360-A410-A415-A416-A316-A430-A395-A100-J10-A99-A59-A250-A315-A361-A323-A317-A318-A380-A397-A391-A351-C203 [SSCL14a(A351)]

    This scenario tests two routes to closure on A351 discharge no contact.  The first follows DNA of the diagnostic test, and the second follows attendance of a "no result" test, then contact is lost before a follow-up test can be arranged.  It tests both in-age and over-age closures, and includes two mid-episode redirects.

    Scenario summary:

    > Find an in-age subject at S9 whose episode started recently before today (1.1)
    > Run timed events > creates S9 letter (1.1)
    > Process S9 letter batch > S10 (1.1)
    > Log kit > S43 (1.2)
    > Read kit with ABNORMAL result > A8 (1.3)
    > Invite for colonoscopy assessment > A183 (1.11)
    > Process A183 appointment letter > A25 (1.11)
    > Attend assessment appointment > J10 (1.11)
    > Suitable for radiology > A100 (1.12)
    > Invite for diagnostic test > A59 (2.1)
    > Patient DNA diagnostic test > A172 (2.1)
    > Process A183 result letter (A167) (1.11)
    > Record diagnosis date reason (A52)
    > Record patient contact – not contacted, close on existing result > A397 (2.3)
    > Process A397 letter batch > A391 (2.3)
    > Process A391 letter batch > A351 (2.3) > C203 (1.13)
    > Check recall [SSCL13a(A351)]
    > Reopen to reschedule diagnostic test > A172 (2.3)
    > Suitable for radiology > A100 (2.3)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset, result = Abnormal (2.1)
    > Enter diagnostic test outcome – refer another test > A315 (2.1)
    > Post-investigation appointment required > A360 (2.1)
    > Book post-investigation appointment > A410 (2.4)
    > Process A410 letter batch > A415 (2.4)
    > Attend post-investigation appointment > A416 > A316 > A430 (2.4)
    > Process A430 letter batch > A395 (2.4)
    > Redirect to DELETE the Latest Diagnostic Test Result > A100 (2.1)
    > Redirect to establish suitability for diagnostic tests > J10 (1.11)
    > Suitable for colonoscopy > A99 (1.12)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset – no result (2.1)
    > Enter diagnostic test outcome – failed test, refer another > A315 (2.1)
    > Post-investigation appointment not required > A361 (2.1)
    > Record patient contact – post-investigation appointment not required > A323 (2.1) > A317 > A318 (2.5)
    > Process A318 letter batch > A380 (2.5)
    > Record patient contact – not contacted, close on existing result > A397 (2.3)
    > Process A397 letter batch > A391 (2.3)
    > SSPI update changes subject to over-age at recall
    > Process A391 letter batch > A351 (2.3) > C203 (1.13)
    > Check recall [SSCL14a(A351)]
    """

    summary_page = SubjectScreeningSummaryPage(page)
    attendance = AppointmentAttendance(page)
    dataset = ColonoscopyDatasetsPage(page)
    ssp_options = FitForColonoscopySspOptions
    advance_fobt_episode = AdvanceFOBTScreeningEpisodePage(page)

    logging.info(
        "[TEST START] Regression - Scenario: 8: Discharge for no contact, diagnostic test result of 'No result'"
    )
    # Given I log in to BCSS "England" as user role "Hub Manager"
    user_role = UserTools.user_login(
        page, "Hub Manager at BCS01", return_role_type=True
    )
    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    # # And there is a subject who meets the following criteria:
    # user_details = UserTools.retrieve_user("Hub Manager at BCS01")

    # criteria = {
    #     Key.LATEST_EVENT_STATUS.description: "S9 Pre-invitation Sent",
    #     Key.LATEST_EPISODE_KIT_CLASS.description: "FIT",
    #     Key.LATEST_EPISODE_STARTED.description: "Within the last 6 months",
    #     Key.LATEST_EPISODE_TYPE.description: "FOBT",
    #     Key.SUBJECT_AGE.description: "Between 60 and 72",
    #     # Key.SUBJECT_HAS_UNPROCESSED_SSPI_UPDATES.description: "No",
    #     # Key.SUBJECT_HAS_USER_DOB_UPDATES.description: "No",
    #     # Key.SUBJECT_HUB_CODE.description: user_details["hub_code"],
    # }

    # nhs_no = SubjectSelector.get_subject_for_pre_invitation(criteria)
    # subject_assertion(nhs_no, criteria)

    # # Then Comment: NHS number
    # logging.info(f"[SUBJECT FOUND] NHS number: {nhs_no}")

    # # When I run Timed Events for my subject
    # OracleDB().exec_bcss_timed_events(nhs_number=nhs_no)

    # # Then there is a "S9" letter batch for my subject with the exact title "Invitation & Test Kit (FIT)"
    # # When I process the open "S9" letter batch for my subject
    # # Then my subject has been updated as follows:
    # batch_processing(
    #     page,
    #     "S9",
    #     "Invitation & Test Kit (FIT)",
    #     "S10 - Invitation & Test Kit Sent",
    #     True,
    # )

    # # When I log my subject's latest unlogged FIT kit
    # fit_kit = FitKitGeneration().get_fit_kit_for_subject_sql(nhs_no, False, False)
    # sample_date = datetime.now()
    # FitKitLogged().log_fit_kits(page, fit_kit, sample_date)

    # # Then my subject has been updated as follows:
    # criteria = {
    #     "latest event status": "S43 Kit Returned and Logged (Initial Test)",
    # }
    # subject_assertion(nhs_no, criteria)

    # # When I read my subject's latest logged FIT kit as "ABNORMAL"
    # FitKitLogged().read_latest_logged_kit(user_role, 2, fit_kit, "ABNORMAL")

    # # Then my subject has been updated as follows:
    # criteria = {
    #     "latest event status": "A8 Abnormal",
    # }
    # subject_assertion(nhs_no, criteria)
    # # When I view the subject
    # screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # # And I choose to book a practitioner clinic for my subject
    # SubjectScreeningSummaryPage(page).click_book_practitioner_clinic_button()

    # # And I select "BCS001" as the screening centre where the practitioner appointment will be held
    # # And I set the practitioner appointment date to "today"
    # # And I book the "earliest" available practitioner appointment on this date
    # book_appointments(
    #     page,
    #     "BCS001 - Wolverhampton Bowel Cancer Screening Centre",
    #     "The Royal Hospital (Wolverhampton)",
    # )

    # # Then my subject has been updated as follows:
    # criteria = {
    #     "latest event status": "A183 1st Colonoscopy Assessment Appointment Requested",
    # }
    # subject_assertion(nhs_no, criteria)

    # # And there is a "A183" letter batch for my subject with the exact title "Practitioner Clinic 1st Appointment"
    # # When I process the open "A183 - Practitioner Clinic 1st Appointment" letter batch for my subject
    # # Then my subject has been updated as follows:
    # batch_processing(
    #     page,
    #     "A183",
    #     "Practitioner Clinic 1st Appointment",
    #     "A25 - 1st Colonoscopy Assessment Appointment Booked, letter sent",
    # )

    # # And there is a "A183" letter batch for my subject with the exact title "GP Result (Abnormal)"
    # batch_processing(
    #     page,
    #     "A183",
    #     "GP Result (Abnormal)",
    #     "A25 - 1st Colonoscopy Assessment Appointment Booked, letter sent",
    # )
    nhs_no = "9658560636"

    # # When I switch users to BCSS "England" as user role "Screening Centre Manager"
    # LogoutPage(page).log_out(close_page=False)
    # BasePage(page).go_to_log_in_page()
    # user_role = UserTools.user_login(page, "Screening Centre Manager at BCS001", True)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # # And I view the event history for the subject's latest episode
    # # And I view the latest practitioner appointment in the subject's episode
    # # And I attend the subject's practitioner appointment "yesterday"
    # attendance.mark_as_attended_yesterday()

    # # Then my subject has been updated as follows:
    # criteria = {
    #     "latest event status": "J10 Attended Colonoscopy Assessment Appointment",
    # }
    # subject_assertion(nhs_no, criteria)

    # # When I view the subject
    # screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # # And I edit the Colonoscopy Assessment Dataset for this subject
    # # And I update the Colonoscopy Assessment Dataset with the following values:
    # # 	| Fit for Colonoscopy (SSP) | No  |
    # # 	| Dataset complete?         | Yes |
    # # And I save the Colonoscopy Assessment Dataset
    # SubjectScreeningSummaryPage(page).click_datasets_link()
    # SubjectDatasetsPage(page).click_colonoscopy_show_datasets()
    # dataset.select_fit_for_colonoscopy_option(ssp_options.NO)
    # dataset.click_dataset_complete_radio_button_yes()
    # dataset.save_dataset()

    # # And I view the subject
    # screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # # And I advance the subject's episode for "Suitable for Radiological Test"
    # SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    # advance_fobt_episode.click_suitable_for_radiological_test_button()

    # # Then my subject has been updated as follows:
    # criteria = {
    #     "latest event status": "A100 Suitable for Radiological Test",
    # }
    # subject_assertion(nhs_no, criteria)

    # # When I view the advance episode options
    # SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # # And I select Diagnostic Test Type "CT Colonography"
    # # And I enter a Diagnostic Test First Offered Appointment Date of "today"
    # # And I advance the subject's episode for "Invite for Diagnostic Test >>"
    # advance_fobt_episode.select_ct_colonography_and_invite()

    # # Then my subject has been updated as follows:
    # criteria = {
    #     "which diagnostic test": "latest test in latest episode",
    #     "diagnostic test proposed type": "CT Colonography",
    #     "latest event status": "A59 Invited for Diagnostic Test",
    # }
    # subject_assertion(nhs_no, criteria)

    # # When the subject DNAs the diagnostic test
    # attendance.mark_diagnostic_test_as_dna()

    # # Then my subject has been updated as follows:
    # criteria = {
    #     "latest event status": "A172 DNA Diagnostic Test",
    # }
    # subject_assertion(nhs_no, criteria)

    # # When I switch users to BCSS "England" as user role "Hub Manager"
    # LogoutPage(page).log_out(close_page=False)
    # BasePage(page).go_to_log_in_page()
    # UserTools.user_login(page, "Hub Manager at BCS01")

    # # And I process the open "A183 - GP Result (Abnormal)" letter batch for my subject
    # # Then my subject has been updated as follows:
    # batch_processing(
    #     page,
    #     "A183",
    #     "GP Result (Abnormal)",
    #     "A172 - DNA Diagnostic Test",
    # )
    # criteria = {
    #     "latest episode includes event status": "A167 GP Abnormal FOBT Result Sent",
    #     "latest episode accumulated result": "No Result",
    # }
    # subject_assertion(nhs_no, criteria)

    # When I switch users to BCSS "England" as user role "Screening Centre Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(page, "Screening Centre Manager at BCS001", True)

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # # And I view the advance episode options
    # SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # # And I select the advance episode option for "Record Diagnosis Date"
    # AdvanceFOBTScreeningEpisodePage(page).click_record_diagnosis_date_button()

    # # And I select Diagnosis Date Reason "Patient could not be contacted"
    # RecordDiagnosisDatePage(page).record_diagnosis_reason(
    #     reason_text="Patient could not be contacted"
    # )

    # And I save Diagnosis Date Information
    # RecordDiagnosisDatePage(page).click_save_button()

    # # Then my subject has been updated as follows:
    # criteria = {
    #     "latest episode diagnosis date reason": "Patient could not be contacted",
    #     "latest episode has diagnosis date": "No",
    #     "latest episode includes event status": "A52 No diagnosis date recorded",
    # }
    # subject_assertion(nhs_no, criteria)

    # When I select the advance episode option for "Record Contact with Patient"
    # And I record contact with the subject with outcome "Close Episode - No Contact"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    advance_fobt_episode.click_record_contact_with_patient_button()
    advance_fobt_episode.record_contact_close_episode_no_contact()

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A397 Discharged  from Screening Round - No Patient Contact",
    }
    subject_assertion(nhs_no, criteria)

    # And there is a "A397" letter batch for my subject with the exact title "Discharge from screening round - no contact (letter to patient)"
    # When I process the open "A397" letter batch for my subject
    # Then my subject has been updated as follows:
    # 	| Latest event status | A391 Patient Discharge Letter Printed - No Patient Contact |
    # 	And there is a "A391" letter batch for my subject with the exact title "Discharge from screening round - no contact (letter to GP)"
    batch_processing(
        page,
        "A397",
        "Discharge from screening round - no contact (letter to patient)",
        "A391 - Patient Discharge Letter Printed - No Patient Contact",
    )
