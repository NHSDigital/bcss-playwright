# mock_selection_builder.py — Development-only testing harness for criteria logic
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# print("PYTHONPATH set to:", sys.path[0]) # Uncomment for local debug
from classes.selection_builder_exception import SelectionBuilderException


class MockSelectionBuilder:
    """
    Lightweight test harness that mimics SubjectSelectionQueryBuilder behavior.

    This class is meant for local testing of SQL fragment builders without the full
    application context. Developers can copy/paste individual _add_criteria_* methods
    from the real builder and test inputs/outputs directly.

    Usage:
        - Create an instance with a criteria key and value
        - Call the appropriate criteria builder method
        - Use dump_sql() to inspect the resulting SQL
    """

    def __init__(self, criteria_key, criteria_value, criteria_comparator=">="):
        self.criteria_key = criteria_key
        self.criteria_key_name = criteria_key.description
        self.criteria_value = criteria_value
        self.criteria_comparator = criteria_comparator
        self.sql_where = []

    # === Example testable method ===
    # Replace this with the one you want to test,
    # then use utils/oracle/test_subject_criteria_dev.py to run your scenarios

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

    def dump_sql(self):
        return "\n".join(self.sql_where)
