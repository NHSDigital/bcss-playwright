# mock_selection_builder.py — Development-only testing harness for criteria logic
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from classes.selection_builder_exception import SelectionBuilderException
from classes.subject_selection_criteria_key import SubjectSelectionCriteriaKey


# Add helper class stubs below
class Subject:
    def __init__(self, lynch_due_date_change_reason_id):
        self.lynch_due_date_change_reason_id = lynch_due_date_change_reason_id


class LynchIncidentEpisodeType:
    """
    Maps symbolic criteria values for Lynch incident episode linkage.
    """

    NULL = "null"
    NOT_NULL = "not_null"
    LATEST_EPISODE = "latest_episode"
    EARLIER_EPISODE = "earlier_episode"

    _symbolics = {NULL, NOT_NULL, LATEST_EPISODE, EARLIER_EPISODE}

    @classmethod
    def from_description(cls, description: str) -> str:
        key = description.strip().lower()
        if key not in cls._symbolics:
            raise ValueError(
                f"Unknown Lynch incident episode criteria: '{description}'"
            )
        return key


class MockSelectionBuilder:
    """
    Lightweight test harness that mimics SubjectSelectionQueryBuilder behavior.

    This class is used for local testing of SQL fragment builder methods without requiring
    the full application context. Developers can reimplement individual _add_criteria_*
    methods here for isolated evaluation.

    Usage:
        - Add your _add_criteria_* method to this class
        - Then create tests in utils/oracle/test_subject_criteria_dev.py to run it
        - Use dump_sql() to inspect the generated SQL fragment
    """

    def __init__(self, criteria_key, criteria_value, criteria_comparator=">="):
        self.criteria_key = criteria_key
        self.criteria_key_name = criteria_key.description
        self.criteria_value = criteria_value
        self.criteria_comparator = criteria_comparator
        self.criteria_index: int = 0
        self.sql_where = []
        self.sql_from = []

    # Don't delete this method; it is used to inspect the SQL fragments
    def dump_sql(self):
        parts = []

        if self.sql_from:
            parts.append("-- FROM clause --")
            parts.extend(self.sql_from)

        if self.sql_where:
            parts.append("-- WHERE clause --")
            parts.extend(self.sql_where)

        return "\n".join(parts)

    def _add_join_to_latest_episode(self) -> None:
        """
        Mock stub for adding latest episode join. No-op for test harness.
        """
        self.sql_from.append("-- JOIN to latest episode placeholder")

    def _force_not_modifier_is_invalid(self):
        # Placeholder for rule enforcement. No-op in mock builder.
        pass

    def _dataset_source_for_criteria_key(self) -> dict:
        """
        Maps criteria key to dataset table and alias.
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

    def _add_join_to_surveillance_review(self):
        self.sql_from.append("-- JOIN to surveillance review placeholder")

    # === Example testable method below ===
    # Replace this with the one you want to test,
    # then use utils/oracle/test_subject_criteria_dev.py to run your scenarios

    def _add_criteria_lynch_incident_episode(self) -> None:
        """
        Filters based on linkage to a Lynch incident episode.
        """
        try:
            self._add_join_to_latest_episode()
            column = "ss.lynch_incident_subject_epis_id"
            value = LynchIncidentEpisodeType.from_description(self.criteria_value)

            if value == LynchIncidentEpisodeType.NULL:
                self.sql_where.append(f"AND {column} IS NULL")

            elif value == LynchIncidentEpisodeType.NOT_NULL:
                self.sql_where.append(f"AND {column} IS NOT NULL")

            elif value == LynchIncidentEpisodeType.LATEST_EPISODE:
                self.sql_where.append(f"AND {column} = ep.subject_epis_id")

            elif value == LynchIncidentEpisodeType.EARLIER_EPISODE:
                self.sql_where.append(f"AND {column} < ep.subject_epis_id")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)
