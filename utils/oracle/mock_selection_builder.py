# mock_selection_builder.py — Development-only testing harness for criteria logic
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from classes.selection_builder_exception import SelectionBuilderException
from classes.subject_selection_criteria_key import SubjectSelectionCriteriaKey


# Add helper class stubs below
class SymptomaticProcedureResultType:
    """
    Maps symptom-driven surgery result descriptions to valid value IDs.
    """

    _label_to_id = {
        "normal": 9601,
        "inconclusive": 9602,
        "cancer detected": 9603,
        # Extend as needed
    }

    @classmethod
    def get_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._label_to_id:
            raise ValueError(f"Unknown symptomatic procedure result: '{description}'")
        return cls._label_to_id[key]


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

    def _add_criteria_symptomatic_procedure_result(self) -> None:
        """
        Filters based on symptomatic surgery result value or presence.
        """
        try:
            column = "xt.surgery_result_id"
            value = self.criteria_value.strip().lower()

            if value == "null":
                self.sql_where.append(f"AND {column} IS NULL")
            else:
                result_id = SymptomaticProcedureResultType.get_id(self.criteria_value)
                self.sql_where.append(
                    f"AND {column} {self.criteria_comparator} {result_id}"
                )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)
