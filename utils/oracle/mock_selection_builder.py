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
