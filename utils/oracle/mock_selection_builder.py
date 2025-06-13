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

    def dump_sql(self):
        return "\n".join(self.sql_where)

    # === Example testable method below ===
    # Replace this with the one you want to test,
    # then use utils/oracle/test_subject_criteria_dev.py to run your scenarios

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
