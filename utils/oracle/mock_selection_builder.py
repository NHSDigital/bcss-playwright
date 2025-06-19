# mock_selection_builder.py — Development-only testing harness for criteria logic
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from classes.selection_builder_exception import SelectionBuilderException


# Add helper class stubs below
class DiagnosticTestHasResult:
    """
    Resolves whether a diagnostic test has a result, or maps to a specific result ID.
    """

    YES = "yes"
    NO = "no"

    _mapping = {
        "yes": YES,
        "no": NO,
        "positive": 9001,
        "negative": 9002,
        "indeterminate": 9003,
    }

    @classmethod
    def from_description(cls, description: str):
        key = description.strip().lower()
        if key not in cls._mapping:
            raise ValueError(f"Unknown test result description: '{description}'")
        return cls._mapping[key]

    @classmethod
    def get_id(cls, description: str) -> int:
        val = cls.from_description(description)
        if isinstance(val, int):
            return val
        raise ValueError(f"No ID associated with: '{description}'")


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

    # === Example testable method below ===
    # Replace this with the one you want to test,
    # then use utils/oracle/test_subject_criteria_dev.py to run your scenarios

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
