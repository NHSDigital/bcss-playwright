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
from classes.has_gp_practice import HasGPPractice
from classes.has_unprocessed_sspi_updates import HasUnprocessedSSPIUpdates
from classes.has_user_dob_update import HasUserDobUpdate
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
