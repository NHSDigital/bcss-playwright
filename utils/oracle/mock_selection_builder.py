# mock_selection_builder.py — Development-only testing harness for criteria logic
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from classes.selection_builder_exception import SelectionBuilderException


# Add helper class stubs below
class AppointmentSlotType:
    """
    Mocked appointment slot type mapping for test purposes.
    Replace IDs with real values from production enum if needed.
    """

    _mapping = {
        "clinic": 1001,
        "phone": 1002,
        "video": 1003,
    }

    @classmethod
    def get_id(cls, description: str) -> int:
        key = description.strip().lower()
        if key not in cls._mapping:
            raise ValueError(f"Unknown appointment slot type: {description}")
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

    def _add_criteria_appointment_type(self) -> None:
        """
        Filters appointments by slot type (e.g. clinic, phone).
        Requires prior join to appointment_t as alias 'ap' (via WHICH_APPOINTMENT).

        Uses comparator and resolves slot type label to ID via AppointmentSlotType.
        """
        try:
            comparator = self.criteria_comparator
            value = self.criteria_value.strip()
            slot_type_id = AppointmentSlotType.get_id(value)

            self.sql_where.append(
                f"AND ap.appointment_slot_type_id {comparator} {slot_type_id}"
            )

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)
