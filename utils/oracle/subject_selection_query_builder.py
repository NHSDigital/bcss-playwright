from typing import Dict, Union, Tuple, Optional
import logging
from datetime import datetime, date
from classes.bowel_scope_dd_reason_for_change_type import (
    BowelScopeDDReasonForChangeType,
)
from classes.ceased_confirmation_details import CeasedConfirmationDetails
from classes.ceased_confirmation_user_id import CeasedConfirmationUserId
from classes.clinical_cease_reason_type import ClinicalCeaseReasonType
from classes.date_description import DateDescription
from classes.event_status_type import EventStatusType
from classes.episode_type import EpisodeType
from classes.has_gp_practice import HasGPPractice
from classes.has_unprocessed_sspi_updates import HasUnprocessedSSPIUpdates
from classes.has_user_dob_update import HasUserDobUpdate
from classes.subject_has_episode import SubjectHasEpisode
from classes.manual_cease_requested import ManualCeaseRequested
from classes.screening_status_type import ScreeningStatusType
from classes.sdd_reason_for_change_type import SDDReasonForChangeType
from classes.ssdd_reason_for_change_type import SSDDReasonForChangeType
from classes.ss_reason_for_change_type import SSReasonForChangeType
from classes.subject_hub_code import SubjectHubCode
from classes.subject_screening_centre_code import SubjectScreeningCentreCode
from classes.subject_selection_criteria_key import SubjectSelectionCriteriaKey
from classes.subject import Subject
from classes.user import User
from classes.selection_builder_exception import SelectionBuilderException
from classes.appointments_slot_type import AppointmentSlotType
from classes.appointment_status_type import AppointmentStatusType
from classes.which_diagnostic_test import WhichDiagnosticTest
from classes.diagnostic_test_type import DiagnosticTestType
from classes.diagnostic_test_is_void import DiagnosticTestIsVoid
from classes.diagnostic_test_has_result import DiagnosticTestHasResult
from classes.diagnostic_test_has_outcome_of_result import (
    DiagnosticTestHasOutcomeOfResult,
)
from classes.intended_extent_type import IntendedExtentType
from classes.latest_episode_has_dataset import LatestEpisodeHasDataset


class SubjectSelectionQueryBuilder:
    """
    Builds dynamic SQL queries for selecting screening subjects based on various criteria.
    """

    def __init__(self):
        """
        Initialise the query builder with empty SQL clause lists and bind variable dictionary.
        """
        self.sql_select = []
        self.sql_from = []
        self.sql_where = []
        self.sql_from_episode = []
        self.sql_from_genetic_condition_diagnosis = []
        self.sql_from_cancer_audit_datasets = []
        self.bind_vars = {}
        self.criteria_value_count = 0

        self.xt = "xt"
        self.ap = "ap"

    def build_subject_selection_query(
        self,
        criteria: Dict[str, str],
        user: "User",
        subject: "Subject",
        subjects_to_retrieve: Optional[int] = None,
    ) -> tuple[str, dict]:
        self._build_select_clause()
        self._build_main_from_clause()
        self._start_where_clause()
        self._add_variable_selection_criteria(criteria, user, subject)
        if subjects_to_retrieve is not None:
            self._end_where_clause(subjects_to_retrieve)
        else:
            self._end_where_clause(1)

        query = " ".join(
            self.sql_select
            + self.sql_from
            + self.sql_from_episode
            + self.sql_from_genetic_condition_diagnosis
            + self.sql_from_cancer_audit_datasets
            + self.sql_where
        )
        logging.info("Final query: %s", query)
        return query, self.bind_vars

    def _build_select_clause(self) -> None:
        columns: list[str] = [
            "ss.screening_subject_id,",
            "ss.subject_nhs_number,",
            "c.person_family_name,",
            "c.person_given_name,",
            "ss.datestamp,",
            "ss.screening_status_id,",
            "ss.ss_reason_for_change_id,",
            "ss.screening_status_change_date,",
            "ss.screening_due_date,",
            "ss.sdd_reason_for_change_id,",
            "ss.sdd_change_date,",
            "ss.calculated_sdd,",
            "ss.surveillance_screen_due_date,",
            "ss.calculated_ssdd,",
            "ss.surveillance_sdd_rsn_change_id,",
            "ss.surveillance_sdd_change_date,",
            "ss.lynch_screening_due_date,",
            "ss.lynch_sdd_reason_for_change_id,",
            "ss.lynch_sdd_change_date,",
            "ss.lynch_calculated_sdd,",
            "c.date_of_birth,",
            "c.date_of_death ",
        ]
        self.sql_select.append("SELECT " + ", ".join(columns))

    def _build_main_from_clause(self) -> None:
        self.sql_from.append(
            " FROM screening_subject_t ss "
            " INNER JOIN sd_contact_t c ON c.nhs_number = ss.subject_nhs_number "
        )

    def _start_where_clause(self) -> None:
        self.sql_where.append(" WHERE 1=1 ")

    def _end_where_clause(self, subject_count: int) -> None:
        self.sql_where.append(f" FETCH FIRST {subject_count} ROWS ONLY ")

    def _add_variable_selection_criteria(
        self,
        criteria: Dict[str, str],
        user: "User",
        subject: "Subject",
    ):
        for criterium_key, criterium_value in criteria.items():
            self.criteria_key_name: str = criterium_key.lower()

            # Helper functions assumed to have correct typing elsewhere
            self.criteria_has_not_modifier: bool = (
                self._get_criteria_has_not_comparator(criterium_value)
            )
            self.criteria_value: str = self._get_criteria_value(criterium_value)
            self.criteria_comparator: str = self._get_criteria_comparator()

            if self.criteria_value.startswith("#"):
                self.criteria_value = ""

            if len(self.criteria_value) > 0:
                if subject is None and self.criteria_value.lower().startswith(
                    "unchanged"
                ):
                    raise ValueError(f"{self.criteria_key_name}: No existing subject")

                if (
                    self.criteria_value.lower() == "null"
                    and self.criteria_has_not_modifier
                ):
                    self._force_not_modifier_is_invalid_for_criteria_value()

                try:
                    self.criteria_key = SubjectSelectionCriteriaKey.by_description(
                        self.criteria_key_name.replace("+", "")
                    )
                    if self.criteria_key is None:
                        raise ValueError(
                            f"No SubjectSelectionCriteriaKey found for description: {self.criteria_key_name}"
                        )

                    self._check_if_more_than_one_criteria_value_is_valid_for_criteria_key()
                    self._check_if_not_modifier_is_valid_for_criteria_key()

                    match self.criteria_key:
                        # ------------------------------------------------------------------------
                        # 👤 Demographics & Subject Identity Criteria
                        # ------------------------------------------------------------------------
                        case SubjectSelectionCriteriaKey.NHS_NUMBER:
                            self.criteria_value.replace(" ", "")
                            self._add_criteria_nhs_number()
                        case (
                            SubjectSelectionCriteriaKey.SUBJECT_AGE
                            | SubjectSelectionCriteriaKey.SUBJECT_AGE_YD
                        ):
                            self._add_criteria_subject_age()
                        case SubjectSelectionCriteriaKey.SUBJECT_HUB_CODE:
                            self._add_criteria_subject_hub_code(user)
                        # ------------------------------------------------------------------------
                        # 🏥 Screening Centre & GP Linkage Criteria
                        # ------------------------------------------------------------------------
                        case (
                            SubjectSelectionCriteriaKey.RESPONSIBLE_SCREENING_CENTRE_CODE
                        ):
                            self._add_criteria_subject_screening_centre_code(user)
                        case SubjectSelectionCriteriaKey.HAS_GP_PRACTICE:
                            self._add_criteria_has_gp_practice()
                        case (
                            SubjectSelectionCriteriaKey.HAS_GP_PRACTICE_ASSOCIATED_WITH_SCREENING_CENTRE_CODE
                        ):
                            self._add_criteria_has_gp_practice_linked_to_sc()
                        # ------------------------------------------------------------------------
                        # 🩺 Screening Status & Change History Criteria
                        # ------------------------------------------------------------------------
                        case SubjectSelectionCriteriaKey.SCREENING_STATUS:
                            self._add_criteria_screening_status(subject)
                        case SubjectSelectionCriteriaKey.PREVIOUS_SCREENING_STATUS:
                            self._add_criteria_previous_screening_status()
                        case SubjectSelectionCriteriaKey.SCREENING_STATUS_REASON:
                            self._add_criteria_screening_status_reason(subject)
                        case (
                            SubjectSelectionCriteriaKey.SCREENING_STATUS_DATE_OF_CHANGE
                        ):
                            self._add_criteria_date_field(
                                subject, "ALL_PATHWAYS", "SCREENING_STATUS_CHANGE_DATE"
                            )
                        # ------------------------------------------------------------------------
                        # ⏰ Due Dates: Screening, Surveillance & Lynch Pathways
                        # ------------------------------------------------------------------------
                        case SubjectSelectionCriteriaKey.PREVIOUS_LYNCH_DUE_DATE:
                            self._add_criteria_date_field(
                                subject, "LYNCH", "PREVIOUS_DUE_DATE"
                            )
                        case (
                            SubjectSelectionCriteriaKey.PREVIOUS_SCREENING_DUE_DATE
                            | SubjectSelectionCriteriaKey.PREVIOUS_SCREENING_DUE_DATE_BIRTHDAY
                        ):
                            self._add_criteria_date_field(
                                subject, "FOBT", "PREVIOUS_DUE_DATE"
                            )
                        case SubjectSelectionCriteriaKey.PREVIOUS_SURVEILLANCE_DUE_DATE:
                            self._add_criteria_date_field(
                                subject, "SURVEILLANCE", "PREVIOUS_DUE_DATE"
                            )
                        case (
                            SubjectSelectionCriteriaKey.SCREENING_DUE_DATE
                            | SubjectSelectionCriteriaKey.SCREENING_DUE_DATE_BIRTHDAY
                        ):
                            self._add_criteria_date_field(subject, "FOBT", "DUE_DATE")
                        case (
                            SubjectSelectionCriteriaKey.CALCULATED_SCREENING_DUE_DATE
                            | SubjectSelectionCriteriaKey.CALCULATED_SCREENING_DUE_DATE_BIRTHDAY
                            | SubjectSelectionCriteriaKey.CALCULATED_FOBT_DUE_DATE
                        ):
                            self._add_criteria_date_field(
                                subject, "FOBT", "CALCULATED_DUE_DATE"
                            )
                        case SubjectSelectionCriteriaKey.SCREENING_DUE_DATE_REASON:
                            self._add_criteria_screening_due_date_reason(subject)
                        case (
                            SubjectSelectionCriteriaKey.SCREENING_DUE_DATE_DATE_OF_CHANGE
                        ):
                            self._add_criteria_date_field(
                                subject, "FOBT", "DUE_DATE_CHANGE_DATE"
                            )
                        case SubjectSelectionCriteriaKey.SURVEILLANCE_DUE_DATE:
                            self._add_criteria_date_field(
                                subject, "SURVEILLANCE", "DUE_DATE"
                            )
                        case (
                            SubjectSelectionCriteriaKey.CALCULATED_SURVEILLANCE_DUE_DATE
                        ):
                            self._add_criteria_date_field(
                                subject, "SURVEILLANCE", "CALCULATED_DUE_DATE"
                            )
                        case SubjectSelectionCriteriaKey.SURVEILLANCE_DUE_DATE_REASON:
                            self._add_criteria_surveillance_due_date_reason(subject)
                        case (
                            SubjectSelectionCriteriaKey.SURVEILLANCE_DUE_DATE_DATE_OF_CHANGE
                        ):
                            self._add_criteria_date_field(
                                subject, "SURVEILLANCE", "DUE_DATE_CHANGE_DATE"
                            )
                        case SubjectSelectionCriteriaKey.BOWEL_SCOPE_DUE_DATE_REASON:
                            self._add_criteria_bowel_scope_due_date_reason()
                        # ------------------------------------------------------------------------
                        # ⛔ Cease & Manual Override Criteria
                        # ------------------------------------------------------------------------
                        case SubjectSelectionCriteriaKey.MANUAL_CEASE_REQUESTED:
                            self._add_criteria_manual_cease_requested()
                        case SubjectSelectionCriteriaKey.CEASED_CONFIRMATION_DATE:
                            self._add_criteria_date_field(
                                subject, "ALL_PATHWAYS", "CEASED_CONFIRMATION_DATE"
                            )
                        case SubjectSelectionCriteriaKey.CEASED_CONFIRMATION_DETAILS:
                            self._add_criteria_ceased_confirmation_details()
                        case SubjectSelectionCriteriaKey.CEASED_CONFIRMATION_USER_ID:
                            self._add_criteria_ceased_confirmation_user_id(user)
                        case SubjectSelectionCriteriaKey.CLINICAL_REASON_FOR_CEASE:
                            self._add_criteria_clinical_reason_for_cease()
                        # ------------------------------------------------------------------------
                        # 📦 Event Status & System Update Flags
                        # ------------------------------------------------------------------------
                        case (
                            SubjectSelectionCriteriaKey.SUBJECT_HAS_EVENT_STATUS
                            | SubjectSelectionCriteriaKey.SUBJECT_DOES_NOT_HAVE_EVENT_STATUS
                        ):
                            self._add_criteria_subject_has_event_status()
                        case (
                            SubjectSelectionCriteriaKey.SUBJECT_HAS_UNPROCESSED_SSPI_UPDATES
                        ):
                            self._add_criteria_has_unprocessed_sspi_updates()
                        case SubjectSelectionCriteriaKey.SUBJECT_HAS_USER_DOB_UPDATES:
                            self._add_criteria_has_user_dob_update()
                        # ------------------------------------------------------------------------
                        # 📁 Subject Has Episode & Age-Based Criteria
                        # ------------------------------------------------------------------------
                        case (
                            SubjectSelectionCriteriaKey.SUBJECT_HAS_EPISODES
                            | SubjectSelectionCriteriaKey.SUBJECT_HAS_AN_OPEN_EPISODE
                        ):
                            self._add_criteria_subject_has_episodes()
                        case SubjectSelectionCriteriaKey.SUBJECT_HAS_FOBT_EPISODES:
                            self._add_criteria_subject_has_episodes(EpisodeType.FOBT)
                        case SubjectSelectionCriteriaKey.SUBJECT_LOWER_FOBT_AGE:
                            self._add_criteria_subject_lower_fobt_age()
                        case SubjectSelectionCriteriaKey.SUBJECT_LOWER_LYNCH_AGE:
                            self._add_criteria_subject_lower_lynch_age()
                        # ------------------------------------------------------------------------
                        # 🧱 Latest Episode Attributes
                        # ------------------------------------------------------------------------
                        case SubjectSelectionCriteriaKey.LATEST_EPISODE_TYPE:
                            self._add_criteria_latest_episode_type()
                        case SubjectSelectionCriteriaKey.LATEST_EPISODE_SUB_TYPE:
                            self._add_criteria_latest_episode_sub_type()
                        case SubjectSelectionCriteriaKey.LATEST_EPISODE_STATUS:
                            self._add_criteria_latest_episode_status()

                        case SubjectSelectionCriteriaKey.LATEST_EPISODE_STATUS_REASON:
                            self._add_criteria_latest_episode_status_reason()
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_RECALL_CALCULATION_METHOD
                        ):
                            self._add_criteria_latest_episode_recall_calc_method()
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_RECALL_EPISODE_TYPE
                        ):
                            self._add_criteria_latest_episode_recall_episode_type()
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_RECALL_SURVEILLANCE_TYPE
                        ):
                            self._add_criteria_latest_episode_recall_surveillance_type()
                        # ------------------------------------------------------------------------
                        # 🎯 Event Code & Status Inclusion Criteria
                        # ------------------------------------------------------------------------
                        case SubjectSelectionCriteriaKey.LATEST_EVENT_STATUS:
                            self._add_criteria_event_status("ep.latest_event_status_id")
                        case SubjectSelectionCriteriaKey.PRE_INTERRUPT_EVENT_STATUS:
                            self._add_criteria_event_status(
                                "ep.pre_interrupt_event_status_id"
                            )
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_INCLUDES_EVENT_CODE
                        ):
                            self._add_criteria_event_code_in_episode(True)
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_DOES_NOT_INCLUDE_EVENT_CODE
                        ):
                            self._add_criteria_event_code_in_episode(False)
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_INCLUDES_EVENT_STATUS
                        ):
                            self._add_criteria_event_status_in_episode(True)
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_DOES_NOT_INCLUDE_EVENT_STATUS
                        ):
                            self._add_criteria_event_status_in_episode(False)
                        case SubjectSelectionCriteriaKey.LATEST_EPISODE_STARTED:
                            self._add_criteria_date_field(
                                subject, "ALL_PATHWAYS", "LATEST_EPISODE_START_DATE"
                            )
                        case SubjectSelectionCriteriaKey.LATEST_EPISODE_ENDED:
                            self._add_criteria_date_field(
                                subject, "ALL_PATHWAYS", "LATEST_EPISODE_END_DATE"
                            )
                        case SubjectSelectionCriteriaKey.LATEST_EPISODE_KIT_CLASS:
                            self._add_criteria_latest_episode_kit_class()
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_SIGNIFICANT_KIT_RESULT
                        ):
                            self._add_criteria_has_significant_kit_result()
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_REFERRAL_DATE
                        ):
                            self._add_criteria_has_referral_date()
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_DIAGNOSIS_DATE
                        ):
                            self._add_criteria_has_diagnosis_date()
                        case SubjectSelectionCriteriaKey.SUBJECT_HAS_DIAGNOSTIC_TESTS:
                            self._add_criteria_has_diagnostic_test(False)
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_DIAGNOSTIC_TEST
                        ):
                            self._add_criteria_has_diagnostic_test(True)
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_DIAGNOSIS_DATE_REASON
                        ):
                            self._add_criteria_diagnosis_date_reason()
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_COMPLETED_SATISFACTORILY
                        ):
                            self._add_criteria_latest_episode_completed_satisfactorily()
                        case (
                            SubjectSelectionCriteriaKey.HAS_DIAGNOSTIC_TEST_CONTAINING_POLYP
                        ):
                            self._add_criteria_has_diagnostic_test_containing_polyp()
                        # ------------------------------------------------------------------------
                        # 📦 Kit Metadata & Participation History
                        # ------------------------------------------------------------------------
                        case SubjectSelectionCriteriaKey.SUBJECT_HAS_UNLOGGED_KITS:
                            self._add_criteria_subject_has_unlogged_kits()
                        case SubjectSelectionCriteriaKey.SUBJECT_HAS_LOGGED_FIT_KITS:
                            self._add_criteria_subject_has_logged_fit_kits()
                        case SubjectSelectionCriteriaKey.SUBJECT_HAS_KIT_NOTES:
                            self._add_criteria_subject_has_kit_notes()
                        case SubjectSelectionCriteriaKey.SUBJECT_HAS_LYNCH_DIAGNOSIS:
                            self._add_criteria_subject_has_lynch_diagnosis()
                        case SubjectSelectionCriteriaKey.WHICH_TEST_KIT:
                            self._add_join_to_test_kits()
                        case SubjectSelectionCriteriaKey.KIT_HAS_BEEN_READ:
                            self._add_criteria_kit_has_been_read()
                        case SubjectSelectionCriteriaKey.KIT_RESULT:
                            self._add_criteria_kit_result()
                        case SubjectSelectionCriteriaKey.KIT_HAS_ANALYSER_RESULT_CODE:
                            self._add_criteria_kit_has_analyser_result_code()
                        case SubjectSelectionCriteriaKey.WHICH_APPOINTMENT:
                            self._add_join_to_appointments()
                        case SubjectSelectionCriteriaKey.APPOINTMENT_TYPE:
                            self._add_criteria_appointment_type()
                        case SubjectSelectionCriteriaKey.APPOINTMENT_STATUS:
                            self._add_criteria_appointment_status()
                        case SubjectSelectionCriteriaKey.APPOINTMENT_DATE:
                            self._add_criteria_date_field(
                                subject, "ALL_PATHWAYS", "APPOINTMENT_DATE"
                            )
                        case SubjectSelectionCriteriaKey.WHICH_DIAGNOSTIC_TEST:
                            self._add_join_to_diagnostic_tests()
                        case SubjectSelectionCriteriaKey.DIAGNOSTIC_TEST_CONFIRMED_TYPE:
                            self._add_criteria_diagnostic_test_type("confirmed")
                        case SubjectSelectionCriteriaKey.DIAGNOSTIC_TEST_PROPOSED_TYPE:
                            self._add_criteria_diagnostic_test_type("proposed")
                        case SubjectSelectionCriteriaKey.DIAGNOSTIC_TEST_IS_VOID:
                            self._add_criteria_diagnostic_test_is_void()
                        case SubjectSelectionCriteriaKey.DIAGNOSTIC_TEST_HAS_RESULT:
                            self._add_criteria_diagnostic_test_has_result()
                        case SubjectSelectionCriteriaKey.DIAGNOSTIC_TEST_HAS_OUTCOME:
                            self._add_criteria_diagnostic_test_has_outcome_of_result()
                        case (
                            SubjectSelectionCriteriaKey.DIAGNOSTIC_TEST_INTENDED_EXTENT
                        ):
                            self._add_criteria_diagnostic_test_intended_extent()
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_CANCER_AUDIT_DATASET
                            | SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_COLONOSCOPY_ASSESSMENT_DATASET
                            | SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_MDT_DATASET
                        ):
                            self._add_criteria_latest_episode_has_dataset()
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_LATEST_INVESTIGATION_DATASET
                        ):
                            self._add_criteria_latest_episode_latest_investigation_dataset()
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_DATASET_INTENDED_EXTENT
                        ):
                            self._add_criteria_latest_episode_intended_extent()
                        case SubjectSelectionCriteriaKey.SURVEILLANCE_REVIEW_STATUS:
                            self._add_criteria_surveillance_review_status()
                        case (
                            SubjectSelectionCriteriaKey.HAS_EXISTING_SURVEILLANCE_REVIEW_CASE
                        ):
                            self._add_criteria_does_subject_have_surveillance_review_case()
                        case SubjectSelectionCriteriaKey.SURVEILLANCE_REVIEW_CASE_TYPE:
                            self._add_criteria_surveillance_review_type()
                        case SubjectSelectionCriteriaKey.DATE_OF_DEATH:
                            self._add_criteria_date_field(
                                subject, "ALL_PATHWAYS", "DATE_OF_DEATH"
                            )
                        case (
                            SubjectSelectionCriteriaKey.HAS_HAD_A_DATE_OF_DEATH_REMOVAL
                        ):
                            self._add_criteria_has_date_of_death_removal()
                        case SubjectSelectionCriteriaKey.INVITED_SINCE_AGE_EXTENSION:
                            self._add_criteria_invited_since_age_extension()
                        case SubjectSelectionCriteriaKey.NOTE_COUNT:
                            self._add_criteria_note_count()
                        case (
                            SubjectSelectionCriteriaKey.LATEST_EPISODE_ACCUMULATED_RESULT
                        ):
                            self._add_criteria_latest_episode_accumulated_episode_result()
                        case SubjectSelectionCriteriaKey.SYMPTOMATIC_PROCEDURE_RESULT:
                            self._add_criteria_symmetric_procedure_result()
                        case SubjectSelectionCriteriaKey.SYMPTOMATIC_PROCEDURE_DATE:
                            self._add_criteria_date_field(
                                subject, "ALL_PATHWAYS", "SYMPTOMATIC_PROCEDURE_DATE"
                            )
                        case SubjectSelectionCriteriaKey.DIAGNOSTIC_TEST_CONFIRMED_DATE:
                            self._add_criteria_date_field(
                                subject,
                                "ALL_PATHWAYS",
                                "DIAGNOSTIC_TEST_CONFIRMED_DATE",
                            )
                        case SubjectSelectionCriteriaKey.SCREENING_REFERRAL_TYPE:
                            self._add_criteria_screening_referral_type()
                        case SubjectSelectionCriteriaKey.CALCULATED_LYNCH_DUE_DATE:
                            self._add_criteria_date_field(
                                subject, "LYNCH", "CALCULATED_DUE_DATE"
                            )
                        case SubjectSelectionCriteriaKey.LYNCH_DUE_DATE:
                            self._add_criteria_date_field(subject, "LYNCH", "DUE_DATE")
                        case SubjectSelectionCriteriaKey.LYNCH_DUE_DATE_REASON:
                            self._add_criteria_lynch_due_date_reason(subject)
                        case SubjectSelectionCriteriaKey.LYNCH_DUE_DATE_DATE_OF_CHANGE:
                            self._add_criteria_date_field(
                                subject, "LYNCH", "DUE_DATE_CHANGE_DATE"
                            )
                        case SubjectSelectionCriteriaKey.LYNCH_INCIDENT_EPISODE:
                            self._add_criteria_lynch_incident_episode()
                        case SubjectSelectionCriteriaKey.LYNCH_DIAGNOSIS_DATE:
                            self._add_criteria_date_field(
                                subject, "LYNCH", "DIAGNOSIS_DATE"
                            )
                        case SubjectSelectionCriteriaKey.LYNCH_LAST_COLONOSCOPY_DATE:
                            self._add_criteria_date_field(
                                subject, "LYNCH", "LAST_COLONOSCOPY_DATE"
                            )
                        case SubjectSelectionCriteriaKey.SUBJECT_75TH_BIRTHDAY:
                            self._add_criteria_date_field(
                                subject, "ALL_PATHWAYS", "SEVENTY_FIFTH_BIRTHDAY"
                            )
                        # ------------------------------------------------------------------------
                        # 🧬 CADS Clinical Dataset Filters
                        # ------------------------------------------------------------------------
                        case SubjectSelectionCriteriaKey.CADS_ASA_GRADE:
                            self._add_criteria_cads_asa_grade()
                        case SubjectSelectionCriteriaKey.CADS_STAGING_SCANS:
                            self._add_criteria_cads_staging_scans()
                        case SubjectSelectionCriteriaKey.CADS_TYPE_OF_SCAN:
                            self._add_criteria_cads_type_of_scan()
                        case SubjectSelectionCriteriaKey.CADS_METASTASES_PRESENT:
                            self._add_criteria_cads_metastases_present()
                        case SubjectSelectionCriteriaKey.CADS_METASTASES_LOCATION:
                            self._add_criteria_cads_metastases_location()
                        case SubjectSelectionCriteriaKey.CADS_METASTASES_OTHER_LOCATION:
                            self._add_criteria_cads_metastases_other_location(
                                self.criteria_value
                            )
                        case (
                            SubjectSelectionCriteriaKey.CADS_FINAL_PRE_TREATMENT_T_CATEGORY
                        ):
                            self._add_criteria_cads_final_pre_treatment_t_category()
                        case (
                            SubjectSelectionCriteriaKey.CADS_FINAL_PRE_TREATMENT_N_CATEGORY
                        ):
                            self._add_criteria_cads_final_pre_treatment_n_category()
                        case (
                            SubjectSelectionCriteriaKey.CADS_FINAL_PRETREATMENT_M_CATEGORY
                        ):
                            self._add_criteria_cads_final_pre_treatment_m_category()
                        case SubjectSelectionCriteriaKey.CADS_TREATMENT_RECEIVED:
                            self._add_criteria_cads_treatment_received()
                        case (
                            SubjectSelectionCriteriaKey.CADS_REASON_NO_TREATMENT_RECEIVED
                        ):
                            self._add_criteria_cads_reason_no_treatment_received()
                        case SubjectSelectionCriteriaKey.CADS_TUMOUR_DATE_OF_DIAGNOSIS:
                            self._add_criteria_date_field(
                                subject, "ALL_PATHWAYS", "CADS_TUMOUR_DATE_OF_DIAGNOSIS"
                            )
                        case SubjectSelectionCriteriaKey.CADS_TUMOUR_LOCATION:
                            self._add_criteria_cads_tumour_location()
                        case (
                            SubjectSelectionCriteriaKey.CADS_TUMOUR_HEIGHT_OF_TUMOUR_ABOVE_ANAL_VERGE
                        ):
                            self._add_criteria_cads_tumour_height_of_tumour_above_anal_verge()
                        case (
                            SubjectSelectionCriteriaKey.CADS_TUMOUR_PREVIOUSLY_EXCISED_TUMOUR
                        ):
                            self._add_criteria_cads_tumour_previously_excised_tumour()
                        case SubjectSelectionCriteriaKey.CADS_TREATMENT_START_DATE:
                            self._add_criteria_date_field(
                                subject, "ALL_PATHWAYS", "CADS_TREATMENT_START_DATE"
                            )
                        case SubjectSelectionCriteriaKey.CADS_TREATMENT_TYPE:
                            self._add_criteria_cads_treatment_type()
                        case SubjectSelectionCriteriaKey.CADS_TREATMENT_GIVEN:
                            self._add_criteria_cads_treatment_given()
                        case SubjectSelectionCriteriaKey.CADS_CANCER_TREATMENT_INTENT:
                            self._add_criteria_cads_cancer_treatment_intent()
                        case SubjectSelectionCriteriaKey.FOBT_PREVALENT_INCIDENT_STATUS:
                            self._add_criteria_fobt_prevalent_incident_status()
                        case SubjectSelectionCriteriaKey.NOTIFY_QUEUED_MESSAGE_STATUS:
                            self._add_criteria_notify_queued_message_status()
                        case SubjectSelectionCriteriaKey.NOTIFY_ARCHIVED_MESSAGE_STATUS:
                            self._add_criteria_notify_archived_message_status()
                        case SubjectSelectionCriteriaKey.HAS_PREVIOUSLY_HAD_CANCER:
                            self._add_criteria_has_previously_had_cancer()
                        case SubjectSelectionCriteriaKey.DEMOGRAPHICS_TEMPORARY_ADDRESS:
                            self._add_criteria_has_temporary_address()
                        case _:
                            raise SelectionBuilderException(
                                f"Invalid subject selection criteria key: {self.criteria_key_name}"
                            )

                except Exception:
                    raise SelectionBuilderException(
                        f"Invalid subject selection criteria key: {self.criteria_key_name}"
                    )

    def _get_criteria_has_not_comparator(self, original_criteria_value: str) -> bool:
        return original_criteria_value.startswith("NOT:")

    def _get_criteria_value(self, original_criteria_value: str) -> str:
        if self.criteria_has_not_modifier:
            return original_criteria_value[4:].strip()
        else:
            return original_criteria_value

    def _get_criteria_comparator(self) -> str:
        if self.criteria_has_not_modifier:
            return " != "
        else:
            return " = "

    def _force_not_modifier_is_invalid_for_criteria_value(self) -> None:
        if self.criteria_has_not_modifier:
            raise ValueError(
                f"The 'NOT:' qualifier cannot be used with criteria key: {self.criteria_key_name}, value: {self.criteria_value}"
            )

    def _check_if_more_than_one_criteria_value_is_valid_for_criteria_key(self) -> None:
        if self.criteria_key is None:
            raise ValueError(f"criteria_key: {self.criteria_key} is None")
        if (
            not self.criteria_key.allow_more_than_one_value
            and self.criteria_value_count > 1
        ):
            raise ValueError(
                f"It is only valid to enter one selection value for criteria key: {self.criteria_key_name}"
            )

    def _check_if_not_modifier_is_valid_for_criteria_key(self) -> None:
        if self.criteria_key is None:
            raise ValueError("criteria_key is None")
        if not self.criteria_key.allow_not_modifier and self.criteria_has_not_modifier:
            raise ValueError(
                f"The 'NOT:' qualifier cannot be used with criteria key: {self.criteria_key_name}"
            )

    def _add_criteria_nhs_number(self) -> None:
        self.sql_where.append(" c.nhs_number = ':nhs_number' ")
        self.bind_vars["nhs_number"] = self.criteria_value

    def _add_criteria_subject_age(self) -> None:
        if "y/d" in self.criteria_key_name and "/" in self.criteria_value:
            age_criteria = self.criteria_value.split("/")
            self.sql_where.append(" AND c.date_of_birth = ")
            self.sql_where.append(
                self._subtract_years_from_oracle_date("TRUNC(SYSDATE)", age_criteria[0])
            )
            self.sql_where.append(" - ")
            self.sql_where.append(age_criteria[1])
        else:
            self.sql_where.append(
                " AND FLOOR(MONTHS_BETWEEN(TRUNC(SYSDATE), c.date_of_birth)/12) "
            )
            if self.criteria_value[0] in "0123456789":
                self.sql_where.append("= ")
            self.sql_where.append(self.criteria_value)

    def _add_criteria_subject_lower_fobt_age(self) -> None:
        """
        Adds a SQL constraint that compares a subject's lower FOBT age eligibility
        using a comparator and a value (e.g. '>= 55' or '>= default').

        If value is 'default', it's replaced with a national parameter lookup:
        pkg_parameters.f_get_national_param_val(10)
        """
        try:
            value = self.criteria_value
            comparator = self.criteria_comparator

            if value.lower() == "default":
                value = "pkg_parameters.f_get_national_param_val (10)"

            self.sql_where.append(
                f"AND pkg_bcss_common.f_get_ss_lower_age_limit (ss.screening_subject_id) "
                f"{comparator} {value}"
            )
        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_subject_lower_lynch_age(self) -> None:
        """
        Adds a SQL constraint for Lynch syndrome lower-age eligibility.

        If value is 'default', it's replaced with '35'.
        Uses comparator to build the WHERE clause.
        """
        try:
            value = self.criteria_value
            comparator = self.criteria_comparator

            if value.lower() == "default":
                value = "35"

            self.sql_where.append(
                f"AND pkg_bcss_common.f_get_lynch_lower_age_limit (ss.screening_subject_id) "
                f"{comparator} {value}"
            )
        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_latest_episode_type(self) -> None:
        """
        Adds a SQL condition that restricts subjects based on the episode_type_id of their latest episode.

        Translates a human-readable episode type string into an internal numeric ID.
        """
        try:
            value = self.criteria_value.lower()
            comparator = self.criteria_comparator

            # Simulate EpisodeType enum mapping
            episode_type_map = {
                "referral": 1,
                "invitation": 2,
                "test_kit_sent": 3,
                "reminder": 4,
                "episode_end": 5,
                # Add more mappings as needed
            }

            if value not in episode_type_map:
                raise ValueError(f"Unknown episode type: {value}")

            episode_type_id = episode_type_map[value]

            # Simulate the required join (docs only—no real SQL execution here)
            # In real builder this would ensure join to 'latest_episode' alias (ep)
            self.sql_where.append(
                f"AND ep.episode_type_id {comparator} {episode_type_id}"
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_latest_episode_sub_type(self) -> None:
        """
        Adds a SQL condition that filters based on the episode_subtype_id of a subject's latest episode.

        Translates a human-readable episode sub-type string into an internal numeric ID.
        """
        try:
            value = self.criteria_value.lower()
            comparator = self.criteria_comparator

            # Simulated EpisodeSubType enum mapping
            episode_subtype_map = {
                "routine screening": 10,
                "urgent referral": 11,
                "pre-assessment": 12,
                "follow-up": 13,
                "surveillance": 14,
                # Add more mappings as needed
            }

            if value not in episode_subtype_map:
                raise ValueError(f"Unknown episode sub-type: {value}")

            episode_subtype_id = episode_subtype_map[value]

            # Add SQL condition using the mapped ID
            self.sql_where.append(
                f"AND ep.episode_subtype_id {comparator} {episode_subtype_id}"
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_latest_episode_status(self) -> None:
        """
        Adds a SQL condition that filters based on the episode_status_id of a subject's latest episode.

        Translates a human-readable episode status into an internal numeric ID.
        """
        try:
            value = self.criteria_value.lower()
            comparator = self.criteria_comparator

            # Simulated EpisodeStatusType mapping
            episode_status_map = {
                "active": 100,
                "completed": 101,
                "pending": 102,
                "cancelled": 103,
                "invalid": 104,
                # Add actual mappings as needed
            }

            if value not in episode_status_map:
                raise ValueError(f"Unknown episode status: {value}")

            episode_status_id = episode_status_map[value]

            self.sql_where.append(
                f"AND ep.episode_status_id {comparator} {episode_status_id}"
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_latest_episode_status_reason(self) -> None:
        """
        Adds a SQL condition that filters based on the episode_status_reason_id of the subject's latest episode.

        Allows for explicit mapping or handling of NULL where no status reason is recorded.
        """
        try:
            value = self.criteria_value.lower()

            # Simulated EpisodeStatusReasonType enum
            episode_status_reason_map = {
                "completed screening": 200,
                "no longer eligible": 201,
                "deceased": 202,
                "moved away": 203,
                "null": None,  # Special case to represent SQL IS NULL
                # Extend as needed
            }

            if value not in episode_status_reason_map:
                raise ValueError(f"Unknown episode status reason: {value}")

            status_reason_id = episode_status_reason_map[value]

            if status_reason_id is None:
                self.sql_where.append("AND ep.episode_status_reason_id IS NULL")
            else:
                comparator = self.criteria_comparator
                self.sql_where.append(
                    f"AND ep.episode_status_reason_id {comparator} {status_reason_id}"
                )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_latest_episode_recall_calc_method(self) -> None:
        """
        Adds a SQL condition filtering on recall_calculation_method_id from the latest episode.

        Handles mapped descriptions or nulls for closed episodes with no recall method.
        """
        try:
            value = self.criteria_value.lower()

            # Simulated enum-like mapping
            recall_calc_method_map = {
                "standard": 300,
                "accelerated": 301,
                "paused": 302,
                "null": None,  # For episodes with no recall method
                # Extend with real values as needed
            }

            if value not in recall_calc_method_map:
                raise ValueError(f"Unknown recall calculation method: {value}")

            method_id = recall_calc_method_map[value]

            if method_id is None:
                self.sql_where.append("AND ep.recall_calculation_method_id IS NULL")
            else:
                comparator = self.criteria_comparator
                self.sql_where.append(
                    f"AND ep.recall_calculation_method_id {comparator} {method_id}"
                )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_latest_episode_recall_episode_type(self) -> None:
        """
        Adds a filter for recall_episode_type_id based on the type of episode that triggered the recall.
        Supports mapped descriptions and IS NULL.
        """
        try:
            value = self.criteria_value.lower()

            recall_episode_type_map = {
                "referral": 1,
                "invitation": 2,
                "reminder": 3,
                "episode_end": 4,
                "null": None,
            }

            if value not in recall_episode_type_map:
                raise ValueError(f"Unknown recall episode type: {value}")

            type_id = recall_episode_type_map[value]

            if type_id is None:
                self.sql_where.append("AND ep.recall_episode_type_id IS NULL")
            else:
                comparator = self.criteria_comparator
                self.sql_where.append(
                    f"AND ep.recall_episode_type_id {comparator} {type_id}"
                )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_latest_episode_recall_surveillance_type(self) -> None:
        """
        Adds a filter for recall_polyp_surv_type_id based on the type of surveillance used during recall.
        Supports mapped descriptions and null values.
        """
        try:
            value = self.criteria_value.lower()

            recall_surv_type_map = {
                "routine": 500,
                "enhanced": 501,
                "annual": 502,
                "null": None,
            }

            if value not in recall_surv_type_map:
                raise ValueError(f"Unknown recall surveillance type: {value}")

            surv_id = recall_surv_type_map[value]

            if surv_id is None:
                self.sql_where.append("AND ep.recall_polyp_surv_type_id IS NULL")
            else:
                comparator = self.criteria_comparator
                self.sql_where.append(
                    f"AND ep.recall_polyp_surv_type_id {comparator} {surv_id}"
                )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_event_status(self, column_name: str) -> None:
        """
        Filters based on the event status code found in the specified column.

        Extracts a code from the criteria value (e.g. "ES01 - Invitation Received"),
        and injects its corresponding event_status_id into SQL.
        """
        try:
            # Extract the code (e.g. "ES01") from the first word
            code = self.criteria_value.strip().split()[0].upper()
            comparator = self.criteria_comparator

            # Simulated EventStatusType registry
            event_status_code_map = {
                "ES01": 600,
                "ES02": 601,
                "ES03": 602,
                "ES99": 699,
                # ...update with real mappings
            }

            if code not in event_status_code_map:
                raise ValueError(f"Unknown event status code: {code}")

            event_status_id = event_status_code_map[code]
            self.sql_where.append(f"AND {column_name} {comparator} {event_status_id}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_event_code_in_episode(self, event_is_included: bool) -> None:
        """
        Adds a filter checking whether the given event code appears in the latest episode's event list.
        Uses EXISTS or NOT EXISTS depending on the flag.
        """
        try:
            code = self.criteria_value.strip().split()[0].upper()

            # Simulated EventCodeType registry
            event_code_map = {
                "EV101": 701,
                "EV102": 702,
                "EV900": 799,
                # ...extend with real mappings
            }

            if code not in event_code_map:
                raise ValueError(f"Unknown event code: {code}")

            event_code_id = event_code_map[code]

            exists_clause = "EXISTS" if event_is_included else "NOT EXISTS"

            self.sql_where.append(
                f"""AND {exists_clause} (
        SELECT 'evc'
        FROM ep_events_t evc
        WHERE evc.event_code_id = {event_code_id}
        AND evc.subject_epis_id = ep.subject_epis_id
    )"""
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_event_status_in_episode(self, event_is_included: bool) -> None:
        """
        Adds a filter that checks whether the specified event status is present
        in the latest episode. Uses EXISTS or NOT EXISTS depending on the flag.
        """
        try:
            code = self.criteria_value.strip().split()[0].upper()

            # Simulated EventStatusType code-to-ID map
            event_status_code_map = {
                "ES01": 600,
                "ES02": 601,
                "ES03": 602,
                "ES99": 699,
                # Extend with actual mappings
            }

            if code not in event_status_code_map:
                raise ValueError(f"Unknown event status code: {code}")

            status_id = event_status_code_map[code]
            exists_clause = "EXISTS" if event_is_included else "NOT EXISTS"

            self.sql_where.append(
                f"""AND {exists_clause} (
        SELECT 'ev'
        FROM ep_events_t ev
        WHERE ev.event_status_id = {status_id}
        AND ev.subject_epis_id = ep.subject_epis_id
    )"""
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_latest_episode_kit_class(self) -> None:
        """
        Filters based on the test kit class of the latest episode using a nested IN clause.
        Resolves from symbolic class name (e.g. 'FIT') to test class ID.
        """
        try:
            value = self.criteria_value.upper()
            comparator = self.criteria_comparator

            # Simulated TestKitClass enum
            test_kit_class_map = {
                "GFOBT": 800,
                "FIT": 801,
                # Extend as needed
            }

            if value not in test_kit_class_map:
                raise ValueError(f"Unknown test kit class: {value}")

            kit_class_id = test_kit_class_map[value]

            self.sql_where.append(
                f"""AND ep.tk_type_id IN (
        SELECT tkt.tk_type_id
        FROM tk_type_t tkt
        WHERE tkt.tk_test_class_id {comparator} {kit_class_id}
    )"""
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_has_significant_kit_result(self) -> None:
        """
        Adds a filter to check if the latest episode has a significant kit result.
        Significant values: NORMAL, ABNORMAL, WEAK_POSITIVE.
        Accepts criteriaValue: "yes" or "no".
        """
        try:
            value = self.criteria_value.strip().lower()

            if value == "yes":
                exists_clause = "EXISTS"
            elif value == "no":
                exists_clause = "NOT EXISTS"
            else:
                raise ValueError(
                    f"Unknown response for significant kit result: {value}"
                )

            self.sql_where.append(
                f"""AND {exists_clause} (
        SELECT 'tks'
        FROM tk_items_t tks
        WHERE tks.screening_subject_id = ss.screening_subject_id
        AND tks.logged_subject_epis_id = ep.subject_epis_id
        AND tks.test_results IN ('NORMAL', 'ABNORMAL', 'WEAK_POSITIVE')
    )"""
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_has_referral_date(self) -> None:
        """
        Adds a filter for the presence or timing of referral_date in the latest episode.
        Accepts values: yes, no, past, more_than_28_days_ago, within_the_last_28_days.
        """
        try:
            value = self.criteria_value.strip().lower()

            clause_map = {
                "yes": "ep.referral_date IS NOT NULL",
                "no": "ep.referral_date IS NULL",
                "past": "ep.referral_date < trunc(sysdate)",
                "more_than_28_days_ago": "(ep.referral_date + 28) < trunc(sysdate)",
                "within_the_last_28_days": "(ep.referral_date + 28) > trunc(sysdate)",
            }

            if value not in clause_map:
                raise ValueError(f"Unknown referral date condition: {value}")

            self.sql_where.append(f"AND {clause_map[value]}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_has_diagnosis_date(self) -> None:
        """
        Adds a filter to check if the latest episode has a diagnosis_date set,
        and whether it matches the subject's date of death if specified.
        Accepts values: yes, no, yes_date_of_death
        """
        try:
            value = self.criteria_value.strip().lower()

            if value == "yes":
                self.sql_where.append("AND ep.diagnosis_date IS NOT NULL")
            elif value == "no":
                self.sql_where.append("AND ep.diagnosis_date IS NULL")
            elif value == "yes_date_of_death":
                self.sql_where.append("AND ep.diagnosis_date IS NOT NULL")
                self.sql_where.append("AND ep.diagnosis_date = c.date_of_death")
            else:
                raise ValueError(f"Unknown condition for diagnosis date: {value}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_has_diagnostic_test(self, latest_episode_only: bool) -> None:
        """
        Adds a filter checking if the subject has (or doesn't have) a diagnostic test.
        Void tests are excluded. The `latest_episode_only` flag limits scope to the latest episode.
        Accepts criteria value: "yes" or "no".
        """
        try:
            value = self.criteria_value.strip().lower()

            if value == "no":
                prefix = "AND NOT "
            elif value == "yes":
                prefix = "AND "
            else:
                raise ValueError(f"Invalid diagnostic test condition: {value}")

            subquery = [
                "EXISTS (",
                "  SELECT 1",
                "  FROM external_tests_t lesxt",
                "  WHERE lesxt.screening_subject_id = ss.screening_subject_id",
                "    AND lesxt.void = 'N'",
            ]
            if latest_episode_only:
                subquery.append("    AND lesxt.subject_epis_id = ep.subject_epis_id")
            subquery.append(")")

            self.sql_where.append(prefix + "\n".join(subquery))

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_diagnosis_date_reason(self) -> None:
        """
        Adds a filter on ep.diagnosis_date_reason_id.
        Supports symbolic matches (via ID) and special values: NULL, NOT_NULL.
        """
        try:
            value = self.criteria_value.strip().lower()
            comparator = self.criteria_comparator

            # Simulated DiagnosisDateReasonType
            reason_map = {
                "patient informed": 900,
                "clinician notified": 901,
                "screening outcome": 902,
                "null": "NULL",
                "not_null": "NOT NULL",
                # Extend as needed
            }

            if value not in reason_map:
                raise ValueError(f"Unknown diagnosis date reason: {value}")

            resolved = reason_map[value]
            if resolved in ("NULL", "NOT NULL"):
                self.sql_where.append(f"AND ep.diagnosis_date_reason_id IS {resolved}")
            else:
                self.sql_where.append(
                    f"AND ep.diagnosis_date_reason_id {comparator} {resolved}"
                )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_latest_episode_completed_satisfactorily(self) -> None:
        """
        Adds a filter to check whether the latest episode completed satisfactorily or not.
        Checks for presence/absence of interruption events or disqualifying result codes.
        """
        try:
            value = self.criteria_value.strip().lower()

            if value == "yes":
                exists_prefix = "AND NOT EXISTS"
            elif value == "no":
                exists_prefix = "AND EXISTS"
            else:
                raise ValueError(f"Invalid completion flag: {value}")

            self.sql_where.append(
                f"""{exists_prefix} (
        SELECT 'ev'
        FROM ep_events_t ev
        WHERE ev.subject_epis_id = ep.subject_epis_id
        AND (
            ev.event_status_id IN (11237, 20188)
            OR ep.episode_result_id IN (605002, 605003, 605004, 605007)
        )
    )"""
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_has_diagnostic_test_containing_polyp(self) -> None:
        """
        Adds logic to filter based on whether a diagnostic test has a recorded polyp.
        'Yes' joins polyp tables; 'No' checks for absence via NOT EXISTS.
        """
        try:
            value = self.criteria_value.strip().lower()

            if value == "yes":
                self.sql_from.append(
                    "INNER JOIN external_tests_t ext ON ep.subject_epis_id = ext.subject_epis_id\n"
                    "INNER JOIN ds_colonoscopy_t dsc ON ext.ext_test_id = dsc.ext_test_id\n"
                    "INNER JOIN ds_polyp_t dst ON ext.ext_test_id = dst.ext_test_id"
                )
                self.sql_where.append(
                    "AND ext.void = 'N'\n" "AND dst.deleted_flag = 'N'"
                )
            elif value == "no":
                self.sql_where.append(
                    """AND NOT EXISTS (
        SELECT 'ext'
        FROM external_tests_t ext
        LEFT JOIN ds_polyp_t dst ON ext.ext_test_id = dst.ext_test_id
        WHERE ext.subject_epis_id = ep.subject_epis_id
    )"""
                )
            else:
                raise ValueError(
                    f"Unknown value for diagnostic test containing polyp: {value}"
                )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_subject_has_unlogged_kits(self) -> None:
        """
        Adds a filter to check for unlogged kits across subject history,
        or scoped to the latest episode. Accepts:
        - "yes"
        - "yes_latest_episode"
        - "no"
        """
        try:
            value = self.criteria_value.strip().lower()

            if value in ("yes", "yes_latest_episode"):
                prefix = "AND EXISTS"
            elif value == "no":
                prefix = "AND NOT EXISTS"
            else:
                raise ValueError(f"Unknown value for unlogged kits: {value}")

            subquery = [
                f"{prefix} (",
                "  SELECT 'tku'",
                "  FROM tk_items_t tku",
                "  WHERE tku.screening_subject_id = ss.screening_subject_id",
            ]

            if value == "yes_latest_episode":
                self._add_join_to_latest_episode()
                subquery.append("    AND tku.subject_epis_id = ep.subject_epis_id")

            subquery.append("    AND tku.logged_in_flag = 'N'")
            subquery.append(")")

            self.sql_where.append("\n".join(subquery))

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_subject_has_logged_fit_kits(self) -> None:
        """
        Adds a filter to check if the subject has logged FIT kits (tk_type_id > 1 and logged_in_flag = 'Y').
        Accepts values: 'yes' or 'no'.
        """
        try:
            value = self.criteria_value.strip().lower()

            if value == "yes":
                prefix = "AND EXISTS"
            elif value == "no":
                prefix = "AND NOT EXISTS"
            else:
                raise ValueError(f"Invalid value for logged FIT kits: {value}")

            self.sql_where.append(
                f"""{prefix} (
    SELECT 'tkl'
    FROM tk_items_t tkl
    WHERE tkl.screening_subject_id = ss.screening_subject_id
        AND tkl.tk_type_id > 1
        AND tkl.logged_in_flag = 'Y'
    )"""
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_subject_has_kit_notes(self) -> None:
        """
        Filters subjects based on presence of active kit-related notes.
        Accepts values: 'yes' or 'no'.
        """
        try:
            value = self.criteria_value.strip().lower()

            if value == "yes":
                prefix = "AND EXISTS"
            elif value == "no":
                prefix = "AND NOT EXISTS"
            else:
                raise ValueError(f"Invalid value for kit notes: {value}")

            self.sql_where.append(
                f"""{prefix} (
        SELECT 1
        FROM supporting_notes_t sn
        WHERE sn.screening_subject_id = ss.screening_subject_id
            AND (
            sn.type_id = '308015'
            OR sn.promote_pio_id IS NOT NULL
            )
            AND sn.status_id = 4100
        )
        AND ss.number_of_invitations > 0
        AND rownum = 1"""
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_subject_has_lynch_diagnosis(self) -> None:
        """
        Adds a filter to check if a subject has an active Lynch diagnosis.
        Accepts:
            - "yes" → subject must have active diagnosis ('Y')
            - "no"  → subject must not have active diagnosis ('N')
        """
        try:
            value = self.criteria_value.strip().lower()

            if value == "yes":
                self.sql_where.append(
                    "AND pkg_lynch.f_subject_has_active_lynch_diagnosis (ss.screening_subject_id) = 'Y'"
                )
            elif value == "no":
                self.sql_where.append(
                    "AND pkg_lynch.f_subject_has_active_lynch_diagnosis (ss.screening_subject_id) = 'N'"
                )
            else:
                raise ValueError(f"Invalid value for Lynch diagnosis: {value}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_join_to_test_kits(self) -> None:
        """
        Adds joins to the tk_items_t table based on test kit selection criteria.
        Handles whether any kit is considered, or a specific one from the latest episode.

        Expected values (case-insensitive):
            - "any_kit_in_any_episode"
            - "only_kit_issued_in_latest_episode"
            - "first_kit_issued_in_latest_episode"
            - "latest_kit_issued_in_latest_episode"
            - "only_kit_logged_in_latest_episode"
            - "first_kit_logged_in_latest_episode"
            - "latest_kit_logged_in_latest_episode"
        """
        try:
            value = self.criteria_value.strip().lower()
            tk_alias = "tk"  # You can extend this if you need multiple joins

            # Base join for all paths (only FIT kits)
            self.sql_from.append(
                f"INNER JOIN tk_items_t {tk_alias} ON {tk_alias}.screening_subject_id = ss.screening_subject_id "
                f"AND {tk_alias}.tk_type_id > 1"
            )

            if value == "any_kit_in_any_episode":
                return

            if "issued_in_latest_episode" in value:
                self._add_join_to_latest_episode()
                self.sql_from.append(
                    f"AND {tk_alias}.subject_epis_id = ep.subject_epis_id "
                    f"AND NOT EXISTS ("
                    f" SELECT 'tko1' FROM tk_items_t tko "
                    f" WHERE tko.screening_subject_id = ss.screening_subject_id "
                    f" AND tko.subject_epis_id = ep.subject_epis_id "
                )
                if value.startswith("only"):
                    comparator = "!="
                elif value.startswith("first"):
                    comparator = "<"
                else:  # latest
                    comparator = ">"
                self.sql_from.append(f" AND tko.kitid {comparator} {tk_alias}.kitid)")

            elif "logged_in_latest_episode" in value:
                self._add_join_to_latest_episode()
                self.sql_from.append(
                    f"AND {tk_alias}.logged_subject_epis_id = ep.subject_epis_id "
                    f"AND NOT EXISTS ("
                    f" SELECT 'tko2' FROM tk_items_t tko "
                    f" WHERE tko.screening_subject_id = ss.screening_subject_id "
                    f" AND tko.logged_subject_epis_id = ep.subject_epis_id"
                )
                if value.startswith("only"):
                    self.sql_from.append(f" AND tko.kitid != {tk_alias}.kitid")
                elif value.startswith("first"):
                    self.sql_from.append(
                        f" AND tko.logged_in_on < {tk_alias}.logged_in_on"
                    )
                else:  # latest
                    self.sql_from.append(
                        f" AND tko.logged_in_on > {tk_alias}.logged_in_on"
                    )
                self.sql_from.append(")")

            else:
                raise ValueError(f"Invalid test kit selection value: {value}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_kit_has_been_read(self) -> None:
        """
        Filters test kits based on whether they have been read.
        Requires prior join to tk_items_t as alias 'tk' (via WHICH_TEST_KIT).

        Accepts values:
            - "yes" → reading_flag = 'Y'
            - "no"  → reading_flag = 'N'
        """
        try:
            value = self.criteria_value.strip().lower()

            if value == "yes":
                self.sql_where.append("AND tk.reading_flag = 'Y'")
            elif value == "no":
                self.sql_where.append("AND tk.reading_flag = 'N'")
            else:
                raise ValueError(f"Invalid value for kit has been read: {value}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_kit_result(self) -> None:
        """
        Filters based on the result associated with the selected test kit.
        Requires prior join to tk_items_t as alias 'tk' (via WHICH_TEST_KIT).
        Uses comparator and uppercase value.
        """
        try:
            comparator = self.criteria_comparator
            value = self.criteria_value.strip().upper()
            self.sql_where.append(f"AND tk.test_results {comparator} '{value}'")
        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_kit_has_analyser_result_code(self) -> None:
        """
        Filters kits based on whether they have an analyser error code.
        Requires prior join to tk_items_t as alias 'tk' (via WHICH_TEST_KIT).

        Accepts values:
            - "yes" → analyser_error_code IS NOT NULL
            - "no"  → analyser_error_code IS NULL
        """
        try:
            value = self.criteria_value.strip().lower()

            if value == "yes":
                self.sql_where.append("AND tk.analyser_error_code IS NOT NULL")
            elif value == "no":
                self.sql_where.append("AND tk.analyser_error_code IS NULL")
            else:
                raise ValueError(
                    f"Invalid value for analyser result code presence: {value}"
                )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_join_to_appointments(self) -> None:
        """
        Adds join to appointment_t table based on appointment selection strategy.
        Requires prior join to latest episode (ep). Aliases the appointment table as 'ap'.

        Accepts values:
            - "any_appointment_in_latest_episode"
            - "latest_appointment_in_latest_episode"
            - "earlier_appointment_in_latest_episode"
            - "later_appointment_in_latest_episode"
        """
        try:
            value = self.criteria_value.strip().lower()
            ap_alias = "ap"
            apr_alias = "ap_prev"  # Simulated prior alias for test support

            self._add_join_to_latest_episode()
            self.sql_from.append(
                f"INNER JOIN appointment_t {ap_alias} ON {ap_alias}.subject_epis_id = ep.subject_epis_id"
            )

            if value == "any_appointment_in_latest_episode":
                return
            elif value == "latest_appointment_in_latest_episode":
                self.sql_from.append(
                    f"AND {ap_alias}.appointment_id = ("
                    f" SELECT MAX(apx.appointment_id)"
                    f" FROM appointment_t apx"
                    f" WHERE apx.subject_epis_id = ep.subject_epis_id"
                    f" AND apx.void = 'N')"
                )
            elif value == "earlier_appointment_in_latest_episode":
                self.sql_from.append(
                    f"AND {ap_alias}.appointment_id < {apr_alias}.appointment_id"
                )
            elif value == "later_appointment_in_latest_episode":
                self.sql_from.append(
                    f"AND {ap_alias}.appointment_id > {apr_alias}.appointment_id"
                )
            else:
                raise ValueError(f"Invalid appointment selection value: {value}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_appointment_type(self) -> None:
        """
        Filters appointments by slot type (e.g. clinic, phone).
        Requires prior join to appointment_t as alias 'ap' (via WHICH_APPOINTMENT).

        Uses comparator and resolves slot type label to ID via AppointmentSlotType.
        """
        try:
            comparator = self.criteria_comparator
            value = self.criteria_value.strip()
            slot_type_id = AppointmentSlotType.get_id(value)

            self.sql_where.append(
                f"AND ap.appointment_slot_type_id {comparator} {slot_type_id}"
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_appointment_status(self) -> None:
        """
        Filters appointments by status (e.g. booked, attended).
        Requires prior join to appointment_t as alias 'ap'.

        Uses comparator and resolves status label to ID via AppointmentStatusType.
        """
        try:
            comparator = self.criteria_comparator
            value = self.criteria_value.strip()
            status_id = AppointmentStatusType.get_id(value)

            self.sql_where.append(
                f"AND ap.appointment_status_id {comparator} {status_id}"
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    # ------------------------------------------------------------------------
    # 🧪 Diagnostic Test Selection & Join Logic
    # ------------------------------------------------------------------------

    def _add_join_to_diagnostic_tests(self) -> None:
        try:
            which = WhichDiagnosticTest.from_description(self.criteria_value)
            idx = getattr(self, "criteria_index", 0)
            xt = f"xt{idx}"
            xtp = f"xt{idx - 1}"

            self.sql_from.append(
                f"INNER JOIN external_tests_t {xt} ON {xt}.screening_subject_id = ss.screening_subject_id"
            )

            if which == WhichDiagnosticTest.ANY_TEST_IN_ANY_EPISODE:
                return

            self._add_join_to_latest_episode()

            handlers = {
                WhichDiagnosticTest.ANY_TEST_IN_LATEST_EPISODE: self._handle_any_test_in_latest_episode,
                WhichDiagnosticTest.ONLY_TEST_IN_LATEST_EPISODE: self._handle_only_test_in_latest_episode,
                WhichDiagnosticTest.ONLY_NOT_VOID_TEST_IN_LATEST_EPISODE: self._handle_only_test_in_latest_episode,
                WhichDiagnosticTest.LATEST_TEST_IN_LATEST_EPISODE: self._handle_latest_test_in_latest_episode,
                WhichDiagnosticTest.LATEST_NOT_VOID_TEST_IN_LATEST_EPISODE: self._handle_latest_test_in_latest_episode,
                WhichDiagnosticTest.EARLIEST_NOT_VOID_TEST_IN_LATEST_EPISODE: self._handle_earliest_test_in_latest_episode,
                WhichDiagnosticTest.EARLIER_TEST_IN_LATEST_EPISODE: self._handle_earlier_or_later_test,
                WhichDiagnosticTest.LATER_TEST_IN_LATEST_EPISODE: self._handle_earlier_or_later_test,
            }

            if which in handlers:
                handlers[which](which, xt, xtp)
            else:
                raise ValueError(f"Unsupported diagnostic test type: {which}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _handle_any_test_in_latest_episode(self, which, xt, _):
        """Helper method for diagnostic test filtering"""

        self.sql_from.append(f"AND {xt}.subject_epis_id = ep.subject_epis_id")

    def _handle_only_test_in_latest_episode(self, which, xt, _):
        """Helper method for diagnostic test filtering"""
        self.sql_from.append(f"AND {xt}.subject_epis_id = ep.subject_epis_id")
        if which == WhichDiagnosticTest.ONLY_NOT_VOID_TEST_IN_LATEST_EPISODE:
            self.sql_from.append(f"AND {xt}.void = 'N'")
        self.sql_from.append(
            f"""AND NOT EXISTS (
        SELECT 'xto' FROM external_tests_t xto
        WHERE xto.screening_subject_id = ss.screening_subject_id
        {'AND xto.void = \'N\'' if which == WhichDiagnosticTest.ONLY_NOT_VOID_TEST_IN_LATEST_EPISODE else ''}
        AND xto.subject_epis_id = ep.subject_epis_id
        AND xto.ext_test_id != {xt}.ext_test_id )"""
        )

    def _handle_latest_test_in_latest_episode(self, which, xt, _):
        """Helper method for diagnostic test filtering"""
        self.sql_from.append(
            f"""AND {xt}.ext_test_id = (
        SELECT MAX(xtx.ext_test_id) FROM external_tests_t xtx
        WHERE xtx.screening_subject_id = ss.screening_subject_id
        {'AND xtx.void = \'N\'' if which == WhichDiagnosticTest.LATEST_NOT_VOID_TEST_IN_LATEST_EPISODE else ''}
        AND xtx.subject_epis_id = ep.subject_epis_id )"""
        )

    def _handle_earliest_test_in_latest_episode(self, which, xt, _):
        """Helper method for diagnostic test filtering"""
        self.sql_from.append(
            f"""AND {xt}.ext_test_id = (
        SELECT MIN(xtn.ext_test_id) FROM external_tests_t xtn
        WHERE xtn.screening_subject_id = ss.screening_subject_id
        AND xtn.void = 'N'
        AND xtn.subject_epis_id = ep.subject_epis_id )"""
        )

    def _handle_earlier_or_later_test(self, which, xt, xtp):
        """Helper method for diagnostic test filtering"""
        if getattr(self, "criteria_index", 0) == 0:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)
        comparator = (
            "<" if which == WhichDiagnosticTest.EARLIER_TEST_IN_LATEST_EPISODE else ">"
        )
        self.sql_from.append(f"AND {xt}.ext_test_id {comparator} {xtp}.ext_test_id")

    def _add_criteria_diagnostic_test_type(self, proposed_or_confirmed: str) -> None:
        """
        Filters diagnostic tests by type—proposed or confirmed.
        Requires prior join to external_tests_t (xt aliasing assumed).
        """
        try:
            idx = getattr(self, "criteria_index", 0)
            xt = f"xt{idx}"

            if proposed_or_confirmed == "proposed":
                column = f"{xt}.proposed_type_id"
            elif proposed_or_confirmed == "confirmed":
                column = f"{xt}.confirmed_type_id"
            else:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )

            self.sql_where.append(f"AND {column} ")

            value = self.criteria_value.strip().lower()
            if value == "null":
                self.sql_where.append("IS NULL")
            elif value == "not null":
                self.sql_where.append("IS NOT NULL")
            else:
                comparator = self.criteria_comparator
                type_id = DiagnosticTestType.get_valid_value_id(self.criteria_value)
                self.sql_where.append(f"{comparator} {type_id}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_diagnostic_test_is_void(self) -> None:
        """
        Adds WHERE clause to check whether diagnostic test is voided ('Y' or 'N').
        Requires prior join to external_tests_t using alias xtN.
        """
        try:
            idx = getattr(self, "criteria_index", 0)
            xt = f"xt{idx}"
            value = DiagnosticTestIsVoid.from_description(self.criteria_value)

            if value == DiagnosticTestIsVoid.YES:
                self.sql_where.append(f"AND {xt}.void = 'Y'")
            elif value == DiagnosticTestIsVoid.NO:
                self.sql_where.append(f"AND {xt}.void = 'N'")
            else:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_diagnostic_test_has_result(self) -> None:
        """
        Adds WHERE clause to check whether a diagnostic test has a result (IS NULL / NOT NULL / = result_id).
        """
        try:
            idx = getattr(self, "criteria_index", 0)
            xt = f"xt{idx}"
            value = self.criteria_value.strip().lower()
            result = DiagnosticTestHasResult.from_description(value)

            self.sql_where.append(f"AND {xt}.result_id ")

            if result == DiagnosticTestHasResult.YES:
                self.sql_where.append("IS NOT NULL")
            elif result == DiagnosticTestHasResult.NO:
                self.sql_where.append("IS NULL")
            else:
                result_id = DiagnosticTestHasResult.get_id(value)
                self.sql_where.append(f"= {result_id}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_diagnostic_test_has_outcome_of_result(self) -> None:
        """
        Adds WHERE clause filtering on whether the diagnostic test has an outcome-of-result.
        """
        try:
            idx = getattr(self, "criteria_index", 0)
            xt = f"xt{idx}"
            value = self.criteria_value.strip().lower()
            outcome = DiagnosticTestHasOutcomeOfResult.from_description(value)

            self.sql_where.append(f"AND {xt}.outcome_of_result_id ")

            if outcome == DiagnosticTestHasOutcomeOfResult.YES:
                self.sql_where.append("IS NOT NULL")
            elif outcome == DiagnosticTestHasOutcomeOfResult.NO:
                self.sql_where.append("IS NULL")
            else:
                outcome_id = DiagnosticTestHasOutcomeOfResult.get_id(value)
                self.sql_where.append(f"= {outcome_id}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_diagnostic_test_intended_extent(self) -> None:
        """
        Adds WHERE clause filtering diagnostic tests by intended_extent_id.
        Supports null checks and value comparisons.
        """
        try:
            idx = getattr(self, "criteria_index", 0)
            xt = f"xt{idx}"
            extent = IntendedExtentType.from_description(self.criteria_value)

            self.sql_where.append(f"AND {xt}.intended_extent_id ")

            if extent in (IntendedExtentType.NULL, IntendedExtentType.NOT_NULL):
                self.sql_where.append(
                    f"IS {IntendedExtentType.get_description(extent)}"
                )
            else:
                self.sql_where.append(
                    f"{self.criteria_comparator} {IntendedExtentType.get_id(self.criteria_value)}"
                )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_latest_episode_has_dataset(self) -> None:
        """
        Filters based on presence or completion status of a dataset in the latest episode.
        """
        try:
            self._add_join_to_latest_episode()

            dataset_info = self._dataset_source_for_criteria_key()
            dataset_table = dataset_info["table"]
            alias = dataset_info["alias"]

            clause = "AND EXISTS ( "
            value = self.criteria_value.strip().lower()
            status = LatestEpisodeHasDataset.from_description(value)
            filter_clause = ""

            if status == LatestEpisodeHasDataset.NO:
                clause = "AND NOT EXISTS ( "
            elif status == LatestEpisodeHasDataset.YES_INCOMPLETE:
                filter_clause = f"AND {alias}.dataset_completed_date IS NULL"
            elif status == LatestEpisodeHasDataset.YES_COMPLETE:
                filter_clause = f"AND {alias}.dataset_completed_date IS NOT NULL"
            elif status == LatestEpisodeHasDataset.PAST:
                filter_clause = (
                    f"AND TRUNC({alias}.dataset_completed_date) < TRUNC(SYSDATE)"
                )
            else:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )

            self.sql_where.append(
                "".join(
                    [
                        clause,
                        f"SELECT 1 FROM {dataset_table} {alias} ",
                        f"WHERE {alias}.episode_id = ep.subject_epis_id ",
                        f"AND {alias}.deleted_flag = 'N' ",
                        filter_clause,
                        ")",
                    ]
                )
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _dataset_source_for_criteria_key(self) -> dict:
        """
        Internal helper method.
        Maps LATEST_EPISODE_HAS_* criteria keys to their corresponding dataset tables and aliases.
        Used by _add_criteria_latest_episode_has_dataset().
        """
        key = self.criteria_key
        if key == SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_CANCER_AUDIT_DATASET:
            return {"table": "ds_cancer_audit_t", "alias": "cads"}
        if (
            key
            == SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_COLONOSCOPY_ASSESSMENT_DATASET
        ):
            return {"table": "ds_patient_assessment_t", "alias": "dspa"}
        if key == SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_MDT_DATASET:
            return {"table": "ds_mdt_t", "alias": "mdt"}
        raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    # ------------------------------------------------------------------------
    # 🧬 CADS Clinical Dataset Filters
    # ------------------------------------------------------------------------

    def _add_criteria_cads_asa_grade(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self.sql_where.append(
            f"AND cads.asa_grade_id = ASAGradeType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_staging_scans(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self._add_join_to_cancer_audit_dataset_staging_scan()
        self.sql_where.append(
            f"AND cads.staging_scans_done_id = YesNoType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_type_of_scan(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self._add_join_to_cancer_audit_dataset_staging_scan()
        self.sql_where.append(
            f"AND dcss.type_of_scan_id = ScanType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_metastases_present(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self.sql_where.append(
            f"AND cads.metastases_found_id = MetastasesPresentType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_metastases_location(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self._add_join_to_cancer_audit_dataset_metastasis()
        self.sql_where.append(
            f"AND dcm.location_of_metastasis_id = MetastasesLocationType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_metastases_other_location(self, other_location: str) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self._add_join_to_cancer_audit_dataset_metastasis()
        self.sql_where.append(
            f"AND dcm.other_location_of_metastasis = '{other_location}'"
        )

    def _add_criteria_cads_final_pre_treatment_t_category(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self.sql_where.append(
            f"AND cads.final_pre_treat_t_category_id = FinalPretreatmentTCategoryType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_final_pre_treatment_n_category(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self.sql_where.append(
            f"AND cads.final_pre_treat_n_category_id = FinalPretreatmentNCategoryType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_final_pre_treatment_m_category(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self.sql_where.append(
            f"AND cads.final_pre_treat_m_category_id = FinalPretreatmentMCategoryType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_treatment_received(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self.sql_where.append(
            f"AND cads.treatment_received_id = YesNoType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_reason_no_treatment_received(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self.sql_where.append(
            f"AND cads.reason_no_treatment_id = ReasonNoTreatmentReceivedType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_tumour_location(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self._add_join_to_cancer_audit_dataset_tumour()
        self.sql_where.append(
            f"AND dctu.location_id = LocationType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_tumour_height_of_tumour_above_anal_verge(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self._add_join_to_cancer_audit_dataset_tumour()
        self.sql_where.append(
            f"AND dctu.height_above_anal_verge = {self.criteria_value}"
        )

    def _add_criteria_cads_tumour_previously_excised_tumour(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self._add_join_to_cancer_audit_dataset_tumour()
        self.sql_where.append(
            f"AND dctu.recurrence_id = PreviouslyExcisedTumourType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_treatment_type(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self._add_join_to_cancer_audit_dataset_treatment()
        self.sql_where.append(
            f"AND dctr.treatment_category_id = TreatmentType.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_treatment_given(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self._add_join_to_cancer_audit_dataset_treatment()
        self.sql_where.append(
            f"AND dctr.treatment_procedure_id = TreatmentGiven.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_cads_cancer_treatment_intent(self) -> None:
        self._add_join_to_latest_episode()
        self._add_join_to_cancer_audit_dataset()
        self._add_join_to_cancer_audit_dataset_treatment()
        self.sql_where.append(
            f"AND dctr.treatment_intent_id = CancerTreatmentIntent.by_description_case_insensitive(self.criteria_value).id"
        )

    def _add_criteria_subject_hub_code(self, user: "User") -> None:
        hub_code = None
        try:
            hub_enum = SubjectHubCode.by_description(self.criteria_value.lower())
            if hub_enum in [SubjectHubCode.USER_HUB, SubjectHubCode.USER_ORGANISATION]:
                if (
                    user.organisation is None
                    or user.organisation.organisation_id is None
                ):
                    raise ValueError("User organisation or organisation_id is None")
                hub_code = user.organisation.organisation_id
            else:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )
        except Exception:
            # If not in the enum it must be an actual hub code
            hub_code = self.criteria_value

        self.sql_where.append(" AND c.hub_id ")
        self.sql_where.append(self.criteria_comparator)
        self.sql_where.append(" (")
        self.sql_where.append("   SELECT hub.org_id ")
        self.sql_where.append("   FROM org hub ")
        self.sql_where.append("   WHERE hub.org_code = ")
        self.sql_where.append(self.single_quoted(hub_code.upper()))
        self.sql_where.append(") ")

    def _add_criteria_subject_screening_centre_code(self, user: "User"):
        sc_code = None

        try:
            option = SubjectScreeningCentreCode.by_description(
                self.criteria_value.lower()
            )
            match option:
                case SubjectScreeningCentreCode.NONE | SubjectScreeningCentreCode.NULL:
                    self.sql_where.append(" AND c.responsible_sc_id IS NULL ")
                case SubjectScreeningCentreCode.NOT_NULL:
                    self.sql_where.append(" AND c.responsible_sc_id IS NOT NULL ")
                case (
                    SubjectScreeningCentreCode.USER_SCREENING_CENTRE
                    | SubjectScreeningCentreCode.USER_SC
                    | SubjectScreeningCentreCode.USER_ORGANISATION
                ):
                    if (
                        user.organisation is None
                        or user.organisation.organisation_id is None
                    ):
                        raise ValueError("User organisation or organisation_id is None")
                    sc_code = user.organisation.organisation_id
                case _:
                    raise SelectionBuilderException(
                        self.criteria_key_name, self.criteria_value
                    )
        except SelectionBuilderException as ssbe:
            raise ssbe
        except Exception:
            # If not in enum, treat as an actual SC code
            sc_code = self.criteria_value

        if sc_code is not None:
            self.sql_where.append(
                f" AND c.responsible_sc_id {self.criteria_comparator} ("
                "   SELECT sc.org_id "
                "   FROM org sc "
                f"   WHERE sc.org_code = {self.single_quoted(sc_code.upper())}"
                ") "
            )

    def _add_criteria_has_gp_practice(self):
        try:
            option = HasGPPractice.by_description(self.criteria_value.lower())

            match option:
                case HasGPPractice.YES_ACTIVE:
                    self.sql_from.append(
                        " INNER JOIN gp_practice_current_links gpl "
                        "   ON gpl.gp_practice_id = c.gp_practice_id "
                    )
                case HasGPPractice.YES_INACTIVE:
                    self.sql_where.append(
                        " AND c.gp_practice_id IS NOT NULL "
                        " AND c.gp_practice_id NOT IN ( "
                        "   SELECT gpl.gp_practice_id "
                        "   FROM gp_practice_current_links gpl ) "
                    )
                case HasGPPractice.NO:
                    self.sql_where.append(" AND c.gp_practice_id IS NULL ")
                case _:
                    raise SelectionBuilderException(
                        self.criteria_key_name, self.criteria_value
                    )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_has_gp_practice_linked_to_sc(self) -> None:
        self.sql_where.append(
            " AND c.gp_practice_id IN ( "
            " SELECT o.org_id FROM gp_practice_current_links gpcl "
            " INNER JOIN org o ON gpcl.gp_practice_id = o.org_id "
            " WHERE gpcl.sc_id = ( "
            f" SELECT org_id FROM org WHERE org_code = {self.single_quoted(self.criteria_value)})) "
        )

    def _add_criteria_screening_status(self, subject: "Subject"):
        self.sql_where.append(" AND ss.screening_status_id ")

        if self.criteria_value.lower() == "unchanged":
            self._force_not_modifier_is_invalid_for_criteria_value()
            if subject is None:
                raise self.invalid_use_of_unchanged_exception(
                    self.criteria_key_name, "no existing subject"
                )
            self.sql_where.append(" = ")
            self.sql_where.append(subject.get_screening_status_id())
        else:
            try:
                screening_status_type = (
                    ScreeningStatusType.by_description_case_insensitive(
                        self.criteria_value
                    )
                )
                if screening_status_type is None:
                    raise SelectionBuilderException(
                        self.criteria_key_name, self.criteria_value
                    )
                self.sql_where.append(self.criteria_comparator)
                self.sql_where.append(screening_status_type.valid_value_id)
            except Exception:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )

    def _add_criteria_previous_screening_status(self):
        screening_status_type = ScreeningStatusType.by_description_case_insensitive(
            self.criteria_value
        )
        if screening_status_type is None:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

        self.sql_where.append(" AND ss.previous_screening_status_id ")

        match screening_status_type:
            case ScreeningStatusType.NULL:
                self.sql_where.append(" IS NULL ")
            case ScreeningStatusType.NOT_NULL:
                self.sql_where.append(" IS NOT NULL ")
            case _:
                self.sql_where.append(
                    f"{self.criteria_comparator}{screening_status_type.valid_value_id}"
                )

    def _add_criteria_screening_status_reason(self, subject: "Subject"):
        if self.criteria_value.lower() == "unchanged":
            self._force_not_modifier_is_invalid_for_criteria_value()
            if subject is None:
                raise self.invalid_use_of_unchanged_exception(
                    self.criteria_key_name, "no existing subject"
                )
            elif subject.get_screening_status_change_reason_id() is None:
                self.sql_where.append(" AND ss.ss_reason_for_change_id IS NULL")
            else:
                self.sql_where.append(
                    f" AND ss.ss_reason_for_change_id = {subject.get_screening_status_change_reason_id()}"
                )
        else:
            try:
                screening_status_change_reason_type = (
                    SSReasonForChangeType.by_description_case_insensitive(
                        self.criteria_value
                    )
                )
                if screening_status_change_reason_type is None:
                    raise SelectionBuilderException(
                        self.criteria_key_name, self.criteria_value
                    )
                self.sql_where.append(
                    f" AND ss.ss_reason_for_change_id {self.criteria_comparator}{screening_status_change_reason_type.valid_value_id}"
                )
            except Exception:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )

    def _add_criteria_date_field(
        self, subject: "Subject", pathway: str, date_type: str
    ) -> None:
        date_column_name = self._get_date_field_column_name(pathway, date_type)

        if date_column_name.startswith("TRUNC(ep."):
            self._add_join_to_latest_episode()
        elif date_column_name.startswith("TRUNC(gcd."):
            self._add_join_to_genetic_condition_diagnosis()
        elif date_column_name.startswith("TRUNC(dctu."):
            self._add_join_to_latest_episode()
            self._add_join_to_cancer_audit_dataset()
            self._add_join_to_cancer_audit_dataset_tumor()
        elif date_column_name.startswith("TRUNC(dctr."):
            self._add_join_to_latest_episode()
            self._add_join_to_cancer_audit_dataset()
            self._add_join_to_cancer_audit_dataset_treatment()

        criteria_words = self.criteria_value.split(" ")

        if self.criteria_value.isdigit():
            self._add_check_comparing_one_date_with_another(
                date_column_name,
                " = ",
                self._add_years_to_oracle_date("c.date_of_birth", self.criteria_value),
                False,
            )
        elif (
            self.criteria_value.lower() != "last birthday"
            and self.criteria_value.lower().endswith(" birthday")
            and len(self.criteria_value.split()) == 2
        ):
            self._add_check_comparing_one_date_with_another(
                date_column_name,
                " = ",
                self._add_years_to_oracle_date(
                    "c.date_of_birth", criteria_words[0][:-2]
                ),
                False,
            )
        elif self._is_valid_date(self.criteria_value):
            self._add_check_comparing_one_date_with_another(
                date_column_name,
                " = ",
                self._oracle_to_date_method(self.criteria_value, "yyyy-mm-dd"),
                False,
            )
        elif self._is_valid_date(self.criteria_value, "%d/%m/%Y"):
            self._add_check_comparing_one_date_with_another(
                date_column_name,
                " = ",
                self._oracle_to_date_method(self.criteria_value, "dd/mm/yyyy"),
                False,
            )
        elif (
            self.criteria_value.endswith(" ago")
            or self.criteria_value.endswith(" later")
        ) and (
            len(criteria_words) == 3
            or (
                len(criteria_words) == 4
                and self.criteria_value.startswith(("> ", "< ", "<= ", ">= "))
            )
            or (
                len(criteria_words) == 5
                and self.criteria_value.lower().startswith(("more than ", "less than "))
            )
        ):
            self._add_check_date_is_a_period_ago_or_later(
                date_column_name, self.criteria_value
            )
        else:
            self._add_criteria_date_field_special_cases(
                self.criteria_value, subject, pathway, date_type, date_column_name
            )

    def _add_criteria_screening_due_date_reason(self, subject: "Subject"):
        due_date_reason = "ss.sdd_reason_for_change_id"
        try:
            screening_due_date_change_reason_type = (
                SDDReasonForChangeType.by_description_case_insensitive(
                    self.criteria_value
                )
            )
            self.sql_where.append(" AND ")

            if screening_due_date_change_reason_type is None:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )

            match screening_due_date_change_reason_type:
                case SDDReasonForChangeType.NULL:
                    self.sql_where.append(f"{due_date_reason}{" IS NULL "}")
                case SDDReasonForChangeType.NOT_NULL:
                    self.sql_where.append(f"{due_date_reason}{" IS NOT NULL "}")
                case SDDReasonForChangeType.UNCHANGED:
                    self._force_not_modifier_is_invalid_for_criteria_value()
                    if subject is None:
                        raise self.invalid_use_of_unchanged_exception(
                            self.criteria_key_name, "no existing subject"
                        )
                    elif subject.get_screening_due_date_change_reason_id() is None:
                        self.sql_where.append(f"{due_date_reason}{" IS NULL "}")
                    else:
                        self.sql_where.append(
                            f"{due_date_reason}{" = "}{subject.get_screening_due_date_change_reason_id()}"
                        )
                case _:
                    self.sql_where.append(
                        f"{due_date_reason}{self.criteria_comparator}{screening_due_date_change_reason_type.valid_value_id}"
                    )
        except SelectionBuilderException as ssbe:
            raise ssbe
        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_surveillance_due_date_reason(self, subject: "Subject"):
        try:
            surveillance_due_date_change_reason = (
                SSDDReasonForChangeType.by_description_case_insensitive(
                    self.criteria_value
                )
            )
            self.sql_where.append(" AND ss.surveillance_sdd_rsn_change_id ")

            if surveillance_due_date_change_reason is None:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )

            match surveillance_due_date_change_reason:
                case SSDDReasonForChangeType.NULL | SSDDReasonForChangeType.NOT_NULL:
                    self.sql_where.append(
                        f" IS {surveillance_due_date_change_reason.description}"
                    )
                case SSDDReasonForChangeType.UNCHANGED:
                    self._force_not_modifier_is_invalid_for_criteria_value()
                    if subject is None:
                        raise self.invalid_use_of_unchanged_exception(
                            self.criteria_key_name, "no existing subject"
                        )
                    elif subject.get_surveillance_due_date_change_reason_id() is None:
                        self.sql_where.append(" IS NULL ")
                    else:
                        self.sql_where.append(
                            f" = {subject.get_surveillance_due_date_change_reason_id()}"
                        )
                case _:
                    self.sql_where.append(
                        f"{self.criteria_comparator}{surveillance_due_date_change_reason.valid_value_id}"
                    )
        except SelectionBuilderException as ssbe:
            raise ssbe
        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_bowel_scope_due_date_reason(self):
        try:
            bowel_scope_due_date_change_reason_type = (
                BowelScopeDDReasonForChangeType.by_description(self.criteria_value)
            )

            if bowel_scope_due_date_change_reason_type is None:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )

            self.sql_where.append(" AND ss.fs_sdd_reason_for_change_id ")
            self.sql_where.append(
                f"{self.criteria_comparator}{bowel_scope_due_date_change_reason_type.valid_value_id}"
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_manual_cease_requested(self) -> None:
        try:
            self.sql_where.append(" AND ss.cease_requested_status_id ")

            criterion = ManualCeaseRequested.by_description_case_insensitive(
                self.criteria_value
            )
            if criterion is None:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )

            match criterion:
                case ManualCeaseRequested.NO:
                    self.sql_where.append(" IS NULL ")
                case ManualCeaseRequested.YES:
                    self.sql_where.append(" IS NOT NULL ")
                case ManualCeaseRequested.DISCLAIMER_LETTER_REQUIRED:
                    self.sql_where.append("= 35")  # C1
                case ManualCeaseRequested.DISCLAIMER_LETTER_SENT:
                    self.sql_where.append("= 36")  # C2
                case _:
                    raise SelectionBuilderException(
                        self.criteria_key_name, self.criteria_value
                    )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_ceased_confirmation_details(self):
        self.sql_where.append(" AND LOWER(ss.ceased_confirmation_details) ")

        try:
            ccd = CeasedConfirmationDetails.by_description(self.criteria_value.lower())
            if ccd in (
                CeasedConfirmationDetails.NULL,
                CeasedConfirmationDetails.NOT_NULL,
            ):
                self.sql_where.append(f" IS {ccd.get_description()} ")
            else:
                raise ValueError("Unrecognized enum value")
        except Exception:
            # Fall back to string matching
            value_quoted = f"'{self.criteria_value.lower()}'"
            self.sql_where.append(f"{self.criteria_comparator} {value_quoted} ")

    def _add_criteria_ceased_confirmation_user_id(self, user: "User") -> None:
        self.sql_where.append(" AND ss.ceased_confirmation_pio_id ")

        if self.criteria_value.isnumeric():  # actual PIO ID
            self.sql_where.append(self.criteria_comparator)
            self.sql_where.append(self.criteria_value)
            self.sql_where.append(" ")
        else:
            try:
                enum_value = CeasedConfirmationUserId.by_description(
                    self.criteria_value.lower()
                )
                if enum_value == CeasedConfirmationUserId.AUTOMATED_PROCESS_ID:
                    self.sql_where.append(self.criteria_comparator)
                    self.sql_where.append(" 2 ")
                elif enum_value == CeasedConfirmationUserId.NOT_NULL:
                    self.sql_where.append(" IS NOT NULL ")
                elif enum_value == CeasedConfirmationUserId.NULL:
                    self.sql_where.append(" IS NULL ")
                elif enum_value == CeasedConfirmationUserId.USER_ID:
                    self.sql_where.append(self.criteria_comparator)
                    self.sql_where.append(str(user.user_id) + " ")
                else:
                    raise SelectionBuilderException(
                        self.criteria_key_name, self.criteria_value
                    )
            except Exception:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )

    def _add_criteria_clinical_reason_for_cease(self) -> None:
        try:
            clinical_cease_reason = (
                ClinicalCeaseReasonType.by_description_case_insensitive(
                    self.criteria_value
                )
            )
            self.sql_where.append(" AND ss.clinical_reason_for_cease_id ")

            if clinical_cease_reason is None:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )

            if clinical_cease_reason in {
                ClinicalCeaseReasonType.NULL,
                ClinicalCeaseReasonType.NOT_NULL,
            }:
                self.sql_where.append(f" IS {clinical_cease_reason.description}")
            else:
                self.sql_where.append(
                    f"{self.criteria_comparator}{clinical_cease_reason.valid_value_id}"
                )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_subject_has_event_status(self) -> None:
        event_exists = (
            self.criteria_key == SubjectSelectionCriteriaKey.SUBJECT_HAS_EVENT_STATUS
        )

        try:
            event_status = EventStatusType.get_by_code(self.criteria_value.upper())

            if event_status is None:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )

            self.sql_where.append(" AND")

            if not event_exists:
                self.sql_where.append(" NOT")

            self.sql_where.append(
                f" EXISTS ("
                f" SELECT 1"
                f" FROM ep_events_t sev"
                f" WHERE sev.screening_subject_id = ss.screening_subject_id"
                f" AND sev.event_status_id = {event_status.id}"
                f") "
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _add_criteria_has_unprocessed_sspi_updates(self) -> None:
        try:
            value = HasUnprocessedSSPIUpdates.by_description(
                self.criteria_value.lower()
            )
            if value == HasUnprocessedSSPIUpdates.YES:
                self.sql_where.append(" AND EXISTS ( SELECT 'sdfp' ")
            elif value == HasUnprocessedSSPIUpdates.NO:
                self.sql_where.append(" AND NOT EXISTS ( SELECT 'sdfp' ")
            else:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )
        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

        self.sql_where.append("   FROM sd_feed_processing_t sdfp ")
        self.sql_where.append("   WHERE sdfp.contact_id = c.contact_id ")
        self.sql_where.append("   AND sdfp.awaiting_manual_intervention = 'Y' ) ")

    def _add_criteria_has_user_dob_update(self) -> None:
        try:
            value = HasUserDobUpdate.by_description(self.criteria_value.lower())
            if value == HasUserDobUpdate.YES:
                self.sql_where.append(" AND EXISTS ( SELECT 'div' ")
            elif value == HasUserDobUpdate.NO:
                self.sql_where.append(" AND NOT EXISTS ( SELECT 'div' ")
            else:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )
        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

        self.sql_where.append("   from mpi.sd_data_item_value_t div ")
        self.sql_where.append("   WHERE div.contact_id = c.contact_id ")
        self.sql_where.append("   AND div.data_item_id = 4 ) ")

    def _add_criteria_subject_has_episodes(
        self, episode_type: Optional["EpisodeType"] = None
    ) -> None:
        try:
            value = SubjectHasEpisode.by_description(self.criteria_value.lower())
            if value == SubjectHasEpisode.YES:
                self.sql_where.append(" AND EXISTS ( SELECT 'ep' ")
            elif value == SubjectHasEpisode.NO:
                self.sql_where.append(" AND NOT EXISTS ( SELECT 'ep' ")
            else:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )
        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

        self.sql_where.append("   FROM ep_subject_episode_t ep ")
        self.sql_where.append(
            "   WHERE ep.screening_subject_id = ss.screening_subject_id "
        )

        if episode_type is not None:
            self.sql_where.append(
                f"   AND ep.episode_type_id = {episode_type.valid_value_id} "
            )

        if self.criteria_key == SubjectSelectionCriteriaKey.SUBJECT_HAS_AN_OPEN_EPISODE:
            self.sql_where.append("   AND ep.episode_end_date IS NULL ")

        self.sql_where.append(" )")

    def _get_date_field_column_name(self, pathway: str, date_type: str) -> str:
        """
        Map pathway and date_type to the correct Oracle column name.
        xt and ap are optional table aliases for diagnostic test and appointment joins.
        """

        concat_key = (pathway + date_type).upper()

        mapping = {
            "ALL_PATHWAYSSCREENING_STATUS_CHANGE_DATE": "TRUNC(ss.screening_status_change_date)",
            "ALL_PATHWAYSLATEST_EPISODE_START_DATE": "TRUNC(ep.episode_start_date)",
            "ALL_PATHWAYSLATEST_EPISODE_END_DATE": "TRUNC(ep.episode_end_date)",
            "ALL_PATHWAYSCEASED_CONFIRMATION_DATE": "TRUNC(ss.ceased_confirmation_recd_date)",
            "ALL_PATHWAYSDATE_OF_DEATH": "TRUNC(c.date_of_death)",
            "ALL_PATHWAYSSYMPTOMATIC_PROCEDURE_DATE": f"TRUNC({self.xt}.surgery_date)",
            "ALL_PATHWAYSAPPOINTMENT_DATE": f"TRUNC({self.ap}.appointment_date)",
            "FOBTDUE_DATE": "TRUNC(ss.screening_due_date)",
            "FOBTCALCULATED_DUE_DATE": "TRUNC(ss.calculated_sdd)",
            "FOBTDUE_DATE_CHANGE_DATE": "TRUNC(ss.sdd_change_date)",
            "FOBTPREVIOUS_DUE_DATE": "TRUNC(ss.previous_sdd)",
            "SURVEILLANCEDUE_DATE": "TRUNC(ss.surveillance_screen_due_date)",
            "SURVEILLANCECALCULATED_DUE_DATE": "TRUNC(ss.calculated_ssdd)",
            "SURVEILLANCEDUE_DATE_CHANGE_DATE": "TRUNC(ss.surveillance_sdd_change_date)",
            "SURVEILLANCEPREVIOUS_DUE_DATE": "TRUNC(ss.previous_surveillance_sdd)",
            "LYNCHDUE_DATE": "TRUNC(ss.lynch_screening_due_date)",
            "LYNCHCALCULATED_DUE_DATE": "TRUNC(ss.lynch_calculated_sdd)",
            "LYNCHDUE_DATE_CHANGE_DATE": "TRUNC(ss.lynch_sdd_change_date)",
            "LYNCHDIAGNOSIS_DATE": "TRUNC(gcd.diagnosis_date)",
            "LYNCHLAST_COLONOSCOPY_DATE": "TRUNC(gcd.last_colonoscopy_date)",
            "LYNCHPREVIOUS_DUE_DATE": "TRUNC(ss.previous_lynch_sdd)",
            "LYNCHLOWER_LYNCH_AGE": "pkg_bcss_common.f_get_lynch_lower_age_limit (ss.screening_subject_id)",
            "ALL_PATHWAYSSEVENTY_FIFTH_BIRTHDAY": "ADD_MONTHS(TRUNC(c.date_of_birth), 12*75)",
            "ALL_PATHWAYSCADS TUMOUR_DATE_OF_DIAGNOSIS": "TRUNC(dctu.date_of_diagnosis)",
            "ALL_PATHWAYSCADS TREATMENT_START_DATE": "TRUNC(dctr.treatment_start_date)",
            "ALL_PATHWAYSDIAGNOSTIC_TEST_CONFIRMED_DATE": f"TRUNC({self.xt}.confirmed_date)",
        }
        if concat_key not in mapping:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)
        return mapping[concat_key]

    def _add_join_to_latest_episode(self) -> None:
        if not self.sql_from_episode:
            self.sql_from_episode.append(
                " INNER JOIN ep_subject_episode_t ep "
                " ON ep.screening_subject_id = ss.screening_subject_id "
                " AND ep.subject_epis_id = ( "
                " SELECT MAX(epx.subject_epis_id) "
                " FROM ep_subject_episode_t epx "
                " WHERE epx.screening_subject_id = ss.screening_subject_id ) "
            )

    def _add_join_to_genetic_condition_diagnosis(self) -> None:
        if not self.sql_from_genetic_condition_diagnosis:
            self.sql_from_genetic_condition_diagnosis.append(
                " INNER JOIN genetic_condition_diagnosis gcd "
                " ON gcd.screening_subject_id = ss.screening_subject_id "
                " AND gcd.deleted_flag = 'N' "
            )

    def _add_join_to_cancer_audit_dataset(self) -> None:
        if (
            " INNER JOIN ds_cancer_audit_t cads ON cads.episode_id = ep.subject_epis_id AND cads.deleted_flag = 'N' "
            not in self.sql_from_cancer_audit_datasets
        ):
            self.sql_from_cancer_audit_datasets.append(
                " INNER JOIN ds_cancer_audit_t cads ON cads.episode_id = ep.subject_epis_id AND cads.deleted_flag = 'N' "
            )

    def _add_join_to_cancer_audit_dataset_tumor(self) -> None:
        if (
            " INNER JOIN DS_CA2_TUMOUR dctu ON dctu.CANCER_AUDIT_ID =cads.CANCER_AUDIT_ID AND dctu.deleted_flag = 'N' "
            not in self.sql_from_cancer_audit_datasets
        ):
            self.sql_from_cancer_audit_datasets.append(
                " INNER JOIN DS_CA2_TUMOUR dctu ON dctu.CANCER_AUDIT_ID =cads.CANCER_AUDIT_ID AND dctu.deleted_flag = 'N' "
            )

    def _add_join_to_cancer_audit_dataset_treatment(self) -> None:
        if (
            " INNER JOIN DS_CA2_TREATMENT dctr ON dctr.CANCER_AUDIT_ID = cads.CANCER_AUDIT_ID AND dctr.deleted_flag = 'N' "
            not in self.sql_from_cancer_audit_datasets
        ):
            self.sql_from_cancer_audit_datasets.append(
                " INNER JOIN DS_CA2_TREATMENT dctr ON dctr.CANCER_AUDIT_ID = cads.CANCER_AUDIT_ID AND dctr.deleted_flag = 'N' "
            )

    def _add_check_comparing_one_date_with_another(
        self,
        column_to_check: str,
        comparator: str,
        date_to_check_against: str,
        allow_nulls: bool,
    ) -> None:
        if allow_nulls:
            column_to_check = self._nvl_date(column_to_check)
            date_to_check_against = self._nvl_date(date_to_check_against)
        self.sql_where.append(
            f" AND {column_to_check}  {comparator}  {date_to_check_against} "
        )

    def _add_days_to_oracle_date(self, column_name: str, number_of_days: str) -> str:
        return f" TRUNC({column_name}) + {number_of_days} "

    def _add_months_to_oracle_date(
        self, column_name: str, number_of_months: str
    ) -> str:
        return self._add_months_or_years_to_oracle_date(
            column_name, False, number_of_months
        )

    def _add_years_to_oracle_date(self, column_name: str, number_of_years) -> str:
        return self._add_months_or_years_to_oracle_date(
            column_name, True, number_of_years
        )

    def _add_months_or_years_to_oracle_date(
        self, column_name: str, years: bool, number_to_add_or_subtract: str
    ) -> str:
        if years:
            number_to_add_or_subtract += " * 12 "
        return f" ADD_MONTHS(TRUNC({column_name}), {number_to_add_or_subtract}) "

    def _subtract_days_from_oracle_date(
        self, column_name: str, number_of_days: str
    ) -> str:
        return f" TRUNC({column_name}) - {number_of_days} "

    def _subtract_months_from_oracle_date(
        self, column_name: str, number_of_months: str
    ) -> str:
        return self._add_months_or_years_to_oracle_date(
            column_name, False, "-" + number_of_months
        )

    def _subtract_years_from_oracle_date(
        self, column_name: str, number_of_years: str
    ) -> str:
        return self._add_months_or_years_to_oracle_date(
            column_name, True, "-" + number_of_years
        )

    def _oracle_to_date_method(self, date: str, format: str) -> str:
        return f" TO_DATE( '{date}', '{format}') "

    def _add_check_date_is_a_period_ago_or_later(
        self, date_column_name: str, value: str
    ) -> None:
        criteria_words = value.split(" ")
        numerator = criteria_words[0]
        denominator = criteria_words[1]
        ago_or_later = criteria_words[-1]

        if ago_or_later == "ago":
            if value.startswith("> "):
                comparator = " < "
                numerator = criteria_words[1]
                denominator = criteria_words[2]
            elif value.startswith(">= "):
                comparator = " <= "
                numerator = criteria_words[1]
                denominator = criteria_words[2]
            elif value.lower().startswith("more than "):
                comparator = " < "
                numerator = criteria_words[2]
                denominator = criteria_words[3]
            elif value.startswith("< "):
                comparator = " > "
                numerator = criteria_words[1]
                denominator = criteria_words[2]
            elif value.startswith("<= "):
                comparator = " >= "
                numerator = criteria_words[1]
                denominator = criteria_words[2]
            elif value.lower().startswith("less than "):
                comparator = " > "
                numerator = criteria_words[2]
                denominator = criteria_words[3]
            else:
                comparator = " = "
        else:
            if value.startswith("> "):
                comparator = " > "
                numerator = criteria_words[1]
                denominator = criteria_words[2]
            elif value.startswith(">= "):
                comparator = " >= "
                numerator = criteria_words[1]
                denominator = criteria_words[2]
            elif value.lower().startswith("more than "):
                comparator = " > "
                numerator = criteria_words[2]
                denominator = criteria_words[3]
            elif value.startswith("< "):
                comparator = " < "
                numerator = criteria_words[1]
                denominator = criteria_words[2]
            elif value.startswith("<= "):
                comparator = " <= "
                numerator = criteria_words[1]
                denominator = criteria_words[2]
            elif value.lower().startswith("less than "):
                comparator = " < "
                numerator = criteria_words[2]
                denominator = criteria_words[3]
            else:
                comparator = " = "

        compound_denominator = denominator + " " + ago_or_later

        if compound_denominator in ("year ago", "years ago"):
            self._get_x_years_ago(date_column_name, comparator, numerator)
        elif compound_denominator in ("year later", "years later"):
            self._get_x_years_later(date_column_name, comparator, numerator)
        elif compound_denominator in ("month ago", "months ago"):
            self._get_x_months_ago(date_column_name, comparator, numerator)
        elif compound_denominator in ("month later", "months later"):
            self._get_x_months_later(date_column_name, comparator, numerator)
        elif compound_denominator in ("day ago", "days ago"):
            self._get_x_days_ago(date_column_name, comparator, numerator)
        elif compound_denominator in ("day later", "days later"):
            self._get_x_days_later(date_column_name, comparator, numerator)

        if comparator == " > ":
            if ago_or_later == "ago":
                self._add_check_comparing_one_date_with_another(
                    date_column_name, " <= ", "TRUNC(SYSDATE)", False
                )
            else:
                self._add_check_comparing_one_date_with_another(
                    date_column_name, " > ", "TRUNC(SYSDATE)", False
                )

    def _add_criteria_date_field_special_cases(
        self,
        value: str,
        subject: "Subject",
        pathway: str,
        date_type: str,
        date_column_name: str,
    ) -> None:
        try:
            date_to_use = DateDescription.by_description_case_insensitive(value)
            if date_to_use is None:
                raise ValueError(f"No DateDescription found for value: {value}")
            number_of_months = str(date_to_use.number_of_months)

            match date_to_use:
                case DateDescription.NOT_NULL:
                    self._add_check_column_is_null_or_not(date_column_name, False)
                case DateDescription.NULL | DateDescription.UNCHANGED_NULL:
                    self._add_check_column_is_null_or_not(date_column_name, True)
                case DateDescription.LAST_BIRTHDAY:
                    self._add_check_comparing_one_date_with_another(
                        date_column_name,
                        " = ",
                        "pkg_bcss_common.f_get_last_birthday(c.date_of_birth)",
                        False,
                    )
                case (
                    DateDescription.CSDD
                    | DateDescription.CALCULATED_FOBT_DUE_DATE
                    | DateDescription.CALCULATED_SCREENING_DUE_DATE
                ):
                    self._add_check_comparing_one_date_with_another(
                        date_column_name, " = ", "TRUNC(ss.calculated_sdd)", True
                    )
                case DateDescription.CALCULATED_LYNCH_DUE_DATE:
                    self._add_check_comparing_one_date_with_another(
                        date_column_name, " = ", "TRUNC(ss.lynch_calculated_sdd)", True
                    )
                case (
                    DateDescription.CALCULATED_SURVEILLANCE_DUE_DATE
                    | DateDescription.CSSDD
                ):
                    self._add_check_comparing_one_date_with_another(
                        date_column_name, " = ", "TRUNC(ss.calculated_ssdd)", True
                    )
                case DateDescription.LESS_THAN_TODAY | DateDescription.BEFORE_TODAY:
                    self._add_check_comparing_one_date_with_another(
                        date_column_name, " < ", "TRUNC(SYSDATE)", False
                    )
                case DateDescription.GREATER_THAN_TODAY | DateDescription.AFTER_TODAY:
                    self._add_check_comparing_one_date_with_another(
                        date_column_name, " > ", "TRUNC(SYSDATE)", False
                    )
                case DateDescription.TODAY:
                    self._add_check_comparing_one_date_with_another(
                        date_column_name, " = ", "TRUNC(SYSDATE)", False
                    )
                case DateDescription.TOMORROW:
                    self._add_check_comparing_one_date_with_another(
                        date_column_name,
                        " = ",
                        self._add_days_to_oracle_date("SYSDATE", "1"),
                        False,
                    )
                case DateDescription.YESTERDAY:
                    self._add_check_comparing_one_date_with_another(
                        date_column_name,
                        " = ",
                        self._subtract_days_from_oracle_date("SYSDATE", "1"),
                        False,
                    )
                case (
                    DateDescription.LESS_THAN_OR_EQUAL_TO_6_MONTHS_AGO
                    | DateDescription.WITHIN_THE_LAST_2_YEARS
                    | DateDescription.WITHIN_THE_LAST_4_YEARS
                    | DateDescription.WITHIN_THE_LAST_6_MONTHS
                ):
                    self._add_check_comparing_one_date_with_another(
                        self._subtract_months_from_oracle_date(
                            "SYSDATE", number_of_months
                        ),
                        " <= ",
                        date_column_name,
                        False,
                    )
                    self._add_check_comparing_one_date_with_another(
                        date_column_name, " <= ", "TRUNC(SYSDATE)", False
                    )
                case DateDescription.LYNCH_DIAGNOSIS_DATE:
                    self._add_join_to_genetic_condition_diagnosis()
                    self._add_check_comparing_one_date_with_another(
                        date_column_name, " = ", "TRUNC(gcd.diagnosis_date)", True
                    )
                case DateDescription.TWO_YEARS_FROM_LAST_LYNCH_COLONOSCOPY_DATE:
                    self._add_join_to_genetic_condition_diagnosis()
                    self._add_check_comparing_one_date_with_another(
                        date_column_name,
                        " = ",
                        self._add_months_to_oracle_date(
                            "gcd.last_colonoscopy_date", number_of_months
                        ),
                        False,
                    )
                case (
                    DateDescription.ONE_YEAR_FROM_EPISODE_END
                    | DateDescription.TWO_YEARS_FROM_EPISODE_END
                    | DateDescription.THREE_YEARS_FROM_EPISODE_END
                ):
                    self._add_check_comparing_one_date_with_another(
                        date_column_name,
                        " = ",
                        self._add_months_to_oracle_date(
                            "ep.episode_end_date", number_of_months
                        ),
                        False,
                    )
                case (
                    DateDescription.ONE_YEAR_FROM_DIAGNOSTIC_TEST
                    | DateDescription.TWO_YEARS_FROM_DIAGNOSTIC_TEST
                    | DateDescription.THREE_YEARS_FROM_DIAGNOSTIC_TEST
                ):
                    self._add_check_comparing_one_date_with_another(
                        date_column_name,
                        " = ",
                        self._add_months_to_oracle_date(
                            self.xt + ".confirmed_date", number_of_months
                        ),
                        False,
                    )
                case (
                    DateDescription.ONE_YEAR_FROM_SYMPTOMATIC_PROCEDURE
                    | DateDescription.TWO_YEARS_FROM_SYMPTOMATIC_PROCEDURE
                    | DateDescription.THREE_YEARS_FROM_SYMPTOMATIC_PROCEDURE
                ):
                    self._add_check_comparing_one_date_with_another(
                        date_column_name,
                        " = ",
                        self._add_months_to_oracle_date(
                            self.xt + ".surgery_date", number_of_months
                        ),
                        False,
                    )
                case DateDescription.TWO_YEARS_FROM_EARLIEST_S10_EVENT:
                    self._add_check_comparing_date_with_earliest_or_latest_event_date(
                        date_column_name,
                        " = ",
                        "MIN",
                        EventStatusType.S10,
                        number_of_months,
                    )
                case DateDescription.TWO_YEARS_FROM_LATEST_A37_EVENT:
                    self._add_check_comparing_date_with_earliest_or_latest_event_date(
                        date_column_name,
                        " = ",
                        "MAX",
                        EventStatusType.A37,
                        number_of_months,
                    )
                case DateDescription.TWO_YEARS_FROM_LATEST_J8_EVENT:
                    self._add_check_comparing_date_with_earliest_or_latest_event_date(
                        date_column_name,
                        " = ",
                        "MAX",
                        EventStatusType.J8,
                        number_of_months,
                    )
                case DateDescription.TWO_YEARS_FROM_LATEST_J15_EVENT:
                    self._add_check_comparing_date_with_earliest_or_latest_event_date(
                        date_column_name,
                        " = ",
                        "MAX",
                        EventStatusType.J15,
                        number_of_months,
                    )
                case DateDescription.TWO_YEARS_FROM_LATEST_J16_EVENT:
                    self._add_check_comparing_date_with_earliest_or_latest_event_date(
                        date_column_name,
                        " = ",
                        "MAX",
                        EventStatusType.J16,
                        number_of_months,
                    )
                case DateDescription.TWO_YEARS_FROM_LATEST_J25_EVENT:
                    self._add_check_comparing_date_with_earliest_or_latest_event_date(
                        date_column_name,
                        " = ",
                        "MAX",
                        EventStatusType.J25,
                        number_of_months,
                    )
                case DateDescription.TWO_YEARS_FROM_LATEST_S158_EVENT:
                    self._add_check_comparing_date_with_earliest_or_latest_event_date(
                        date_column_name,
                        " = ",
                        "MAX",
                        EventStatusType.S158,
                        number_of_months,
                    )
                case DateDescription.AS_AT_EPISODE_START:
                    self._add_join_to_latest_episode()
                    self._add_check_comparing_one_date_with_another(
                        date_column_name, " = ", "TRUNC(ep.episode_start_dd)", False
                    )
                case DateDescription.UNCHANGED:
                    existing_due_date_value = self._get_date_field_existing_value(
                        subject, pathway, date_type
                    )
                    if subject is None:
                        raise ValueError("Subject is None")
                    elif existing_due_date_value is None:
                        self._add_check_column_is_null_or_not(date_column_name, True)
                    elif existing_due_date_value == date(1066, 1, 1):
                        raise ValueError(f"{value} date doesn't support 'unchanged'")
                    else:
                        self._add_check_comparing_one_date_with_another(
                            date_column_name,
                            " = ",
                            self._oracle_to_date_method(
                                existing_due_date_value.strftime("%Y-%m-%d"),
                                "yyyy-mm-dd",
                            ),
                            False,
                        )

        except Exception:
            raise Exception

    def _add_check_comparing_date_with_earliest_or_latest_event_date(
        self,
        date_column_name: str,
        comparator: str,
        min_or_max: str,
        event: EventStatusType,
        number_of_months: str,
    ):

        self._add_join_to_latest_episode()

        alias = event.code.lower()
        subquery = (
            f"(SELECT {self._add_months_to_oracle_date(f'{min_or_max}({alias}.datestamp)', number_of_months)} "
            f"FROM ep_events_t {alias} "
            f"WHERE {alias}.subject_epis_id = ep.subject_epis_id "
            f"AND {alias}.event_status_id = {event.id})"
        )

        self.sql_where.append(f"AND {date_column_name} {comparator} {subquery}")

    def _add_check_column_is_null_or_not(self, column_name: str, is_null: bool) -> None:
        self.sql_where.append(f" AND {column_name} ")
        if is_null:
            self.sql_where.append(" IS NULL ")
        else:
            self.sql_where.append(" IS NOT NULL ")

    def _get_date_field_existing_value(
        self, subject: "Subject", pathway: str, date_type: str
    ) -> Optional[date]:

        key = pathway + date_type

        if key == "ALL_PATHWAYS" + "SCREENING_STATUS_CHANGE_DATE":
            return subject.screening_status_change_date
        elif key == "ALL_PATHWAYS" + "DATE_OF_DEATH":
            return subject.date_of_death
        elif key == "FOBT" + "DUE_DATE":
            return subject.screening_due_date
        elif key == "FOBT" + "CALCULATED_DUE_DATE":
            return subject.calculated_screening_due_date
        elif key == "FOBT" + "DUE_DATE_CHANGE_DATE":
            return subject.screening_due_date_change_date
        elif key == "SURVEILLANCE" + "DUE_DATE":
            return subject.surveillance_screening_due_date
        elif key == "SURVEILLANCE" + "CALCULATED_DUE_DATE":
            return subject.calculated_surveillance_due_date
        elif key == "SURVEILLANCE" + "DUE_DATE_CHANGE_DATE":
            return subject.surveillance_due_date_change_date
        elif key == "LYNCH" + "DUE_DATE":
            return subject.lynch_due_date
        elif key == "LYNCH" + "CALCULATED_DUE_DATE":
            return subject.calculated_lynch_due_date
        elif key == "LYNCH" + "DUE_DATE_CHANGE_DATE":
            return subject.lynch_due_date_change_date
        else:
            return date(1066, 1, 1)

    def _get_x_years_ago(
        self, date_column_name: str, comparator: str, numerator: str
    ) -> None:
        self._add_check_comparing_one_date_with_another(
            date_column_name,
            comparator,
            self._subtract_years_from_oracle_date("SYSDATE", numerator),
            False,
        )

    def _get_x_months_ago(
        self, date_column_name: str, comparator: str, numerator: str
    ) -> None:
        self._add_check_comparing_one_date_with_another(
            date_column_name,
            comparator,
            self._subtract_months_from_oracle_date("SYSDATE", numerator),
            False,
        )

    def _get_x_days_ago(
        self, date_column_name: str, comparator: str, numerator: str
    ) -> None:
        self._add_check_comparing_one_date_with_another(
            date_column_name,
            comparator,
            self._subtract_days_from_oracle_date("SYSDATE", numerator),
            False,
        )

    def _get_x_years_later(
        self, date_column_name: str, comparator: str, numerator: str
    ) -> None:
        self._add_check_comparing_one_date_with_another(
            date_column_name,
            comparator,
            self._add_years_to_oracle_date("SYSDATE", numerator),
            False,
        )

    def _get_x_months_later(
        self, date_column_name: str, comparator: str, numerator: str
    ) -> None:
        self._add_check_comparing_one_date_with_another(
            date_column_name,
            comparator,
            self._add_months_to_oracle_date("SYSDATE", numerator),
            False,
        )

    def _get_x_days_later(
        self, date_column_name: str, comparator: str, numerator: str
    ) -> None:
        self._add_check_comparing_one_date_with_another(
            date_column_name,
            comparator,
            self._add_days_to_oracle_date("SYSDATE", numerator),
            False,
        )

    def _nvl_date(self, column_name: str) -> str:
        if "SYSDATE" in column_name.upper():
            return_value = " " + column_name + " "
        else:
            return_value = (
                " NVL(" + column_name + ", TO_DATE('01/01/1066', 'dd/mm/yyyy')) "
            )
        return return_value

    def _is_valid_date(self, value: str, date_format: str = "%Y-%m-%d") -> bool:
        try:
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            return False

    @staticmethod
    def single_quoted(value: str) -> str:
        return f"'{value}'"

    @staticmethod
    def invalid_use_of_unchanged_exception(criteria_key_name: str, reason: str):
        return SelectionBuilderException(
            f"Invalid use of 'unchanged' criteria value ({reason}) for: {criteria_key_name}"
        )
