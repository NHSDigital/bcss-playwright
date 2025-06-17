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

    # Don't delete this method; it is used to inspect the SQL fragments
    def dump_sql(self):
        return "\n".join(self.sql_where)

    # === Example testable method below ===
    # Replace this with the one you want to test,
    # then use utils/oracle/test_subject_criteria_dev.py to run your scenarios

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
