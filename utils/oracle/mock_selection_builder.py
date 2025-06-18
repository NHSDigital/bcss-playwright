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

    # === Example testable method below ===
    # Replace this with the one you want to test,
    # then use utils/oracle/test_subject_criteria_dev.py to run your scenarios

    def _add_criteria_subject_has_kit_notes(self) -> None:
        """
        Filters subjects based on presence of active kit-related notes.
        Accepts values: 'yes' or 'no'.
        """
        try:
            value = self.criteria_value.strip().lower()

            if value == "yes":
                prefix = "AND EXISTS"
            elif value == "no":
                prefix = "AND NOT EXISTS"
            else:
                raise ValueError(f"Invalid value for kit notes: {value}")

            self.sql_where.append(
                f"""{prefix} (
    SELECT 1
    FROM supporting_notes_t sn
    WHERE sn.screening_subject_id = ss.screening_subject_id
        AND (
        sn.type_id = '308015'
        OR sn.promote_pio_id IS NOT NULL
        )
        AND sn.status_id = 4100
    )
    AND ss.number_of_invitations > 0
    AND rownum = 1"""
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)
