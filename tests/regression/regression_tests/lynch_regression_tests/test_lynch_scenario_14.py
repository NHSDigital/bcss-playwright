import logging
import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page
from classes.repositories.episode_repository import EpisodeRepository
from classes.repositories.general_repository import GeneralRepository
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
from pages.screening_practitioner_appointments.appointment_detail_page import (
    AppointmentDetailPage,
)
from pages.screening_subject_search.advance_lynch_surveillance_episode_page import (
    AdvanceLynchSurveillanceEpisodePage,
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
    ReasonForSymptomaticReferral,
)
from pages.screening_subject_search.episode_events_and_notes_page import (
    EpisodeEventsAndNotesPage,
)
from pages.screening_subject_search.non_neoplastic_result_from_symptomatic_procedure_page import (
    NonNeoplasticResultFromSymptomaticProcedurePage,
)
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.screening_subject_search.refer_to_mdt_page import ReferToMDTPage
from utils import screening_subject_page_searcher
from utils.appointments import book_appointments
from utils.batch_processing import batch_processing
from utils.calendar_picker import CalendarPicker
from utils.investigation_dataset import InvestigationDatasetCompletion
from utils.lynch_utils import LynchUtils
from utils.oracle.oracle import OracleDB
from utils.sspi_change_steps import SSPIChangeSteps
from utils.subject_assertion import subject_assertion
from utils.user_tools import UserTools


@pytest.mark.usefixtures("setup_org_and_appointments")
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.lynch_regression_tests
def test_lynch_scenario_14(page: Page) -> None:
    """
    Scenario: 14 - Abnormal result from symptomatic procedure

    G1-G2-G3-A183-A25-J10-A99-A59-A259-A315-A361-A323-A317-A348-A372-A373-A377-A65-Lynch in age [SSCL10g]

    This scenario tests progression of an FOBT episode to closure on A65 Abnormal from symptomatic procedure result, and checks that following referral for symptomatic procedure the "lowest" result possible is Abnormal, even if diagnostic test results were "No result" and the symptomatic procedure result is non-neoplastic.

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
    > Attend test > A259 (2.1)
    > Diagnostic Test Outcome Entered (Refer to Symptomatic) > A315 (2.1)
    > Other Post-investigation Contact Required > A361 (2.1)
    > Post-investigation Appointment Not Required > A317 (2.1)
    > MDT Referral Required > A348 (2.6)
    > Process A348 letter batch > A372 (2.6)
    > Symptomatic procedure of non-neoplastic > A373 (2.7)
    > Refer Lynch > A377 (2.7)
    > Check recall [SSCL10g]
    """
    # Given I log in to BCSS "England" as user role "Hub Manager"
    user_role = UserTools.user_login(
        page, "Hub Manager State Registered at BCS01", return_role_type=True
    )
    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    # When I receive Lynch diagnosis "EPCAM" for a new subject in my hub aged "25" with diagnosis date "1 year ago" and no last colonoscopy date
    nhs_no = LynchUtils(page).insert_validated_lynch_patient_from_new_subject_with_age(
        age="25",
        gene="EPCAM",
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
            "Subject lower lynch age": "25",
            "Screening status": "Lynch Surveillance",
            "Screening status date of change": "Today",
            "Screening status reason": "Eligible for Lynch Surveillance",
            "Subject age": "25",
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
            "Lynch due date": "25th birthday",
            "Lynch due date date of change": "Today",
            "Lynch due date reason": "Selected for Lynch Surveillance",
            "Previous screening status": "Null",
            "Screening due date": "Null",
            "Screening due date date of change": "Null",
            "Screening due date reason": "Null",
            "Subject has an open episode": "Yes",
            "Subject has lynch diagnosis": "Yes",
            "Subject lower FOBT age": "Default",
            "Subject lower lynch age": "25",
            "Screening status": "Lynch Surveillance",
            "Screening status date of change": "Today",
            "Screening status reason": "Eligible for Lynch Surveillance",
            "Subject age": "25",
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

    logging.info("Make sure the subject is within the Lynch age range at recall")

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I receive an SSPI update to change their date of birth to "34" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 34)

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
    UserTools.user_login(page, "Screening Centre Manager at BCS001")

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page).expand_episodes_list()
    SubjectScreeningSummaryPage(page).click_first_lynch_surveillance_episode_link()

    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # And I attend the subject's practitioner appointment "3 days ago"
    AppointmentDetailPage(page).mark_appointment_as_attended(
        datetime.today() - timedelta(days=3)
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
            "which diagnostic test": "Latest test in latest episode",
            "diagnostic test proposed type": "Colonoscopy",
            "diagnostic test confirmed type": "Null",
            "diagnostic test intended extent": "Null",
            "latest event status": "A59 Invited for Diagnostic Test",
        },
    )

    # When I select the advance episode option for "Attend Diagnostic Test"
    AdvanceLynchSurveillanceEpisodePage(page).click_attend_diagnostic_test_button()

    # Then I confirm the value of the diagnostic test attendance field "Proposed Type of Test" is "Colonoscopy"
    AttendDiagnosticTestPage(page).confirm_proposed_type_of_test(
        "Proposed Type of Test", "Colonoscopy"
    )

    # And I confirm the value of the diagnostic test attendance field "Actual Type of Test" is "Colonoscopy"
    AttendDiagnosticTestPage(page).confirm_proposed_type_of_test(
        "Actual Type of Test", "Colonoscopy"
    )

    # When I attend the subject's diagnostic test
    AttendDiagnosticTestPage(page).click_calendar_button()
    CalendarPicker(page).v1_calender_picker(datetime.today())
    AttendDiagnosticTestPage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Latest test in latest episode",
            "diagnostic test proposed type": "Colonoscopy",
            "diagnostic test confirmed type": "Colonoscopy",
            "diagnostic test intended extent": "Null",
            "latest event status": "A259 Attended Diagnostic Test",
        },
    )

    logging.info("Complete the investigation dataset to give a result of No result")

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I edit the Investigation Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    # Confirm on the investigation Datasets Page
    InvestigationDatasetsPage(page).bowel_cancer_screening_page_title_contains_text(
        "Investigation Datasets"
    )

    # Then message "WARNING - Resect & Discard is not appropriate for a Lynch patient." is displayed at the top of the investigation dataset
    InvestigationDatasetsPage(page).message_is_displayed(
        "WARNING - Resect & Discard is not appropriate for a Lynch patient."
    )

    # And I open all minimized sections on the dataset
    InvestigationDatasetsPage(page).open_all_minimized_sections()

    # And I set the following fields and values within the "Investigation Dataset" section of the investigation dataset:
    InvestigationDatasetCompletion(page).fill_out_general_information(
        {
            "practitioner": 1,
            "site": 1,
            "testing clinician": 1,
            "aspirant endoscopist": None,
        }
    )

    # And I add the following bowel preparation drugs and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_drug_information(
        {
            "drug_dose1": "3",
            "drug_type1": DrugTypeOptions.MANNITOL,
        }
    )

    # And I set the following fields and values within the "Endoscopy Information" section of the investigation dataset:
    InvestigationDatasetCompletion(page).fill_endoscopy_information(
        {
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
    )

    # And I set the following failure reasons within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_failure_information(
        {"failure reasons": FailureReasonsOptions.PAIN}
    )

    # And I mark the Investigation Dataset as completed
    InvestigationDatasetsPage(page).check_dataset_complete_checkbox()

    # Then the Investigation Dataset result message, which I will cancel, is "No Result"
    InvestigationDatasetsPage(page).click_save_dataset_button_assert_dialog("No Result")

    # And I press the save Investigation Dataset button
    InvestigationDatasetsPage(page).click_save_dataset_button()

    # Then I confirm the Episode Result is "No Result"
    EpisodeRepository().confirm_episode_result(nhs_no, "No Result")

    logging.info(
        "Progress the episode via post-investigation telephone contact to referral for symptomatic"
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Enter Diagnostic Test Outcome"
    SubjectScreeningSummaryPage(page).click_advance_lynch_surveillance_episode_button()
    AdvanceLynchSurveillanceEpisodePage(
        page
    ).click_enter_diagnostic_test_outcome_button()

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
    DiagnosticTestOutcomePage(page).text_is_visible(
        "Diagnostic Test Date resulting in a recall due date", False
    )

    # When I select Reason for Symptomatic Referral value "Suspected Cancer Surgery"
    DiagnosticTestOutcomePage(page).select_reason_for_symptomatic_referral_option(
        ReasonForSymptomaticReferral.SUSPECTED_CANCER_SURGERY
    )

    # And I save the Diagnostic Test Outcome information
    DiagnosticTestOutcomePage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A315 Diagnostic Test Outcome Entered"},
    )

    # When I advance the subject's episode for "Other Post-investigation Contact Required"
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_lynch_surveillance_episode_button()
    AdvanceLynchSurveillanceEpisodePage(
        page
    ).click_other_post_investigation_contact_required_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A361 Other Post-investigation Contact Required"},
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Record other post-investigation contact"
    SubjectScreeningSummaryPage(page).click_advance_lynch_surveillance_episode_button()
    AdvanceLynchSurveillanceEpisodePage(
        page
    ).click_record_other_post_investigation_contact_button()

    # Then I confirm the patient outcome dropdown has the following options:
    ContactWithPatientPage(page).patient_outcome_dropdown_contains_options(
        [
            "Post-investigation Appointment Not Required",
            "Post-investigation Appointment Required",
            "No outcome",
        ]
    )

    # When I record contact with the subject with outcome "Post-investigation Appointment Not Required"
    ContactWithPatientPage(page).record_post_investigation_appointment_not_required()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A323 Post-investigation Appointment NOT Required",
            "latest event status": "A317 Post-investigation Contact Made ",
        },
    )

    # When I select the advance episode option for "MDT Referral Required"
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_lynch_surveillance_episode_button()
    AdvanceLynchSurveillanceEpisodePage(page).click_mdt_referral_required_button()

    # And I enter simple MDT information
    ReferToMDTPage(page).enter_date_in_mdt_discussion_date_field(datetime.today())
    ReferToMDTPage(page).select_mdt_location_lookup(1)
    ReferToMDTPage(page).click_record_mdt_appointment_button()
    page.wait_for_timeout(500)  # Timeout to allow subject to update in the DB.

    #  Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A348 MDT Referral Required"},
    )

    # And there is a "A348" letter batch for my subject with the exact title "GP Letter Indicating Referral to MDT (Lynch)"
    # When I process the open "A348" letter batch for my subject
    batch_processing(
        page,
        "A348",
        "GP Letter Indicating Referral to MDT (Lynch)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A372 Refer Symptomatic, GP Letter Printed",
        },
    )

    logging.info("Symptomatic procedure of non-neoplastic")

    # When I view the advance episode options
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_lynch_surveillance_episode_button()

    # Then I "can" advance the subject's episode for "Non-neoplastic and Other Non-bowel Cancer Result"
    AdvanceLynchSurveillanceEpisodePage(
        page
    ).non_neoplastic_and_other_non_bowel_cancer_result_button.is_visible()

    # And I select the advance episode option for "Non-neoplastic and Other Non-bowel Cancer Result"
    AdvanceLynchSurveillanceEpisodePage(
        page
    ).click_non_neoplastic_and_other_non_bowel_cancer_result_button()

    # And I set the Date of Symptomatic Procedure to "2 days ago"
    NonNeoplasticResultFromSymptomaticProcedurePage(
        page
    ).enter_date_of_symptomatic_procedure(datetime.today() - timedelta(days=2))

    # And the Screening Interval is 24 months
    NonNeoplasticResultFromSymptomaticProcedurePage(page).assert_text_in_alert_textbox(
        "recall interval of 24 months"
    )

    # And I select test number 1
    NonNeoplasticResultFromSymptomaticProcedurePage(page).select_test_number(1)

    # And I save the Result from Symptomatic Procedure
    NonNeoplasticResultFromSymptomaticProcedurePage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Latest not-void test in latest episode",
            "latest episode accumulated result": "Abnormal",
            "latest event status": "A373 Symptomatic result recorded",
            "symptomatic procedure date": "2 days ago",
            "symptomatic procedure result": "Non-neoplastic",
        },
    )

    # When I advance the subject's episode for "Return to Lynch after symptomatic referral"
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_lynch_surveillance_episode_button()
    AdvanceLynchSurveillanceEpisodePage(
        page
    ).click_return_to_lynch_after_symptomatic_referral_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A377 Return to Lynch after symptomatic referral",
        },
    )

    # And there is a "A377" letter batch for my subject with the exact title "Return to Lynch after symptomatic referral"
    # When I process the open "A377" letter batch for my subject
    batch_processing(
        page,
        "A377",
        "Return to Lynch after symptomatic referral",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Latest not-void test in latest episode",
            "calculated fobt due date": "Null",
            "calculated lynch due date": "2 years from Symptomatic Procedure",
            "calculated surveillance due date": "Unchanged",
            "latest episode accumulated result": "Abnormal",
            "latest episode recall calculation method": "Symptomatic Procedure date",
            "latest episode recall episode type": "Lynch Surveillance",
            "latest episode status": "Closed",
            "latest episode status reason": "Episode Complete",
            "latest event status": "A65 Abnormal/No Result",
            "screening due date": "Null",
            "screening due date date of change": "Null",
            "screening due date reason": "Null",
            "symptomatic procedure date": "2 days ago",
            "symptomatic procedure result": "Non-neoplastic",
            "screening referral type": "Null",
            "screening status": "Lynch Surveillance",
            "screening status date of change": "Unchanged",
            "screening status reason": "Lynch Surveillance",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Unchanged",
            "surveillance due date reason": "Unchanged",
        },
    )

    LogoutPage(page).log_out()
