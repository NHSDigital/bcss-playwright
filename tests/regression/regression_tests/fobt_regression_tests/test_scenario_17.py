import pytest
import logging
from datetime import datetime, timedelta
from playwright.sync_api import Page
from classes.repositories.episode_repository import EpisodeRepository
from classes.repositories.subject_repository import SubjectRepository
from classes.subject.subject import Subject
from classes.user.user import User
from pages.base_page import BasePage
from pages.datasets.colonoscopy_dataset_page import (
    ColonoscopyDatasetsPage,
    FitForColonoscopySspOptions,
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
from pages.screening_subject_search.diagnostic_test_outcome_page import (
    DiagnosticTestOutcomePage,
    OutcomeOfDiagnosticTest,
    ReasonForSymptomaticReferral,
)
from pages.screening_subject_search.episode_events_and_notes_page import (
    EpisodeEventsAndNotesPage,
)
from pages.screening_subject_search.handover_into_symptomatic_care_page import (
    HandoverIntoSymptomaticCarePage,
)
from pages.screening_subject_search.record_diagnosis_date_page import (
    RecordDiagnosisDatePage,
)
from pages.screening_subject_search.refer_to_mdt_page import ReferToMDTPage
from pages.logout.log_out_page import LogoutPage
from utils.appointments import book_appointments, book_post_investigation_appointment
from utils.batch_processing import batch_processing
from utils.calendar_picker import CalendarPicker
from utils.fit_kit import FitKitGeneration, FitKitLogged
from utils.investigation_dataset import InvestigationDatasetCompletion
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from utils.subject_assertion import subject_assertion
from utils.user_tools import UserTools
from utils import screening_subject_page_searcher
from utils.oracle.oracle import OracleDB
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
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
    ReasonPathologyLostOptions,
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
)
from classes.repositories.person_repository import PersonRepository
from pages.organisations.organisations_page import OrganisationSwitchPage


@pytest.mark.wip
@pytest.mark.usefixtures("setup_org_and_appointments")
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.fobt_regression_tests
def test_scenario_17(page: Page) -> None:
    """
        Scenario: 17: Unsuitable for symptomatic (cease)

        S9-S10-S43-A8-A183-A25-J10-(A50)-A99-A59-A259-A315-A360-A410-A415-A416-A316-A348-A372-A357-(A167)-A356-C203 [SSCL24b]

        This scenario tests the episode pathway in which the subject is referred for a symptomatic procedure, but after an MDT they are discharged as being unsuitable.  During the handover, the decision is made to cease the subject from the programme.

        Scenario summary:

    > Find an in-age subject at S9 whose episode started recently before today (1.1)
    > Process S9 letter batch > S10 (1.1)
    > Log kit > S43 (1.2)
    > Read kit with ABNORMAL result > A8 (1.3)
    > Invite for colonoscopy assessment > A183 (1.11)
    > Process A183 appointment letter > A25 (1.11)
    > Attend assessment appointment > J10 (1.11)
    > Record diagnosis date (A50)
    > Suitable for colonoscopy > A99 (1.12)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset – LNPCP (2.1)
    > Enter diagnostic test outcome – refer symptomatic > A315 (2.1)
    > Post-investigation appointment required > A360 (2.1)
    > Book post-investigation appointment > A410 (2.4)
    > Process A410 letter batch > A415 (2.4)
    > Attend post-investigation appointment > A416 > A316 (2.4)
    > MDT required - record MDT > A348 (2.6)
    > Process A348 letter batch > A372 (2.6)
    > Unsuitable for symptomatic procedure – handover to clinician & cease > A357 (2.6)
    > Process A183 result letter (A167) (1.11)
    > Process A357 letter batch > A356 > C203 (2.6)
    > Check recall [SSCL24b]
    """
    # Given I log in to BCSS "England" as user role "Hub Manager"
    user_role = UserTools.user_login(
        page, "Hub Manager at BCS01", return_role_type=True
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
        "subject hub code": "User's hub",
    }

    user = User().from_user_role_type(user_role)

    query, bind_vars = SubjectSelectionQueryBuilder().build_subject_selection_query(
        criteria=criteria,
        user=user,
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
        page=page,
        batch_type="S9",
        latest_event_status="S10 - Invitation & Test Kit Sent",
        batch_description="Invitation & Test Kit (FIT)",
    )

    # When I log my subject's latest unlogged FIT kit
    fit_kit = FitKitGeneration().get_fit_kit_for_subject_sql(nhs_no, False, False)
    FitKitLogged().log_fit_kits(
        page=page,
        sample_date=datetime.now(),
        fit_kit=fit_kit,
    )

    # Then my subject has been updated as follows:
    criteria = {"latest event status": "S43 Kit Returned and Logged (Initial Test)"}
    subject_assertion(nhs_no, criteria)

    # When I read my subject's latest logged FIT kit as "ABNORMAL"
    FitKitLogged().read_latest_logged_kit(
        user=user_role, kit=fit_kit, kit_type=2, kit_result="ABNORMAL"
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
    screening_centre = "BCS001 - Wolverhampton Bowel Cancer Screening Centre"
    site = "The Royal Hospital (Wolverhampton)"

    book_appointments(
        page,
        screening_centre=screening_centre,
        site=site,
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A183 1st Colonoscopy Assessment Appointment Requested"
        },
    )

    # And there is a "A183" letter batch for my subject with the exact title "Practitioner Clinic 1st Appointment"
    letter_code = "A183"
    letter_type = "Practitioner Clinic 1st Appointment"
    is_active = True

    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no, letter_code, letter_type, is_active
    )
    # And there is a "A183" letter batch for my subject with the exact title "GP Result (Abnormal)"
    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no, "A183", "GP Result (Abnormal)", True
    )
    # When I process the open "A183 - Practitioner Clinic 1st Appointment" letter batch for my subject
    batch_processing(
        page=page,
        batch_description="Practitioner Clinic 1st Appointment",
        batch_type="A183",
        latest_event_status="A25 - 1st Colonoscopy Assessment Appointment Booked, letter sent",
    )
    # When I switch users to BCSS "England" as user role "Specialist Screening Practitioner"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(
        page, "Specialist Screening Practitioner at BCS009 & BCS001", True
    )

    OrganisationSwitchPage(page).select_organisation_by_id("BCS001")
    OrganisationSwitchPage(page).click_continue()
    if user_role is None:
        raise ValueError("User role is none")

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page).expand_episodes_list()
    SubjectScreeningSummaryPage(page).click_first_fobt_episode_link()
    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()
    # And I attend the subject's practitioner appointment "yesterday"
    AppointmentDetailPage(page).mark_appointment_as_attended(
        datetime.today() - timedelta(1)
    )
    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "J10 1st Colonoscopy Assessment Appointment Attended"},
    )
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    # And I select the advance episode option for "Record Diagnosis Date"
    AdvanceFOBTScreeningEpisodePage(page).click_record_diagnosis_date_button()
    # And I enter a Diagnosis Date of "today"
    RecordDiagnosisDatePage(page).enter_date_in_diagnosis_date_field(datetime.today())
    # And I save Diagnosis Date Information
    RecordDiagnosisDatePage(page).click_save_button()
    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode diagnosis date reason": "Null",
            "latest episode has diagnosis date": "Yes",
            "latest episode includes event status": "A50 Diagnosis date recorded",
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
        option=FitForColonoscopySspOptions.YES
    )
    ColonoscopyDatasetsPage(page).click_dataset_complete_radio_button_yes()

    # And I save the Colonoscopy Assessment Dataset
    ColonoscopyDatasetsPage(page).save_dataset()
    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I advance the subject's episode for "Suitable for Endoscopic Test"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_suitable_for_endoscopic_test_button()
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
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    # And I enter a Diagnostic Test First Offered Appointment Date of "tomorrow"
    AdvanceFOBTScreeningEpisodePage(page).click_calendar_button()
    CalendarPicker(page).v1_calender_picker(datetime.today() + timedelta(days=1))
    # And I select Diagnostic Test Type "Colonoscopy"
    AdvanceFOBTScreeningEpisodePage(page).select_test_type_dropdown_option(
        "Colonoscopy"
    )

    # And I advance the subject's episode for "Invite for Diagnostic Test >>"
    AdvanceFOBTScreeningEpisodePage(page).click_invite_for_diagnostic_test_button()

    # Then my subject has been updated as follows:
    AdvanceFOBTScreeningEpisodePage(page).verify_latest_event_status_value(
        latest_event_status="A59 - Invited for Diagnostic Test"
    )

    # When I select the advance episode option for "Attend Diagnostic Test"
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_attend_diagnostic_test_button()

    # And I attend the subject's diagnostic test today
    AttendDiagnosticTestPage(page).click_calendar_button()
    CalendarPicker(page).v1_calender_picker(datetime.today())
    AttendDiagnosticTestPage(page).click_save_button()

    # Then my subject has been updated as follows:
    criteria = {"latest event status": "A259 Attended Diagnostic Test"}
    subject_assertion(
        nhs_number=nhs_no,
        criteria=criteria,
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I edit the Investigation Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    # And I open all minimized sections on the dataset
    SubjectDatasetsPage(page).click_investigation_show_datasets()
    # And I mark the Investigation Dataset as completed
    # When I press the save Investigation Dataset button
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
    endoscopy_information = {
        "endoscope inserted": "yes",
        "procedure type": "therapeutic",
        "bowel preparation quality": BowelPreparationQualityOptions.GOOD,
        "comfort during recovery": ComfortOptions.NO_DISCOMFORT,
        "comfort during examination": ComfortOptions.NO_DISCOMFORT,
        "endoscopist defined extent": EndoscopyLocationOptions.APPENDIX,
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
    general_information = {
        "practitioner": 1,
        "site": 1,
        "testing clinician": person_name,
        "aspirant endoscopist": None,
    }

    # And I set the following completion proof values within the Investigation Dataset for this subject:
    completion_information = {"completion proof": CompletionProofOptions.VIDEO_APPENDIX}

    # And I set the following failure reasons within the Investigation Dataset for this subject:
    failure_information = {"failure reasons": FailureReasonsOptions.NO_FAILURE_REASONS}
    # And I add new polyp 1-3 with the following fields and values within the Investigation Dataset for this subject:
    polyp_information = [
        {
            "location": EndoscopyLocationOptions.ANASTOMOSIS,
            "classification": PolypClassificationOptions.IP,
            "polyp access": PolypAccessOptions.EASY,
            "estimate of whole polyp size": "11",
            "left in situ": YesNoOptions.NO,
        },
        {
            "location": EndoscopyLocationOptions.CAECUM,
            "classification": PolypClassificationOptions.LST_NG,
            "estimate of whole polyp size": "5",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        },
        {
            "location": EndoscopyLocationOptions.HEPATIC_FLEXURE,
            "classification": PolypClassificationOptions.LST_NG,
            "polyp access": PolypAccessOptions.EASY,
            "estimate of whole polyp size": "21",
            "left in situ": YesNoOptions.NO,
        },
    ]
    # And I add intervention for 3 polyps with the following fields and values within the Investigation Dataset for this subject:
    polyp_intervention = [
        [
            {
                "modality": PolypInterventionModalityOptions.POLYPECTOMY,
                "excised": YesNoOptions.YES,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
                "retrieved": PolypInterventionRetrievedOptions.YES,
            }
        ],
        [
            {
                "modality": PolypInterventionModalityOptions.EMR,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
                "excised": YesNoOptions.YES,
                "retrieved": PolypInterventionRetrievedOptions.YES,
                "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
            }
        ],
        [
            {
                "modality": PolypInterventionModalityOptions.POLYPECTOMY,
                "excised": YesNoOptions.YES,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
                "retrieved": PolypInterventionRetrievedOptions.YES,
                "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
                "polyp appears fully resected endoscopically": YesNoOptions.YES,
            }
        ],
    ]
    # And I add histology for 3 polyps with the following fields and values within the Investigation Dataset for this subject:
    polyp_histology = [
        {
            "date of reporting": datetime.today(),
            "date of receipt": datetime.today(),
            "pathology provider": 1,
            "pathologist": 1,
            "polyp type": PolypTypeOptions.ADENOMA,
            "adenoma sub type": AdenomaSubTypeOptions.NOT_REPORTED,
            "polyp excision complete": PolypExcisionCompleteOptions.R1,
            "polyp size": "13",
            "polyp dysplasia": PolypDysplasiaOptions.NOT_REPORTED,
            "polyp carcinoma": YesNoUncertainOptions.NO,
        },
        {
            "date of reporting": datetime.today(),
            "date of receipt": datetime.today(),
            "pathology provider": 1,
            "pathologist": 1,
            "polyp type": PolypTypeOptions.ADENOMA,
            "adenoma sub type": AdenomaSubTypeOptions.TUBULOVILLOUS_ADENOMA,
            "polyp excision complete": PolypExcisionCompleteOptions.R1,
            "polyp size": "4",
            "polyp dysplasia": PolypDysplasiaOptions.NOT_REPORTED,
            "polyp carcinoma": YesNoUncertainOptions.NO,
        },
        {
            "pathology lost": YesNoOptions.YES,
            "reason pathology lost": ReasonPathologyLostOptions.LOST_IN_TRANSIT,
        },
    ]
    # When I press the save Investigation Dataset button
    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        endoscopy_information=endoscopy_information,
        drug_information=drug_information,
        failure_information=failure_information,
        completion_information=completion_information,
        polyp_information=polyp_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )
    # Then the Investigation Dataset result message, which I will cancel, is "LNPCP"
    InvestigationDatasetsPage(page).expect_text_to_be_visible("LNPCP")
    # Then I confirm the Polyp Algorithm Size for Polyp 1,2 and 3 are 13,4,21 respectively
    expected_size = 1
    expected_value = "13"

    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(expected_size, expected_value)

    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(2, "4")

    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(3, "21")
    # And I confirm the Polyp Category for Polyp 1,2,3 are "Advanced colorectal polyp", "Premalignant polyp" and "LNPCP" respectively
    InvestigationDatasetsPage(page).assert_polyp_category(
        1, "Advanced colorectal polyp"
    )

    InvestigationDatasetsPage(page).assert_polyp_category(2, "Premalignant polyp")

    InvestigationDatasetsPage(page).assert_polyp_category(3, "LNPCP")
    # And I confirm the Episode Result is "Abnormal"
    episode_result = "LNPCP"
    EpisodeRepository().confirm_episode_result(nhs_no, episode_result)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I advance the subject's episode for "Enter Diagnostic Test Outcome"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_enter_diagnostic_test_outcome_button()
    # And I select Outcome of Diagnostic Test "Refer Symptomatic"
    DiagnosticTestOutcomePage(page).select_test_outcome_option(
        OutcomeOfDiagnosticTest.REFER_SYMPTOMATIC
    )
    # And I select Reason for Symptomatic Referral value "Corrective Surgery"
    DiagnosticTestOutcomePage(page).select_reason_for_symptomatic_referral_option(
        ReasonForSymptomaticReferral.CORRECTIVE_SURGERY
    )
    # And I save the Diagnostic Test Outcome information
    DiagnosticTestOutcomePage(page).click_save_button()
    # Then my subject has been updated as follows:
    criteria = {"latest event status": "A315 Diagnostic Test Outcome Entered"}
    subject_assertion(
        nhs_no,
        criteria,
    )
    # When I advance the subject's episode for "Post-investigation Appointment Required"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(
        page
    ).click_post_investigation_appointment_required_button()
    #    Then my subject has been updated as follows:
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
    #  And I set the practitioner appointment date to "today"
    # And I book the "earliest" available practitioner appointment on this date
    book_post_investigation_appointment(page, "The Royal Hospital (Wolverhampton)", 1)
    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A410 Post-investigation Appointment Made",
        },
    )
    # And there is a "A410" letter batch for my subject with the exact title "Post-Investigation Appointment Invitation Letter"
    # When I process the open "A410 - Post-Investigation Appointment Invitation Letter" letter batch for my subject
    letter_code = "A410"
    letter_type = "Post-Investigation Appointment Invitation Letter"

    batch_processing(
        page,
        letter_code,
        letter_type,
    )
    # Then my subject has been updated as follows:
    criteria = {"latest event status": "A415 Post-investigation Appointment Invitation Letter Printed"}
    subject_assertion(
    nhs_no,
    criteria,
)
    #  When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page).expand_episodes_list()
    SubjectScreeningSummaryPage(page).click_first_fobt_episode_link()
    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()
    # And I attend the subject's practitioner appointment "today"
    AppointmentDetailPage(page).mark_appointment_as_attended(datetime.today())
    # Then my subject has been updated as follows:
    criteria = {
    "latest episode includes event status": "A416 Post-investigation Appointment Attended ",
    "latest event status": "A316 Post-investigation Appointment Attended ",
}
    subject_assertion(
    nhs_number=nhs_no,
    criteria=criteria,
)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # When I select the advance episode option for "MDT Referral Required"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_mdt_referral_required_button()
    # # And I enter simple MDT information
    ReferToMDTPage(page).enter_date_in_Mdt_discussion_date_field(datetime.today())
    ReferToMDTPage(page).select_mdt_location_lookup(1)
    ReferToMDTPage(page).click_record_MDT_appointment_button()
    #  Then my subject has been updated as follows:
    criteria = {"latest event status": "A348 MDT Referral Required"}
    subject_assertion(
    nhs_no,
    criteria,
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
    # # And I select the advance episode option for "Patient Unfit, Handover into Symptomatic Care"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_handover_into_symptomatic_care_button()
    # And I fill in Handover into Symptomatic Care form for Patient Unfit for Treatment and Cease from programme
    HandoverIntoSymptomaticCarePage(page).select_referral_dropdown_option(
        "Referral to Patient's GP Practice"
    )
    HandoverIntoSymptomaticCarePage(page).select_practitioner_from_index(1)
    HandoverIntoSymptomaticCarePage(page).fill_notes("Handover notes - unfit (cease)")
    HandoverIntoSymptomaticCarePage(page).select_cease_from_program(True)
    HandoverIntoSymptomaticCarePage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A357 Patient Unfit, Handover into Symptomatic Care",
        },
    )
    # And there is a "A357" letter batch for my subject with the exact title "Handover into Symptomatic Care, Patient Unfit"
    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no, "A357", "Handover into Symptomatic Care, Patient Unfit", True
    )
    # When I switch users to BCSS "England" as user role "Hub Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    UserTools.user_login(
        page, "Hub Manager at BCS01", return_role_type=True
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I process the open "A183 - GP Result (Abnormal)" letter batch for my subject
    batch_processing(
        page=page,
        batch_type="A183",
        batch_description="GP Result (Abnormal)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A167 GP Abnormal FOBT Result Sent",
            "latest event status": "A357 Patient Unfit, Handover into Symptomatic Care",
        },
    )
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(
        page, "Specialist Screening Practitioner at BCS009 & BCS001", True
    )

    OrganisationSwitchPage(page).select_organisation_by_id("BCS001")
    OrganisationSwitchPage(page).click_continue()
    if user_role is None:
        raise ValueError("User role is none")
    # And I process the open "A357 - Handover into Symptomatic Care, Patient Unfit" letter batch for my subject
    batch_processing(
        page,
        "A357",
        "Handover into Symptomatic Care, Patient Unfit",
    )
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Only not-void test in latest episode",
            "calculated fobt due date": "2 years from diagnostic test",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "Unchanged",
            "ceased confirmation date": "Today",
            "ceased confirmation details": "Handover notes - unfit (cease)",
            "ceased confirmation user id": "User's ID",
            "clinical reason for cease": "Null",
            "latest episode recall calculation method": "Diagnostic Test Date",
            "latest episode recall episode type": "FOBT Screening",
            "latest episode recall surveillance type": "Null",
            "latest episode status reason": "Discharged from Screening into Symptomatic care",
            "latest event status": "A356 Handover into Symptomatic Care, Patient Unfit, GP Letter Printed",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Today",
            "screening due date reason": "Discharged, Patient Unfit",
            "screening status": "Ceased",
            "screening status date of change": "Today",
            "screening status reason": "Discharged, Patient Unfit",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Unchanged",
            "surveillance due date reason": "Unchanged",
            "symptomatic procedure date": "Null",
            "symptomatic procedure result": "Patient is unfit for a symptomatic procedure at this time",
            "screening referral type": "Null",
        },
        user_role=user_role,
    )
    LogoutPage(page).log_out()
