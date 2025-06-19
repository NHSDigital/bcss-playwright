# mock_selection_builder.py — Development-only testing harness for criteria logic
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from classes.selection_builder_exception import SelectionBuilderException


# Add helper class stubs below
class DiagnosticTestType:
    """
    Mock mapping of diagnostic test type names to valid value IDs.
    """

    _mapping = {
        "pcr": 3001,
        "antigen": 3002,
        "lateral flow": 3003,
    }

    @classmethod
    def get_valid_value_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._mapping:
            raise ValueError(f"Unknown diagnostic test type: {description}")
        return cls._mapping[key]


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
