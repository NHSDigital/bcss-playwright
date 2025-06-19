# mock_selection_builder.py — Development-only testing harness for criteria logic
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from classes.selection_builder_exception import SelectionBuilderException


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
        self.sql_where = []
        self.sql_from = []

    # Don't delete this method; it is used to inspect the SQL fragments
    def dump_sql(self):
        return "\n".join(self.sql_where)
    
    def _add_join_to_latest_episode(self) -> None:
        """
        Mock stub for adding latest episode join. No-op for test harness.
        """
        self.sql_from.append("-- JOIN to latest episode placeholder")


    # === Example testable method below ===
    # Replace this with the one you want to test,
    # then use utils/oracle/test_subject_criteria_dev.py to run your scenarios

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
                raise ValueError(f"Invalid value for analyser result code presence: {value}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

