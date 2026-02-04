import logging
from datetime import datetime, timedelta
import pytest
from classes.user.user import User
from classes.repositories.episode_repository import EpisodeRepository
from classes.repositories.person_repository import PersonRepository
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pages.datasets.colonoscopy_dataset_page import (
    ColonoscopyDatasetsPage,
    FitForColonoscopySspOptions,
)
from pages.datasets.investigation_dataset_page import (
    BowelPreparationQualityOptions,
    ComfortOptions,
    DrugTypeOptions,
    EndoscopyLocationOptions,
    FailureReasonsOptions,
    InsufflationOptions,
    InvestigationDatasetsPage,
    LateOutcomeOptions,
    OutcomeAtTimeOfProcedureOptions,
    YesNoOptions,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.logout.log_out_page import LogoutPage
from pages.organisations.organisations_page import OrganisationSwitchPage
from pages.screening_practitioner_appointments.appointment_detail_page import (
    AppointmentDetailPage,
)
from pages.screening_subject_search.advance_surveillance_episode_page import (
    AdvanceSurveillanceEpisodePage,
)
from pages.screening_subject_search.attend_diagnostic_test_page import (
    AttendDiagnosticTestPage,
)
from pages.screening_subject_search.contact_with_patient_page import (
    ContactWithPatientPage,
)
from pages.screening_subject_search.diagnostic_test_outcome_page import (
    DiagnosticTestOutcomePage,
    OutcomeOfDiagnosticTest,
    ReasonForOnwardReferral,
)
from pages.screening_subject_search.episode_events_and_notes_page import (
    EpisodeEventsAndNotesPage,
)
from pages.screening_subject_search.lnpcp_result_from_symptomatic_procedure_page import (
    LnpcpResultFromSymptomaticProcedure,
)
from pages.screening_subject_search.record_request_to_cease_page import (
    RecordRequestToCeasePage,
)
from pages.screening_subject_search.reopen_surveillance_episode_page import (
    ReopenSurveillanceEpisodePage,
)
from pages.screening_subject_search.return_from_symptomatic_referral_page import (
    ReturnFromSymptomaticReferralPage,
)
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.screening_subject_search.uncease_and_initiate_optin_episode_page import (
    UnceaseAndInitiateOptinEpisodePage,
)
from utils import screening_subject_page_searcher
from utils.appointments import book_post_investigation_appointment
from utils.batch_processing import batch_processing
from utils.calendar_picker import CalendarPicker
from utils.generate_health_check_forms_util import GenerateHealthCheckFormsUtil
from utils.investigation_dataset import InvestigationDatasetCompletion
from utils.oracle.oracle import OracleDB
from utils.sspi_change_steps import SSPIChangeSteps
from utils.subject_assertion import subject_assertion
from utils.user_tools import UserTools


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.surveillance_regression_tests
def test_surveillance_scenario_14(page: Page, general_properties: dict) -> None:
    """
    Scenario: 14: LNPCP result from symptomatic procedure, refer another diagnostic test

    X500-X505-A99-A59-A259-A315-A361-A323-A317-A353-A372-A373-A374-A157-C203 [SSCL52b] [SSUN9.7] A372-A373-A389-A360-A410-A415-A416-A316-A319-A395

    This scenario tests a subject being referred for symptomatic procedure following a "No result" diagnostic test.  The symptomatic result is LNPCP, keeping the in-age subject in Surveillance.  After the episode has closed, manually ceasing then unceasing the subject returns the subject to FOBT screening, as the user must use the Opt-in to Send a Kit option to uncease them: because their calculated FOBT due date is now in the past, they are given an immediate FOBT screening due date.  Note also than when manually ceasing a subject their FOBT due date reason is set to "Ceased" even though it is not changing, and when manually unceasing a subject, they come back into the FOBT pathway with status Opt-in - which seems a little odd, but still!

    BCSS-17906 NOTE: The pathway for referring for another diagnostic test following symptomatic procedure is currently incomplete, so stopping at A360

    Scenario summary:

    > Run surveillance invitations for 1 subject > X500 (3.1)
    > SSPI update changes subject to in-age at recall
    > Process X500 letter batch > X505 (3.1)
    > Complete the colonoscopy assessment dataset - fit for colonoscopy
    > Record patient contact – contacted, suitable for colonoscopy > A99 (3.1)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset – No result (2.1)
    > Enter diagnostic test outcome – refer symptomatic > A315 (2.1)
    > Post-investigation appointment not required > A361 (2.1)
    > Record patient contact – post-investigation appointment not required > A323 (2.1) > A317 (2.5)
    > MDT not required > A353 (2.6)
    > Process A353 letter batch > A372 (2.6)
    > Record symptomatic result – LNPCP > A373 (2.7)
    > Refer Surveillance > A374 (2.7)
    > Process A374 letter batch > A157 (2.7) > C203 (3.6)
    > Check recall [SSCL52b]
    > Manually cease subject
    > Manually uncease subject (Opt-in to Send a Kit) [SSUN9.7]
    > Reopen to Re-record Outcome from Symptomatic Referral > A372 (2.7)
    > Record symptomatic result - non-neoplastic > A373 (2.7)
    > Refer another diagnostic test > A389 (2.7)
    > Post-investigation appointment required > A360 (2.1)
    > Book post-investigation appointment > A410 (2.4)
    > Process A410 letter batch > A415 (2.4)
    > Attend post-investigation appointment > A416 > A316 > A319 (2.4)
    > Process A319 letter batch > A395 (2.4)
    """
    # Given I log in to BCSS "England" as user role "Specialist Screening Practitioner"
    user_role = UserTools.user_login(
        page, "Specialist Screening Practitioner at BCS009 & BCS001", True
    )

    OrganisationSwitchPage(page).select_organisation_by_id("BCS001")
    OrganisationSwitchPage(page).click_continue()
    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    # When I run surveillance invitations for 1 subject
    org_id = general_properties["eng_screening_centre_id"]
    nhs_no = GenerateHealthCheckFormsUtil(page).invite_surveillance_subjects_early(
        org_id
    )
    logging.info(f"[SUBJECT RETRIEVAL] Subject's NHS Number: {nhs_no}")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode status": "Open",
            "latest episode type": "Surveillance",
            "latest event status": "X500 Selected For Surveillance",
            "responsible screening centre code": "User's screening centre",
            "subject has unprocessed SSPI updates": "No",
            "subject has user DOB updates": "No",
        },
        user_role,
    )

    # And I receive an SSPI update to change their date of birth to "72" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 72)

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"subject age": "72"})

    # And there is a "X500" letter batch for my subject with the exact title "Surveillance Selection"
    # When I process the open "X500" letter batch for my subject
    batch_processing(
        page,
        "X500",
        "Surveillance Selection",
    )

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"latest event status": "X505 HealthCheck Form Printed"})

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

    # And I select the advance episode option for "Record Contact with Patient"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_record_contact_with_patient_button()

    # And I record contact with the subject with outcome "Suitable for Endoscopic Test"
    ContactWithPatientPage(page).record_contact("Suitable for Endoscopic Test")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A99 Suitable for Endoscopic Test",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()

    # And I select Diagnostic Test Type "Colonoscopy"
    AdvanceSurveillanceEpisodePage(page).select_test_type_dropdown_option("Colonoscopy")

    # And I enter a Diagnostic Test First Offered Appointment Date of "today"
    AdvanceSurveillanceEpisodePage(page).click_calendar_button()
    CalendarPicker(page).v1_calender_picker(datetime.today())

    # And I advance the subject's episode for "Invite for Diagnostic Test >>"
    AdvanceSurveillanceEpisodePage(page).click_invite_for_diagnostic_test_button()

    page.wait_for_timeout(500)  # Timeout to allow subject to update on the DB

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A59 Invited for Diagnostic Test",
        },
    )

    # When I select the advance episode option for "Attend Diagnostic Test"
    AdvanceSurveillanceEpisodePage(page).click_attend_diagnostic_test_button()

    # And I attend the subject's diagnostic test today
    AttendDiagnosticTestPage(page).click_calendar_button()
    CalendarPicker(page).v1_calender_picker(datetime.today())
    AttendDiagnosticTestPage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A259 Attended Diagnostic Test"},
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I edit the Investigation Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    # Confirm on the investigation Datasets Page
    InvestigationDatasetsPage(page).bowel_cancer_screening_page_title_contains_text(
        "Investigation Datasets"
    )

    # And I open all minimized sections on the dataset
    InvestigationDatasetsPage(page).open_all_minimized_sections()

    # When I add the following bowel preparation drugs and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_drug_information(
        {
            "drug_dose1": "3",
            "drug_type1": DrugTypeOptions.MANNITOL,
        }
    )

    # And there is a clinician who meets the following criteria:
    user = User.from_user_role_type(user_role)
    criteria = {
        "Person has current role": "Accredited Screening Colonoscopist",
        "Person has current role in organisation": "User's SC",
        "Resect & Discard accreditation status": "None",
    }
    query = PersonRepository().build_person_selection_query(
        criteria=criteria, person=None, required_person_count=1, user=user, subject=None
    )
    df = OracleDB().execute_query(query)
    person_name = (
        f"{df["person_family_name"].iloc[0]} {df["person_given_name"].iloc[0]}"
    )

    # And I set the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_general_information(
        {
            "practitioner": 1,
            "site": 1,
            "testing clinician": person_name,
            "aspirant endoscopist": None,
        }
    )

    InvestigationDatasetCompletion(page).fill_endoscopy_information(
        {
            "endoscope inserted": "yes",
            "procedure type": "diagnostic",
            "bowel preparation quality": BowelPreparationQualityOptions.GOOD,
            "comfort during recovery": ComfortOptions.NO_DISCOMFORT,
            "comfort during examination": ComfortOptions.NO_DISCOMFORT,
            "endoscopist defined extent": EndoscopyLocationOptions.DESCENDING_COLON,
            "scope imager used": YesNoOptions.YES,
            "retroverted view": YesNoOptions.YES,
            "start of intubation time": "09:00",
            "start of extubation time": "09:30",
            "end time of procedure": "10:00",
            "scope id": "Autotest",
            "insufflation": InsufflationOptions.AIR,
            "outcome at time of procedure": OutcomeAtTimeOfProcedureOptions.LEAVE_DEPARTMENT,
            "late outcome": LateOutcomeOptions.NO_COMPLICATIONS,
        }
    )

    # And I set the following failure reasons within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_failure_information(
        {"failure reasons": FailureReasonsOptions.PAIN}
    )

    # And I mark the Investigation Dataset as completed
    InvestigationDatasetsPage(page).check_dataset_complete_checkbox()

    # When I press the save Investigation Dataset button
    # Then the Investigation Dataset result message, which I will cancel, is "No Result"
    InvestigationDatasetsPage(page).click_save_dataset_button_assert_dialog("No Result")

    # When I press the save Investigation Dataset button
    InvestigationDatasetsPage(page).click_save_dataset_button()

    # And I confirm the Episode Result is "No result"
    EpisodeRepository().confirm_episode_result(nhs_no, "No Result")

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Enter Diagnostic Test Outcome"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_enter_diagnostic_test_outcome_button()

    # Then I confirm the Outcome Of Diagnostic Test dropdown has the following options:
    DiagnosticTestOutcomePage(page).test_outcome_dropdown_contains_options(
        [
            "Failed Test - Refer Another",
            "Refer Symptomatic",
        ],
    )

    # When I select Outcome of Diagnostic Test "Refer Symptomatic"
    DiagnosticTestOutcomePage(page).select_test_outcome_option(
        OutcomeOfDiagnosticTest.REFER_SYMPTOMATIC
    )

    # Then the text "Diagnostic Test Date resulting in a recall due date" is not visible
    expect(
        page.get_by_text("Diagnostic Test Date resulting in a recall due date")
    ).not_to_be_visible()

    # And I confirm the Reason for Symptomatic Referral dropdown has the following options:
    DiagnosticTestOutcomePage(
        page
    ).reason_for_symptomatic_referral_dropdown_contains_options(
        [
            "Polyp Excision",
            "Corrective Surgery",
            "Suspected Cancer Surgery",
        ],
    )

    # When I select Reason for Symptomatic Referral value "Suspected Cancer Surgery"
    DiagnosticTestOutcomePage(page).select_reason_for_symptomatic_referral_option(
        ReasonForOnwardReferral.SUSPECTED_CANCER_SURGERY
    )

    # And I save the Diagnostic Test Outcome
    DiagnosticTestOutcomePage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A315 Diagnostic Test Outcome Entered",
        },
    )

    # When I advance the subject's episode for "Other Post-investigation Contact Required"
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_other_post_investigation_contact_required_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A361 Other Post-investigation Contact Required",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Record other post-investigation contact"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_record_other_post_investigation_contact_button()

    # Then I confirm the patient outcome dropdown has the following options:
    ContactWithPatientPage(page).verify_contact_with_patient_page_is_displayed()
    ContactWithPatientPage(page).patient_outcome_dropdown_contains_options(
        [
            "Post-investigation Appointment Not Required",
            "Post-investigation Appointment Required",
            "No outcome",
        ],
    )

    # When I record contact with the subject with outcome "Post-investigation Appointment Not Required"
    ContactWithPatientPage(page).record_post_investigation_appointment_not_required()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A323 Post-investigation Appointment NOT Required",
            "latest event status": "A317 Post-investigation Contact Made",
        },
    )

    # When I view the advance episode options
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()

    # And I advance the subject's episode for "MDT Referral Not Required"
    AdvanceSurveillanceEpisodePage(page).click_mdt_referral_not_required_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A353 MDT Referral Not Required",
        },
    )

    # And there is a "A353" letter batch for my subject with the exact title "GP Letter Indicating Referral to Symptomatic"
    # When I process the open "A353" letter batch for my subject
    batch_processing(
        page,
        "A353",
        "GP Letter Indicating Referral to Symptomatic",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A372 Refer Symptomatic, GP Letter Printed",
        },
    )

    # When I view the advance episode options
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()

    # And I select the advance episode option for "LNPCP Result from Symptomatic Procedure"
    AdvanceSurveillanceEpisodePage(
        page
    ).click_lnpcp_result_from_symptomatic_procedure_button()

    # And I set the Date of Symptomatic Procedure to "yesterday"
    LnpcpResultFromSymptomaticProcedure(page).enter_date_of_symptomatic_procedure(
        datetime.today() - timedelta(days=1)
    )

    # And the Screening Interval is 36 months
    LnpcpResultFromSymptomaticProcedure(page).assert_text_in_alert_textbox(
        "recall interval of 36 months"
    )

    # And I select test number 1
    LnpcpResultFromSymptomaticProcedure(page).select_test_number(1)

    # And I save the Result from Symptomatic Procedure
    LnpcpResultFromSymptomaticProcedure(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Latest not-void test in latest episode",
            "latest episode accumulated result": "LNPCP",
            "latest event status": "A373 Symptomatic result recorded",
            "symptomatic procedure date": "Yesterday",
            "symptomatic procedure result": "LNPCP",
        },
    )

    # When I advance the subject's episode for "Refer to Surveillance after Symptomatic Referral"
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_refer_to_surveillance_after_symptomatic_referral_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A374 Refer to Surveillance after Symptomatic Referral",
        },
    )

    # And there is a "A374" letter batch for my subject with the exact title "Return Surveillance Letter after Referral to Symptomatic"
    # When I process the open "A374" letter batch for my subject
    batch_processing(
        page,
        "A374",
        "Return Surveillance Letter after Referral to Symptomatic",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Latest not-void test in latest episode",
            "calculated fobt due date": "Unchanged",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "3 years from symptomatic procedure",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "diagnostic test has result": "No result",
            "latest episode accumulated result": "LNPCP",
            "latest episode recall calculation method": "Symptomatic Procedure date",
            "latest episode recall episode type": "Surveillance - LNPCP",
            "latest episode recall surveillance type": "LNPCP",
            "latest episode status": "Closed",
            "latest episode status reason": "Episode Complete",
            "latest event status": "A157 LNPCP",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Unchanged",
            "screening due date reason": "Unchanged",
            "screening referral type": "Null",
            "screening status": "Surveillance",
            "screening status date of change": "Unchanged",
            "screening status reason": "Unchanged",
            "surveillance due date": "Calculated Surveillance Due Date",
            "surveillance due date date of change": "Today",
            "surveillance due date reason": "Result - LNPCP",
            "symptomatic procedure date": "Yesterday",
            "symptomatic procedure result": "LNPCP",
        },
    )

    # When I switch users to BCSS "England" as user role "Hub Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(page, "Hub Manager at BCS01", True)

    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I manually cease the subject with reason "No Colon (subject request)"
    SubjectScreeningSummaryPage(page).click_request_cease_button()
    RecordRequestToCeasePage(page).cease_subject_with_reason(
        "No Colon (subject request)"
    )

    # Then my subject has been updated as follows
    subject_assertion(
        nhs_no,
        {
            "calculated fobt due date": "Unchanged",
            "calculated lynch due date": "Unchanged",
            "calculated surveillance due date": "Unchanged",
            "ceased confirmation date": "Today",
            "ceased confirmation details": "AUTO TESTING: confirm not-immediate manual cease",
            "ceased confirmation user id": "User's ID",
            "clinical reason for cease": "Null",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Unchanged",
            "screening due date reason": "Ceased",
            "screening status": "Ceased",
            "screening status date of change": "Today",
            "screening status reason": "No Colon (subject request)",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Today",
            "surveillance due date reason": "Ceased",
        },
        user_role,
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I manually uncease the subject to "send a new kit"
    SubjectScreeningSummaryPage(page).click_uncease_subject_button()
    UnceaseAndInitiateOptinEpisodePage(page).manually_uncease_the_subject(
        "send a new kit"
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "calculated fobt due date": "Unchanged",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "Unchanged",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Today",
            "screening due date date of change": "Today",
            "screening due date reason": "Opt (Back) into Screening Programme",
            "screening status": "Opt-in",
            "screening status date of change": "Today",
            "screening status reason": "Opt (Back) into Screening Programme",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Unchanged",
            "surveillance due date reason": "Null",
        },
    )

    # When Comment:
    logging.info(
        "The Surveillance episode can be reopened, taking the subject back to Surveillance status"
    )
    logging.info(
        "NB the Calculated FOBT due date is nullified during the reopen, which seems odd!"
    )

    # When I switch users to BCSS "England" as user role "Screening Centre Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(page, "Screening Centre Manager at BCS001", True)
    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I reopen the subject's episode for "Reopen to Re-record Outcome from Symptomatic Referral"
    SubjectScreeningSummaryPage(page).click_reopen_surveillance_episode_button()
    ReopenSurveillanceEpisodePage(
        page
    ).click_reopen_to_rerecord_outcome_from_symptomatic_referral_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "calculated fobt due date": "Null",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "As at episode start",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "No Result",
            "latest episode recall calculation method": "Symptomatic Procedure date",
            "latest episode recall episode type": "Null",
            "latest episode recall surveillance type": "LNPCP",
            "latest episode status": "Open",
            "latest episode status reason": "Null",
            "latest event status": "A372 Refer Symptomatic, GP Letter Printed",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Today",
            "screening due date reason": "Reopened Episode",
            "screening status": "Surveillance",
            "screening status date of change": "Today",
            "screening status reason": "Reopened Episode",
            "surveillance due date": "As at episode start",
            "surveillance due date date of change": "Today",
            "surveillance due date reason": "Reopened Episode",
        },
    )

    # When I view the advance episode options
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()

    # And I select the advance episode option for "LNPCP Result from Symptomatic Procedure"
    AdvanceSurveillanceEpisodePage(
        page
    ).click_lnpcp_result_from_symptomatic_procedure_button()

    # And I set the Date of Symptomatic Procedure to "today"
    LnpcpResultFromSymptomaticProcedure(page).enter_date_of_symptomatic_procedure(
        datetime.today()
    )

    # And the Screening Interval is 36 months
    LnpcpResultFromSymptomaticProcedure(page).assert_text_in_alert_textbox(
        "recall interval of 36 months"
    )

    # And I select test number 1
    LnpcpResultFromSymptomaticProcedure(page).select_test_number(1)

    # And I save the Result from Symptomatic Procedure
    LnpcpResultFromSymptomaticProcedure(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Latest not-void test in latest episode",
            "latest episode accumulated result": "LNPCP",
            "latest event status": "A373 Symptomatic result recorded",
            "symptomatic procedure date": "Today",
            "symptomatic procedure result": "LNPCP",
        },
    )

    # When I select the advance episode option for "Refer Another Diagnostic Test after return from Symptomatic Referral"
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_refer_another_diagnostic_test_after_return_from_symptomatic_referral_button()

    # And I select Referral Type of "Radiological" for the Diagnostic Test Referral Following Symptomatic Procedure
    # And I select Referral Type of "Radiological" for the Diagnostic Test Referral Following Symptomatic Procedure
    ReturnFromSymptomaticReferralPage(
        page
    ).select_radiological_or_endoscopic_referral_option("Radiological")

    # And I select Reason for Onward Referral of "Further Clinical Assessment" for the Diagnostic Test Referral Following Symptomatic Procedure
    ReturnFromSymptomaticReferralPage(page).select_reason_for_onward_referral_option(
        "Further Clinical Assessment"
    )

    # And I save the Diagnostic Test Referral Following Symptomatic Procedure
    ReturnFromSymptomaticReferralPage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A389 Refer Another Diagnostic Test after return from Symptomatic Referral"
        },
    )

    # When Comment:
    logging.info(
        "Temporary pathway until the Return from Symptomatic Referral - Refer Another Diagnostic Test screen is built in BCSS-16246"
    )

    # When I advance the subject's episode for "Post-investigation Appointment Required"
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_post_investigation_appointment_required_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A360 Post-investigation Appointment Required",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I choose to book a practitioner clinic for my subject
    SubjectScreeningSummaryPage(page).click_book_practitioner_clinic_button()

    # And I set the practitioner appointment date to "today"
    # And I book the earliest available post investigation appointment on this date
    book_post_investigation_appointment(page, "The Royal Hospital (Wolverhampton)")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A410 Post-investigation Appointment Made"},
    )

    # And there is a "A410" letter batch for my subject with the exact title "Post-Investigation Appointment Invitation Letter"
    # When I process the open "A410" letter batch for my subject
    batch_processing(
        page,
        "A410",
        "Post-Investigation Appointment Invitation Letter",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A415 Post-investigation Appointment Invitation Letter Printed"
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page).expand_episodes_list()
    SubjectScreeningSummaryPage(page).click_first_surveillance_episode_link()

    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # And I attend the subject's practitioner appointment "today"
    AppointmentDetailPage(page).mark_appointment_as_attended(datetime.today())

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A416 Post-investigation Appointment Attended",
        },
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A316 Post-investigation Appointment Attended",
            "latest event status": "A319 Refer follow-up test after return from symptomatic referral letter (Patient & GP)",
        },
    )

    # And there is a "A319" letter batch for my subject with the exact title "Result Letters - Refer another test after symptomatic referral"
    # When I process the open "A319" letter batch for my subject
    batch_processing(
        page,
        "A319",
        "Result Letters - Refer another test after symptomatic referral",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A395 Refer Another Diagnostic Test",
        },
    )

    LogoutPage(page).log_out()
