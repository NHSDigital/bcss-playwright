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

    def _add_criteria_has_diagnostic_test_containing_polyp(self) -> None:
        """
        Adds logic to filter based on whether a diagnostic test has a recorded polyp.
        'Yes' joins polyp tables; 'No' checks for absence via NOT EXISTS.
        """
        try:
            value = self.criteria_value.strip().lower()

            if value == "yes":
                self.sql_from.append(
                    "INNER JOIN external_tests_t ext ON ep.subject_epis_id = ext.subject_epis_id\n"
                    "INNER JOIN ds_colonoscopy_t dsc ON ext.ext_test_id = dsc.ext_test_id\n"
                    "INNER JOIN ds_polyp_t dst ON ext.ext_test_id = dst.ext_test_id"
                )
                self.sql_where.append(
                    "AND ext.void = 'N'\n"
                    "AND dst.deleted_flag = 'N'"
                )
            elif value == "no":
                self.sql_where.append(
                    """AND NOT EXISTS (
        SELECT 'ext'
        FROM external_tests_t ext
        LEFT JOIN ds_polyp_t dst ON ext.ext_test_id = dst.ext_test_id
        WHERE ext.subject_epis_id = ep.subject_epis_id
    )"""
                )
            else:
                raise ValueError(f"Unknown value for diagnostic test containing polyp: {value}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)
