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

    def _add_join_to_appointments(self) -> None:
        """
        Adds join to appointment_t table based on appointment selection strategy.
        Requires prior join to latest episode (ep). Aliases the appointment table as 'ap'.

        Accepts values:
            - "any_appointment_in_latest_episode"
            - "latest_appointment_in_latest_episode"
            - "earlier_appointment_in_latest_episode"
            - "later_appointment_in_latest_episode"
        """
        try:
            value = self.criteria_value.strip().lower()
            ap_alias = "ap"
            apr_alias = "ap_prev"  # Simulated prior alias for test support

            self._add_join_to_latest_episode()
            self.sql_from.append(
                f"INNER JOIN appointment_t {ap_alias} ON {ap_alias}.subject_epis_id = ep.subject_epis_id"
            )

            if value == "any_appointment_in_latest_episode":
                return
            elif value == "latest_appointment_in_latest_episode":
                self.sql_from.append(
                    f"AND {ap_alias}.appointment_id = ("
                    f" SELECT MAX(apx.appointment_id)"
                    f" FROM appointment_t apx"
                    f" WHERE apx.subject_epis_id = ep.subject_epis_id"
                    f" AND apx.void = 'N')"
                )
            elif value == "earlier_appointment_in_latest_episode":
                self.sql_from.append(
                    f"AND {ap_alias}.appointment_id < {apr_alias}.appointment_id"
                )
            elif value == "later_appointment_in_latest_episode":
                self.sql_from.append(
                    f"AND {ap_alias}.appointment_id > {apr_alias}.appointment_id"
                )
            else:
                raise ValueError(f"Invalid appointment selection value: {value}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)
