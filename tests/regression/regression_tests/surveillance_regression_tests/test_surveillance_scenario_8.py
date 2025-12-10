import pytest
from playwright.sync_api import Page
from classes.repositories.subject_repository import SubjectRepository
from pages.organisations.organisations_page import OrganisationSwitchPage
from pages.screening_subject_search.lnpcp_result_from_symptomatic_procedure_page import (
    LnpcpResultFromSymptomaticProcedure,
)
from pages.screening_subject_search.refer_to_mdt_page import ReferToMDTPage
from pages.screening_subject_search.reopen_episode_page import ReopenEpisodePage
from pages.screening_subject_search.reopen_surveillance_episode_page import (
    ReopenSurveillanceEpisodePage,
)
from utils.generate_health_check_forms_util import GenerateHealthCheckFormsUtil
from utils.sspi_change_steps import SSPIChangeSteps
from utils.user_tools import UserTools
from utils.subject_assertion import subject_assertion
import logging
from utils.batch_processing import batch_processing
from pages.logout.log_out_page import LogoutPage
from utils import screening_subject_page_searcher
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.screening_subject_search.advance_surveillance_episode_page import (
    AdvanceSurveillanceEpisodePage,
)
from pages.screening_subject_search.contact_with_patient_page import (
    ContactWithPatientPage,
)
from classes.user.user import User
from classes.subject.subject import Subject
from utils.oracle.oracle import OracleDB
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from datetime import datetime, timedelta
from utils.calendar_picker import CalendarPicker
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.datasets.colonoscopy_dataset_page import (
    ColonoscopyDatasetsPage,
    FitForColonoscopySspOptions,
)
from pages.screening_subject_search.attend_diagnostic_test_page import (
    AttendDiagnosticTestPage,
)
from pages.datasets.investigation_dataset_page import (
    FailureReasonsOptions,
    DrugTypeOptions,
    BowelPreparationQualityOptions,
    ComfortOptions,
    EndoscopyLocationOptions,
    InsufflationOptions,
    InvestigationDatasetsPage,
    LateOutcomeOptions,
    OutcomeAtTimeOfProcedureOptions,
    YesNoOptions,
    EndoscopyLocationOptions,
)
from classes.repositories.person_repository import PersonRepository
from utils.investigation_dataset import InvestigationDatasetCompletion
from pages.screening_subject_search.diagnostic_test_outcome_page import (
    DiagnosticTestOutcomePage,
    OutcomeOfDiagnosticTest,
    ReasonForSymptomaticReferral,
)


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.surveillance_regression_tests
def test_scenario_8(page: Page, general_properties: dict) -> None:
    """
    Scenario: 8:SSPI cease

    X500-X505-X92-C203 [SSCL30e] [SSUN7] X900-A99-A59-A259-X92-C203 [SSCL30e] [SSUN5] X900-A99-A59-A259-A315-A361-A323-A317-A348-A372-A373-A374-X92-C203 [SSCL30c] [SSUN6] X900

    This scenario tests closure of a Surveillance episode, at various points, as a result of an SSPI cease.  Reopening a Surveillance episode from closure on X92 always reopens to X900, which is suitable for reopening after a postpone, but seems less suitable for reopening after the closure occurred later in the episode, as a result of an SSPI cease.

    The cease/uncease rules for Surveillance are old and possibly due for an overhaul – and alas the reasoning behind them has been long since lost in the mists of time.

    The first cease (before the subject has attended a diagnostic test) closes the episode for death: on uncease the surveillance due date and reason for change are not changed but left as null and "Ceased".  Presumably this is to allow user to investigate and possibly reopen the episode.  This uncease is done by re-registering the subject with a GP practice.

    The second cease (after the subject has attended a diagnostic test, but the episode result is none of Cancer, LNPCP or High-risk findings) closes the episode for embarkation: on uncease the due date is set to the previous surveillance due date (rather than the calculated surveillance due date, which is also a little odd), and the reason set to "Reinstate surveillance".  The actual value of the due date is too difficult to check, because the previous surveillance due date field is nullified at the same time.  This uncease is done by changing the subject’s deduction code to one of the "not cease" codes.

    <i>At this point the subject has a diagnostic test with a result and a completed investigation dataset, but no outcome, and there is no Advance Episode option (or even an interrupt) to add one.  For the purposes of this scenario, the subject is invited for another test.</i>

    The third cease occurs when the episode has a result of High-risk findings.  This is another embarkation cease, and the uncease is done by reopening the episode.  Because the reopen also unceases the subject, the recall surveillance type is nullified.  Reopening a surveillance episode nullifies the calculated FOBT due date, and the FOBT due date change date and reason for change.

    <i>Once again, there are only limited options on reopen, and it is impossible to redirect the episode to re-enter the symptomatic result.  This means the episode result cannot be “downgraded” at all.</i>

    Scenario summary:

    > Run surveillance invitations for 1 subject > X500 (3.1)
    > SSPI update changes subject to in-age at recall
    > Process X500 letter batch > X505 (3.1)
    > SSPI update ceases subject for death > X92 > C203 (3.1)
    > Check recall [SSCL30e]
    > SSPI update unceases subject - re-registered with a GP [SSUN7]
    > Reopen episode for correction > X900 (3.1)
    > Suitable for colonoscopy > A99 (3.1)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset, result = No result (2.1)
    > SSPI update ceases subject for embarkation > X92 > C203 (3.1)
    > Check recall [SSCL30e]
    > SSPI update unceases subject - change to non-cease deduction [SSUN5]
    > Reopen episode for patient decision > X900 (3.1)
    > Complete the colonoscopy assessment dataset - fit for colonoscopy
    > Suitable for colonoscopy > A99 (3.1)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset, result = No result (2.1)
    > Enter diagnostic test outcome – failed test, refer another > A315 (2.1)
    > Post-investigation appointment not required > A361 (2.1)
    > Record patient contact – post-investigation appointment not required > A323 (2.1) > A317 (2.5)
    > MDT required - record MDT > A348 (2.6)
    > Process A348 letter batch > A372 (2.6)
    > Record symptomatic result – High-risk findings > A373 (2.7)
    > Refer surveillance > A374 (2.7)
    > SSPI update ceases subject for embarkation > X92 > C203 (3.1)
    > Check recall [SSCL30c]
    > Reopen episode for correction > X900 (3.1) [SSUN6]
    """

    # Given I log in to BCSS "England" as user role "Specialist Screening Practitioner"
    user_role = UserTools.user_login(
        page, "Specialist Screening Practitioner at BCS009 & BCS001", True
    )

    OrganisationSwitchPage(page).select_organisation_by_id("BCS001")
    OrganisationSwitchPage(page).click_continue()
    if user_role is None:
        raise ValueError("User role is none")

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

    # When I receive an SSPI update to change their date of birth to "62" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 62)

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"subject age": "62"})

    # And there is a "X500" letter batch for my subject with the exact title "Surveillance Selection"
    # When I process the open "X500" letter batch for my subject
    batch_processing(
        page,
        "X500",
        "Surveillance Selection",
    )

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"latest event status": "X505 HealthCheck Form Printed"})

    # When I process an SSPI update for deduction reason "Death"
    SSPIChangeSteps().process_sspi_deduction_by_description(nhs_no, "Death")

    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "Unchanged",
        "calculated lynch due date": "Null",
        "calculated surveillance due date": "3 years from episode end",
        "ceased confirmation date": "Today",
        "ceased confirmation details": "SSPI deduction for death received.",
        "ceased confirmation user id": "Automated process ID",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "(Any) Surveillance non-participation",
        "latest episode recall calculation method": "X92 Interrupt User Date",
        "latest episode recall episode type": "Surveillance - High-risk findings",
        "latest episode recall surveillance type": "High-risk findings",
        "latest episode status": "Closed",
        "latest episode status reason": "Deceased",
        "latest event status": "X92 Close Surveillance Episode via interrupt",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "pre-interrupt event status": "X505 HealthCheck Form Printed",
        "screening due date": "Null",
        "screening due date date of change": "Unchanged",
        "screening due date reason": "Ceased",
        "screening status": "Ceased",
        "screening status date of change": "Today",
        "screening status reason": "Deceased",
        "surveillance due date": "Null",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "Ceased",
    }
    subject_assertion(nhs_no, criteria)

    # When I process an SSPI update to re-register my subject with their latest GP practice
    SSPIChangeSteps().reregister_subject_with_latest_gp_practice(nhs_no)

    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "Unchanged",
        "calculated lynch due date": "Null",
        "calculated surveillance due date": "3 years from episode end",
        "ceased confirmation date": "Null",
        "ceased confirmation details": "Null",
        "ceased confirmation user id": "Null",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "(Any) Surveillance non-participation",
        "latest episode recall calculation method": "X92 Interrupt User Date",
        "latest episode recall episode type": "Surveillance - High-risk findings",
        "latest episode recall surveillance type": "High-risk findings",
        "latest episode status": "Closed",
        "latest episode status reason": "Deceased",
        "latest event status": "X92 Close Surveillance Episode via interrupt",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "pre-interrupt event status": "X505 HealthCheck Form Printed",
        "screening due date": "Null",
        "screening due date date of change": "Unchanged",
        "screening due date reason": "Ceased",
        "screening status": "Surveillance",
        "screening status date of change": "Today",
        "screening status reason": "Reinstate Surveillance for Reversal of Death Notification",
        "surveillance due date": "Null",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "Ceased",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I reopen the subject's episode for "Reopen episode for correction"
    SubjectScreeningSummaryPage(page).click_reopen_surveillance_episode_button()
    ReopenSurveillanceEpisodePage(page).click_reopen_episode_for_correction_button()

    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "Null",
        "calculated lynch due date": "Null",
        "calculated surveillance due date": "As at episode start",
        "ceased confirmation date": "Null",
        "ceased confirmation details": "Null",
        "ceased confirmation user id": "Null",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "Null",
        "latest episode includes event code": "E63 Reopen episode for correction",
        "latest episode recall calculation method": "X92 Interrupt User Date",
        "latest episode recall episode type": "Null",
        "latest episode recall surveillance type": "High-risk findings",
        "latest episode status": "Open",
        "latest episode status reason": "Null",
        "latest event status": "X900 Surveillance Episode reopened",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "screening due date": "Null",
        "screening due date date of change": "Unchanged",
        "screening due date reason": "Unchanged",
        "screening status": "Surveillance",
        "screening status date of change": "Unchanged",
        "screening status reason": "Unchanged",
        "surveillance due date": "Calculated surveillance due date",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "Reopened episode",
    }
    subject_assertion(nhs_no, criteria)

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
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_suitable_for_endoscopic_test_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A99 Suitable for Endoscopic Test",
        },
    )

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
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # When I select the advance episode option for "Attend Diagnostic Test"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
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

    # And I add the following bowel preparation drugs and values within the Investigation Dataset for this subject:
    drug_information = {
        "drug_dose1": "3",
        "drug_type1": DrugTypeOptions.MANNITOL,
    }

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
    logging.info(f"Final query: {query}")
    df = OracleDB().execute_query(query)
    person_name = (
        f"{df["person_family_name"].iloc[0]} {df["person_given_name"].iloc[0]}"
    )

    # And I set the following fields and values within the Investigation Dataset for this subject:
    general_information = {
        "practitioner": 1,
        "site": 1,
        "testing clinician": person_name,
        "aspirant endoscopist": None,
    }

    endoscopy_information = {
        "endoscope inserted": "yes",
        "procedure type": "diagnostic",
        "bowel preparation quality": BowelPreparationQualityOptions.GOOD,
        "comfort during recovery": ComfortOptions.NO_DISCOMFORT,
        "comfort during examination": ComfortOptions.NO_DISCOMFORT,
        "endoscopist defined extent": EndoscopyLocationOptions.DESCENDING_COLON,
        "scope imager used": YesNoOptions.YES,
        "retroverted view": YesNoOptions.NO,
        "start of intubation time": "09:00",
        "start of extubation time": "09:30",
        "end time of procedure": "10:00",
        "scope id": "Autotest",
        "insufflation": InsufflationOptions.AIR,
        "outcome at time of procedure": OutcomeAtTimeOfProcedureOptions.LEAVE_DEPARTMENT,
        "late outcome": LateOutcomeOptions.NO_COMPLICATIONS,
    }

    # And I set the following failure reasons within the Investigation Dataset for this subject:
    failure_information = {"failure reasons": FailureReasonsOptions.PAIN}

    # And I open all minimized sections on the dataset
    # And I mark the Investigation Dataset as completed
    # When I press the save Investigation Dataset button
    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        endoscopy_information=endoscopy_information,
        drug_information=drug_information,
        general_information=general_information,
        failure_information=failure_information,
    )

    # Then the Investigation Dataset result message is "No Result"
    InvestigationDatasetsPage(page).expect_text_to_be_visible("No Result")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"Latest episode accumulated result": "No Result"},
    )

    # When I process an SSPI update for deduction reason "Embarkation"
    SSPIChangeSteps().process_sspi_deduction_by_description(nhs_no, "Embarkation")

    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "Unchanged",
        "calculated lynch due date": "Null",
        "calculated surveillance due date": "3 years from episode end",
        "ceased confirmation date": "Today",
        "ceased confirmation details": "SSPI deduction for emigration received.",
        "ceased confirmation user id": "Automated process ID",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "No result",
        "latest episode recall calculation method": "X92 Interrupt User Date",
        "latest episode recall episode type": "Surveillance - High-risk findings",
        "latest episode recall surveillance type": "High-risk findings",
        "latest episode status": "Closed",
        "latest episode status reason": "Individual has left the country",
        "latest event status": "X92 Close Surveillance Episode via interrupt",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "pre-interrupt event status": "A259 Attended Diagnostic Test",
        "screening due date": "Null",
        "screening due date date of change": "Unchanged",
        "screening due date reason": "Ceased",
        "screening status": "Ceased",
        "screening status date of change": "Today",
        "screening status reason": "Individual has left the country",
        "surveillance due date": "Null",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "Ceased",
    }
    subject_assertion(nhs_no, criteria)

    # When I process an SSPI update for deduction code "ORR"
    SSPIChangeSteps().process_sspi_deduction_by_code(nhs_no, "ORR")

    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "Unchanged",
        "calculated lynch due date": "Null",
        "calculated surveillance due date": "3 years from episode end",
        "ceased confirmation date": "Null",
        "ceased confirmation details": "Null",
        "ceased confirmation user id": "Null",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "No result",
        "latest episode recall calculation method": "X92 Interrupt User Date",
        "latest episode recall episode type": "Surveillance - High-risk findings",
        "latest episode recall surveillance type": "High-risk findings",
        "latest episode status": "Closed",
        "latest episode status reason": "Individual has left the country",
        "latest event status": "X92 Close Surveillance Episode via interrupt",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "pre-interrupt event status": "A259 Attended Diagnostic Test",
        "screening due date": "Null",
        "screening due date date of change": "Unchanged",
        "screening due date reason": "Unchanged",
        "screening status": "Surveillance",
        "screening status date of change": "Today",
        "screening status reason": "Reinstate Surveillance",
        "surveillance due date": "Not null",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "Reinstate Surveillance",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I reopen the subject's episode for "Reopen due to subject or patient decision"
    SubjectScreeningSummaryPage(page).click_reopen_surveillance_episode_button()
    ReopenEpisodePage(page).click_reopen_due_to_subject_or_patient_decision()

    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "Null",
        "calculated lynch due date": "Null",
        "calculated surveillance due date": "As at episode start",
        "ceased confirmation date": "Null",
        "ceased confirmation details": "Null",
        "ceased confirmation user id": "Null",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "No result",
        "latest episode includes event code": "E72 Reopen due to subject or patient decision",
        "latest episode recall calculation method": "X92 Interrupt User Date",
        "latest episode recall episode type": "Null",
        "latest episode recall surveillance type": "High-risk findings",
        "latest episode status": "Open",
        "latest episode status reason": "Null",
        "latest event status": "X900 Surveillance Episode reopened",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "screening due date": "Null",
        "screening due date date of change": "Unchanged",
        "screening due date reason": "Unchanged",
        "screening status": "Surveillance",
        "screening status date of change": "Unchanged",
        "screening status reason": "Unchanged",
        "surveillance due date": "Calculated surveillance due date",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "# Not checking - probably hasn't changed",
    }
    subject_assertion(nhs_no, criteria)
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I advance the subject's episode for "Suitable for Endoscopic Test"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_suitable_for_endoscopic_test_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A99 Suitable for Endoscopic Test"},
    )

    # And I select Diagnostic Test Type "Colonoscopy"
    AdvanceSurveillanceEpisodePage(page).select_test_type_dropdown_option("Colonoscopy")
    # And I enter a Diagnostic Test First Offered Appointment Date of "today"
    AdvanceSurveillanceEpisodePage(page).click_calendar_button()
    CalendarPicker(page).v1_calender_picker(datetime.today())
    # And I advance the subject's episode for "Invite for Diagnostic Test >>"
    AdvanceSurveillanceEpisodePage(page).click_invite_for_diagnostic_test_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A59 Invited for Diagnostic Test"},
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
    # And I add the following bowel preparation drugs and values within the Investigation Dataset for this subject
    drug_information = {
        "drug_dose1": "3",
        "drug_type1": DrugTypeOptions.MANNITOL,
    }
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
    logging.info(f"Final query: {query}")
    df = OracleDB().execute_query(query)
    person_name = (
        f"{df['person_family_name'].iloc[0]} {df['person_given_name'].iloc[0]}"
    )
    # And I set the following fields and values within the Investigation Dataset for this subject:
    general_information = {
        "practitioner": 1,
        "site": 1,
        "testing clinician": person_name,
        "aspirant endoscopist": None,
    }
    endoscopy_information = {
        "endoscope inserted": "yes",
        "procedure type": "diagnostic",
        "bowel preparation quality": BowelPreparationQualityOptions.GOOD,
        "comfort during recovery": ComfortOptions.NO_DISCOMFORT,
        "comfort during examination": ComfortOptions.NO_DISCOMFORT,
        "endoscopist defined extent": EndoscopyLocationOptions.DESCENDING_COLON,
        "scope imager used": YesNoOptions.YES,
        "retroverted view": YesNoOptions.NO,
        "start of intubation time": "09:00",
        "start of extubation time": "09:30",
        "end time of procedure": "10:00",
        "scope id": "Autotest",
        "insufflation": InsufflationOptions.AIR,
        "outcome at time of procedure": OutcomeAtTimeOfProcedureOptions.LEAVE_DEPARTMENT,
        "late outcome": LateOutcomeOptions.NO_COMPLICATIONS,
    }
    # And I set the following failure reasons within the Investigation Dataset for this subject:
    failure_information = {"failure reasons": FailureReasonsOptions.PAIN}
    # And I open all minimized sections on the dataset
    # And I mark the Investigation Dataset as completed
    # When I press the save Investigation Dataset button
    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        endoscopy_information=endoscopy_information,
        drug_information=drug_information,
        general_information=general_information,
        failure_information=failure_information,
    )
    # Then the Investigation Dataset result message is "No Result"
    InvestigationDatasetsPage(page).expect_text_to_be_visible("No Result")
    # Then my subject has been updated as follows:

    subject_assertion(
        nhs_no,
        {"Latest episode accumulated result": "No Result"},
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Enter Diagnostic Test Outcome"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_enter_diagnostic_test_outcome_button()

    # And I select Outcome of Diagnostic Test "Refer Symptomatic"
    DiagnosticTestOutcomePage(page).select_test_outcome_option(
        OutcomeOfDiagnosticTest.REFER_SYMPTOMATIC
    )
    # And I select Reason for Symptomatic Referral value "Suspected Cancer Surgery"
    DiagnosticTestOutcomePage(page).select_reason_for_symptomatic_referral_option(
        ReasonForSymptomaticReferral.SUSPECTED_CANCER_SURGERY
    )

    # And I save the Diagnostic Test Outcome
    DiagnosticTestOutcomePage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A315 Diagnostic Test Outcome Entered"},
    )

    # When I select the advance episode option for "Record other post-investigation contact"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_other_post_investigation_contact_required_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A361 Other Post-investigation Contact Required"},
    )

    # When I select the advance episode option for "Record other post-investigation contact"
    AdvanceSurveillanceEpisodePage(
        page
    ).click_record_other_post_investigation_contact_button()

    # And I record contact with the subject with outcome "Post-investigation Appointment Not Required"
    ContactWithPatientPage(page).record_post_investigation_appointment_not_required()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A323 Post-investigation Appointment NOT Required",
            "latest event status": "A317 Post-investigation Contact Made ",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # When I select the advance episode option for "MDT Referral Required"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_mdt_referral_required_button()
    # And I enter simple MDT information
    ReferToMDTPage(page).enter_date_in_mdt_discussion_date_field(datetime.today())
    ReferToMDTPage(page).select_mdt_location_lookup(1)
    ReferToMDTPage(page).click_record_mdt_appointment_button()
    page.wait_for_timeout(500)  # Timeout to allow subject to update in the DB.
    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A348 Referred to MDT"},
    )

    # And there is a "A348" letter batch for my subject with the exact title "GP Letter Indicating Referral to MDT"
    # When I process the open "A348" letter batch for my subject
    batch_processing(
        page,
        "A348",
        "GP Letter Indicating Referral to MDT",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A372 Refer Symptomatic, GP Letter Printed",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()

    # And I select the advance episode option for "High-risk findings Result from Symptomatic Procedure"-recheck tomorrow
    AdvanceSurveillanceEpisodePage(
        page
    ).click_high_risk_findings_result_from_symptomatic_procedure_button()

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
    criteria = {
        "which diagnostic test": "Latest not-void test in latest episode",
        "latest episode accumulated result": "High-risk findings",
        "latest event status": "A373 Symptomatic result recorded",
        "symptomatic procedure date": "Yesterday",
        "symptomatic procedure result": "High-risk findings",
    }
    subject_assertion(nhs_no, criteria)

    # When I advance the subject's episode for "Refer to Surveillance after Symptomatic Referral"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_refer_to_surveillance_after_symptomatic_referral_button()

    # Then my subject has been updated as follows
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A374 Referred to Surveillance after Symptomatic Referral"
        },
    )

    # And there is a "A374" letter batch for my subject with the exact title "Return Surveillance Letter after Referral to Symptomatic"
    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no,
        "A374",
        "Return Surveillance Letter after Referral to Symptomatic",
        True,
    )

    # When I process an SSPI update for deduction reason "Embarkation"
    SSPIChangeSteps().process_sspi_deduction_by_description(nhs_no, "Embarkation")

    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "Unchanged",
        "calculated lynch due date": "Null",
        "calculated surveillance due date": "3 years from episode end",
        "ceased confirmation date": "Today",
        "ceased confirmation details": "SSPI deduction for emigration received.",
        "ceased confirmation user id": "Automated process ID",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "High-risk findings",
        "latest episode recall calculation method": "X92 Interrupt User Date",
        "latest episode recall episode type": "Surveillance - High-risk findings",
        "latest episode recall surveillance type": "High-risk findings",
        "latest episode status": "Closed",
        "latest episode status reason": "Individual has left the country",
        "latest event status": "X92 Close Surveillance Episode via interrupt",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "pre-interrupt event status": "A374 Refer to Surveillance after Symptomatic Referral",
        "screening due date": "Null",
        "screening due date date of change": "Unchanged",
        "screening due date reason": "Ceased",
        "screening status": "Ceased",
        "screening status date of change": "Today",
        "screening status reason": "Individual has left the country",
        "surveillance due date": "Null",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "Ceased",
    }
    subject_assertion(nhs_no, criteria)
    # And there is no "A374" letter batch for my subject with the exact title "Return Surveillance Letter after Referral to Symptomatic"
    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no,
        "A374",
        "Return Surveillance Letter after Referral to Symptomatic",
        False,
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I reopen the subject's episode for "Reopen episode for correction"
    SubjectScreeningSummaryPage(page).click_reopen_surveillance_episode_button()
    ReopenEpisodePage(page).click_reopen_episode_for_correction_button()

    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "Null",
        "calculated lynch due date": "Null",
        "calculated surveillance due date": "As at episode start",
        "ceased confirmation date": "Null",
        "ceased confirmation details": "Null",
        "ceased confirmation user id": "Null",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "High-risk findings",
        "latest episode includes event code": "E63 Reopen episode for correction",
        "latest episode recall calculation method": "X92 Interrupt User Date",
        "latest episode recall episode type": "Null",
        "latest episode recall surveillance type": "Null",
        "latest episode status": "Open",
        "latest episode status reason": "Null",
        "latest event status": "X900 Surveillance Episode reopened",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "screening due date": "Null",
        "screening due date date of change": "Null",
        "screening due date reason": "Null",
        "screening status": "Surveillance",
        "screening status date of change": "Today",
        "screening status reason": "Reopened Episode",
        "surveillance due date": "Calculated surveillance due date",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "Reopened episode",
    }
    subject_assertion(nhs_no, criteria)

    LogoutPage(page).log_out()
