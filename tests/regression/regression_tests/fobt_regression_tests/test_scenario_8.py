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

    # And there is a subject who meets the following criteria:
    user_details = UserTools.retrieve_user("Hub Manager at BCS01")

    criteria = {
        Key.LATEST_EVENT_STATUS.description: "S9 Pre-invitation Sent",
        Key.LATEST_EPISODE_KIT_CLASS.description: "FIT",
        Key.LATEST_EPISODE_STARTED.description: "Within the last 6 months",
        Key.LATEST_EPISODE_TYPE.description: "FOBT",
        Key.SUBJECT_AGE.description: "Between 60 and 72",
        # Key.SUBJECT_HAS_UNPROCESSED_SSPI_UPDATES.description: "No",
        # Key.SUBJECT_HAS_USER_DOB_UPDATES.description: "No",
        # Key.SUBJECT_HUB_CODE.description: user_details["hub_code"],
    }

    nhs_no = SubjectSelector.get_subject_for_pre_invitation(criteria)
    subject_assertion(nhs_no, criteria)

    # Then Comment: NHS number
    logging.info(f"[SUBJECT FOUND] NHS number: {nhs_no}")

    # When I run Timed Events for my subject
    OracleDB().exec_bcss_timed_events(nhs_number=nhs_no)

    # Then there is a "S9" letter batch for my subject with the exact title "Invitation & Test Kit (FIT)"
    # When I process the open "S9" letter batch for my subject
    # Then my subject has been updated as follows:
    batch_processing(
        page,
        "S9",
        "Invitation & Test Kit (FIT)",
        "S10 - Invitation & Test Kit Sent",
        True,
    )

    # When I log my subject's latest unlogged FIT kit
    fit_kit = FitKitGeneration().get_fit_kit_for_subject_sql(nhs_no, False, False)
    sample_date = datetime.now()
    FitKitLogged().log_fit_kits(page, fit_kit, sample_date)

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "S43 Kit Returned and Logged (Initial Test)",
    }
    subject_assertion(nhs_no, criteria)

    # When I read my subject's latest logged FIT kit as "ABNORMAL"
    FitKitLogged().read_latest_logged_kit(user_role, 2, fit_kit, "ABNORMAL")

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A8 Abnormal",
    }
    subject_assertion(nhs_no, criteria)
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I choose to book a practitioner clinic for my subject
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
    criteria = {
        "latest event status": "A183 1st Colonoscopy Assessment Appointment Requested",
    }
    subject_assertion(nhs_no, criteria)

    # And there is a "A183" letter batch for my subject with the exact title "Practitioner Clinic 1st Appointment"
    # When I process the open "A183 - Practitioner Clinic 1st Appointment" letter batch for my subject
    # Then my subject has been updated as follows:
    batch_processing(
        page,
        "A183",
        "Practitioner Clinic 1st Appointment",
        "A25 - 1st Colonoscopy Assessment Appointment Booked, letter sent",
    )

    # And there is a "A183" letter batch for my subject with the exact title "GP Result (Abnormal)"
    batch_processing(
        page,
        "A183",
        "GP Result (Abnormal)",
        "A25 - 1st Colonoscopy Assessment Appointment Booked, letter sent",
    )

    # When I switch users to BCSS "England" as user role "Screening Centre Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(page, "Screening Centre Manager at BCS001", True)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the event history for the subject's latest episode
    # And I view the latest practitioner appointment in the subject's episode
    # And I attend the subject's practitioner appointment "yesterday"
    attendance.mark_as_attended_yesterday()

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "J10 Attended Colonoscopy Assessment Appointment",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I edit the Colonoscopy Assessment Dataset for this subject
    # And I update the Colonoscopy Assessment Dataset with the following values:
    # 	| Fit for Colonoscopy (SSP) | No  |
    # 	| Dataset complete?         | Yes |
    # And I save the Colonoscopy Assessment Dataset
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_colonoscopy_show_datasets()
    dataset.select_fit_for_colonoscopy_option(ssp_options.NO)
    dataset.click_dataset_complete_radio_button_yes()
    dataset.save_dataset()

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I advance the subject's episode for "Suitable for Radiological Test"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    advance_fobt_episode.click_suitable_for_radiological_test_button()

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A100 Suitable for Radiological Test",
    }
    subject_assertion(nhs_no, criteria)

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # When I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # And I select Diagnostic Test Type "CT Colonography"
    # And I enter a Diagnostic Test First Offered Appointment Date of "today"
    # And I advance the subject's episode for "Invite for Diagnostic Test >>"
    advance_fobt_episode.select_ct_colonography_and_invite()

    # Then my subject has been updated as follows:
    criteria = {
        "which diagnostic test": "latest test in latest episode",
        "diagnostic test proposed type": "CT Colonography",
        "latest event status": "A59 Invited for Diagnostic Test",
    }
    subject_assertion(nhs_no, criteria)

    # When the subject DNAs the diagnostic test
    attendance.mark_diagnostic_test_as_dna()

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A172 DNA Diagnostic Test",
    }
    subject_assertion(nhs_no, criteria)

    # When I switch users to BCSS "England" as user role "Hub Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    UserTools.user_login(page, "Hub Manager at BCS01")

    # # And I process the open "A183 - GP Result (Abnormal)" letter batch for my subject
    # TODO: LEAVE COMMENTED - is this needed? Subject is already at A172 DNA Diagnostic Test (line 279)
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

    # And I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # And I select the advance episode option for "Record Diagnosis Date"
    AdvanceFOBTScreeningEpisodePage(page).click_record_diagnosis_date_button()

    # And I select Diagnosis Date Reason "Patient could not be contacted"
    RecordDiagnosisDatePage(page).record_diagnosis_reason(
        reason_text="Patient could not be contacted"
    )

    # Then my subject has been updated as follows:
    criteria = {
        "latest episode diagnosis date reason": "Patient could not be contacted",
        "latest episode has diagnosis date": "No",
        "latest episode includes event status": "A52 No diagnosis date recorded",
    }
    subject_assertion(nhs_no, criteria)

    # # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

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

    # When I process the open "A391 - Discharge from screening round - no contact (letter to GP)" letter batch for my subject
    batch_processing(
        page,
        "A391",
        "Discharge from screening round - no contact (letter to GP)",
        "A351 - GP Discharge Letter Printed - No Patient Contact",
    )

    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "2 years from episode end",
        "calculated lynch due date": "Unchanged",
        "calculated surveillance due date": "Unchanged",
        "ceased confirmation date": "Null",
        "ceased confirmation details": "Null",
        "ceased confirmation user id": "Null",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "No result",
        "latest episode recall calculation method": "Episode end date",
        "latest episode recall episode type": "FOBT Screening",
        "latest episode recall surveillance type": "Null",
        "latest episode status": "Closed",
        "latest episode status reason": "Patient could not be contacted",
        "latest event status": "A351 GP Discharge Letter Printed - No Patient Contact",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "screening due date": "Calculated FOBT Due Date",
        "screening due date reason": "Recall",
        "screening due date date of change": "Today",
        # Screening status fields intentionally not checked
        "surveillance due date": "Null",
        "surveillance due date date of change": "Unchanged",
        "surveillance due date reason": "Unchanged",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # 	And I reopen the subject's episode for "Reopen to Reschedule Diagnostic Test"

    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "As at episode start",
        "calculated lynch due date": "Null",
        "calculated surveillance due date": "Null",
        "ceased confirmation date": "Null",
        "ceased confirmation details": "Null",
        "ceased confirmation user id": "Null",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "No result",
        "latest episode includes event code": "E68 Reopen to Reschedule Diagnostic Test",
        "latest episode recall calculation method": "Episode end date",
        "latest episode recall episode type": "Null",
        "latest episode recall surveillance type": "Null",
        "latest episode status": "Open",
        "latest episode status reason": "Null",
        "latest event status": "A172 DNA Diagnostic Test",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "screening due date": "Calculated FOBT due date",
        "screening due date date of change": "Today",
        "screening due date reason": "Reopened episode",
        # Screening status fields intentionally not checked
        "surveillance due date": "Null",
        "surveillance due date date of change": "Unchanged",
        "surveillance due date reason": "Unchanged",
    }
    subject_assertion(nhs_no, criteria)

    # When I select the advance episode option for "Record Contact with Patient"
    # 	And I record contact with the subject with outcome "Suitable for Radiological Test"

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A100 Suitable for Radiological Test",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # 	And I select Diagnostic Test Type "CT Colonography"
    # 	And I enter a Diagnostic Test First Offered Appointment Date of "today"
    # 	And I advance the subject's episode for "Invite for Diagnostic Test >>"

    # Then my subject has been updated as follows:
    criteria = {
        "which diagnostic test": "Latest test in latest episode",
        "diagnostic test proposed type": "CT Colonography",
        "latest event status": "A59 Invited for Diagnostic Test",
    }
    subject_assertion(nhs_no, criteria)

    # When I select the advance episode option for "Attend Diagnostic Test"
    # And I attend the subject's diagnostic test today

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A259 Attended Diagnostic Test",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I edit the Investigation Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    # 	And I open all minimized sections on the dataset
    # 	And I mark the Investigation Dataset as completed
    # 	And I set the following fields and values within the Investigation Dataset for this subject:
    # 	| Screening Site                         | (Pick first option)  |
    # 	| Practitioner                           | (Pick first option)  |
    # 	| Testing Clinician                      | (Pick first option)  |
    # 	| Reporting Radiologist                  | (Pick second option) |
    # 	| Fit for Subsequent Endoscopic Referral | Yes                  |

    # 	And I set the following fields and values within the Contrast, Tagging & Drug Information:
    # 	| IV Buscopan Administered                  | No  |
    # 	| Contraindicated                           | No  |
    # 	| IV Contrast Administered                  | No  |
    # 	| Tagging Agent Given                       | Yes |
    # 	| Additional Bowel Preparation Administered | Yes |

    # 	And I add the following "Tagging Agent Given" drugs and doses within the Investigation Dataset for this subject:
    # 	| Gastrografin | 1 |
    # 	And I add the following Additional Bowel Preparation drugs and values within the Investigation Dataset for this subject:
    # 	| Picolax | 1 |
    # 	And I set the following fields and values within the Radiology Information:
    # 	| Examination Quality          | Good                |
    # 	| Number of Scan Positions     | Dual                |
    # 	| Outcome at time of procedure | Leave department    |
    # 	| Late outcome                 | No complications    |
    # 	| Segmental Inadequacy         | No                  |
    # 	| Intracolonic Summary Code    | Cx Inadequate study |
    # 	And I set the following radiology failure reasons within the Investigation Dataset for this subject:
    # 	| No failure reasons |
    # 	And I set the following fields and values within the Radiology Information:
    # 	| Extracolonic Summary Code | E4 Potentially important new finding, requires further action |
    # 	And I press the save Investigation Dataset button
    # Then the Investigation Dataset result message, which I will cancel, is "Abnormal"

    # When I press the save Investigation Dataset button
    # 	And I press OK on my confirmation prompt

    # Then my subject has been updated as follows:
    criteria = {
        "latest episode accumulated result": "Abnormal",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # 	And I select the advance episode option for "Enter Diagnostic Test Outcome"
    # 	And I select Outcome of Diagnostic Test "Refer Another Diagnostic Test"
    # 	And I select Radiological or Endoscopic Referral value "Radiological"
    # 	And I select Reason for Onward Referral value "Currently Unsuitable for Endoscopic Referral"
    # 	And I set any onward referring clinician
    # 	And I save the Diagnostic Test Outcome

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A315 Diagnostic Test Outcome Entered",
    }
    subject_assertion(nhs_no, criteria)

    # When I advance the subject's episode for "Post-investigation Appointment Required"

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A360 Post-investigation Appointment Required",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # 	And I choose to book a practitioner clinic for my subject
    # 	And I set the practitioner appointment date to "today"
    # 	And I book the earliest available post investigation appointment on this date

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A410 Post-investigation Appointment Made",
    }
    subject_assertion(nhs_no, criteria)

    # And there is a "A410" letter batch for my subject with the exact title "Post-Investigation Appointment Invitation Letter"
    # When I process the open "A410" letter batch for my subject
    # Then my subject has been updated as follows:
    # 	| Latest event status | A415 Post-investigation Appointment Invitation Letter Printed |
    batch_processing(
        page,
        "A410",
        "Post-Investigation Appointment Invitation Letter",
        "A415 - Post-investigation Appointment Invitation Letter Printed",
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # 	And I view the event history for the subject's latest episode
    # 	And I view the latest practitioner appointment in the subject's episode
    # 	And I attend the subject's practitioner appointment "today"

    # Then my subject has been updated as follows:
    # 	| Latest episode includes event status | A416 Post-investigation Appointment Attended |
    # 	And my subject has been updated as follows:
    # 	| Latest episode includes event status | A316 Post-investigation Appointment Attended                                        |
    # 	| Latest event status                  | A430 Post-investigation Appointment Attended - Diagnostic Result Letter not Printed |

    # And there is a "A430" letter batch for my subject with the exact title "Result Letters Following Post-investigation Appointment"
    # When I process the open "A430" letter batch for my subject
    # Then my subject has been updated as follows:
    # 	| Latest event status | A395 Refer Another Diagnostic Test |
    batch_processing(
        page,
        "A430",
        "Result Letters Following Post-investigation Appointment",
        "A395 - Refer Another Diagnostic Test",
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # And I interrupt the subject's episode for "Redirect to DELETE the Latest Diagnostic Test Result"
    # Then I get a confirmation prompt that "contains" "WARNING - This redirect will DELETE the following datasets if they exist:"
    # And my confirmation prompt "contains" "Investigation"
    # And my confirmation prompt "contains" "MDT"
    # And my confirmation prompt "contains" "Cancer Audit"
    # When I press OK on my confirmation prompt

    # Then my subject has been updated as follows:
    criteria = {
        "latest episode includes event code": "E27 Redirect to DELETE the Latest Diagnostic Test Result",
        "latest event status": "A100 Suitable for Radiological Test",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # 	And I interrupt the subject's episode for "Redirect to re-establish suitability for diagnostic test re:patient contact"

    # Then my subject has been updated as follows:
    criteria = {
        "latest episode includes event code": "E349 Redirect to re-establish suitability for diagnostic test re:patient contact",
        "latest event status": "A172 DNA Diagnostic Test",
    }
    subject_assertion(nhs_no, criteria)

    # When I select the advance episode option for "Record Contact with Patient"
    # 	And I record contact with the subject with outcome "Suitable for Endoscopic Test"

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A99 Suitable for Endoscopic Test",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # 	And I select Diagnostic Test Type "Colonoscopy"
    # 	And I enter a Diagnostic Test First Offered Appointment Date of "today"
    # 	And I advance the subject's episode for "Invite for Diagnostic Test >>"

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A59 Invited for Diagnostic Test",
    }
    subject_assertion(nhs_no, criteria)

    # When I select the advance episode option for "Attend Diagnostic Test"
    # 	And I attend the subject's diagnostic test today

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A259 Attended Diagnostic Test",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # 	And I edit the Investigation Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    # 	And I open all minimized sections on the dataset
    # 	And I mark the Investigation Dataset as completed
    # 	And I add the following bowel preparation drugs and values within the Investigation Dataset for this subject:
    # 	| Mannitol | 3 |
    # 	And I set the following fields and values within the Investigation Dataset for this subject:
    # 	| Screening Site               | (Pick first option) |
    # 	| Practitioner                 | (Pick first option) |
    # 	| Testing Clinician            | (Pick first option) |
    # 	| Aspirant Endoscopist         | Not Present         |
    # 	| Endoscope inserted           | Yes                 |
    # 	| Procedure type               | Diagnostic          |
    # 	| Bowel preparation quality    | Good                |
    # 	| Comfort during examination   | No discomfort       |
    # 	| Comfort during recovery      | No discomfort       |
    # 	| Endoscopist defined extent   | Descending Colon    |
    # 	| Scope imager used            | Yes                 |
    # 	| Retroverted view             | No                  |
    # 	| Start of intubation time     | 09:00               |
    # 	| Start of extubation time     | 09:30               |
    # 	| End time of procedure        | 10:00               |
    # 	| Scope ID                     | Autotest            |
    # 	| Insufflation                 | Air                 |
    # 	| Outcome at time of procedure | Leave department    |
    # 	| Late outcome                 | No complications    |
    # 	And I set the following failure reasons within the Investigation Dataset for this subject:
    # 	| Pain |
    # 	And I press the save Investigation Dataset button
    # Then the Investigation Dataset result message, which I will cancel, is "No Result"

    # When I press the save Investigation Dataset button
    # 	And I press OK on my confirmation prompt

    # Then my subject has been updated as follows:
    criteria = {
        "latest episode accumulated result": "No result",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # 	And I select the advance episode option for "Enter Diagnostic Test Outcome"
    # 	And I select Outcome of Diagnostic Test "Failed Test - Refer Another"
    # 	And I save the Diagnostic Test Outcome

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A315 Diagnostic Test Outcome Entered",
    }
    subject_assertion(nhs_no, criteria)

    # When I advance the subject's episode for "Other Post-investigation Contact Required"

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A361 Other Post-investigation Contact Required",
    }
    subject_assertion(nhs_no, criteria)

    # When I select the advance episode option for "Record other post-investigation contact"
    # 	And I record contact with the subject with outcome "Post-investigation Appointment Not Required"

    # Then my subject has been updated as follows:
    # 	| Latest episode includes event status | A323 Post-investigation Appointment NOT Required |
    # Then my subject has been updated as follows:
    # 	| Latest episode includes event status | A317 Post-investigation Contact Made                                     |
    # 	| Latest event status                  | A318 Post-investigation Appointment NOT Required - Result Letter Created |
    # 	And there is a "A318" letter batch for my subject with the exact title "Result Letters - No Post-investigation Appointment"

    # When I process the open "A318" letter batch for my subject
    # Then my subject has been updated as follows:
    # 	| Latest event status | A380 Failed Diagnostic Test - Refer Another |

    # When I select the advance episode option for "Record Contact with Patient"
    # 	And I record contact with the subject with outcome "Close Episode - No Contact"

    # Then my subject has been updated as follows:
    criteria = {
        "latest event status": "A397 Discharged  from Screening Round - No Patient Contact",
    }
    subject_assertion(nhs_no, criteria)

    # And there is a "A397" letter batch for my subject with the exact title "Discharge from screening round - no contact (letter to patient)"
    # When I process the open "A397" letter batch for my subject
    # Then my subject has been updated as follows:
    # 	| Latest event status | A391 Patient Discharge Letter Printed - No Patient Contact |
    # And there is a "A391" letter batch for my subject with the exact title "Discharge from screening round - no contact (letter to GP)"

    # When I receive an SSPI update to change their date of birth to "73" years old

    # Then my subject has been updated as follows:
    criteria = {
        "subject age": "73",
    }
    subject_assertion(nhs_no, criteria)

    # When I process the open "A391 - Discharge from screening round - no contact (letter to GP)" letter batch for my subject
    batch_processing(
        page,
        "A391",
        "Discharge from screening round - no contact (letter to GP)",
        "A351 - GP Discharge Letter Printed - No Patient Contact",
    )

    # Then my subject has been updated as follows:
    criteria = {
        "calculated FOBT due date": "2 years from episode end",
        "calculated Lynch due date": "Unchanged",
        "calculated Surveillance due date": "Unchanged",
        "ceased confirmation date": "Today",
        "ceased confirmation details": "Outside screening population at recall.",
        "ceased confirmation user ID": "User's ID",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "No result",
        "latest episode recall calculation method": "Episode end date",
        "latest episode recall episode type": "FOBT Screening",
        "latest episode recall surveillance type": "Null",
        "latest episode status": "Closed",
        "latest episode status reason": "Patient could not be contacted",
        "latest event status": "A351 GP Discharge Letter Printed - No Patient Contact",
        "Lynch due date": "Null",
        "Lynch due date date of change": "Unchanged",
        "Lynch due date reason": "Unchanged",
        "screening Due Date": "Null",
        "screening Due Date Reason": "Ceased",
        "screening Due Date Date of change": "Today",
        "screening Status": "Ceased",
        "screening Status date of change": "Today",
        "screening Status reason": "Outside Screening Population",
        "surveillance Due Date": "Null",
        "surveillance due date date of change": "Unchanged",
        "surveillance due date reason": "Unchanged",
    }
    subject_assertion(nhs_no, criteria)
