# mock_selection_builder.py — Development-only testing harness for criteria logic
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from classes.selection_builder_exception import SelectionBuilderException


# Add helper class stubs below
class WhichDiagnosticTest:
    """
    Test stub that maps criteria values to normalized diagnostic test selection keys.
    Used by _add_join_to_diagnostic_tests for test harness evaluation.
    """

    ANY_TEST_IN_ANY_EPISODE = "any_test_in_any_episode"
    ANY_TEST_IN_LATEST_EPISODE = "any_test_in_latest_episode"
    ONLY_TEST_IN_LATEST_EPISODE = "only_test_in_latest_episode"
    ONLY_NOT_VOID_TEST_IN_LATEST_EPISODE = "only_not_void_test_in_latest_episode"
    LATEST_TEST_IN_LATEST_EPISODE = "latest_test_in_latest_episode"
    LATEST_NOT_VOID_TEST_IN_LATEST_EPISODE = "latest_not_void_test_in_latest_episode"
    EARLIEST_NOT_VOID_TEST_IN_LATEST_EPISODE = (
        "earliest_not_void_test_in_latest_episode"
    )
    EARLIER_TEST_IN_LATEST_EPISODE = "earlier_test_in_latest_episode"
    LATER_TEST_IN_LATEST_EPISODE = "later_test_in_latest_episode"

    _mapping = {
        "any_test_in_any_episode": ANY_TEST_IN_ANY_EPISODE,
        "any_test_in_latest_episode": ANY_TEST_IN_LATEST_EPISODE,
        "only_test_in_latest_episode": ONLY_TEST_IN_LATEST_EPISODE,
        "only_not_void_test_in_latest_episode": ONLY_NOT_VOID_TEST_IN_LATEST_EPISODE,
        "latest_test_in_latest_episode": LATEST_TEST_IN_LATEST_EPISODE,
        "latest_not_void_test_in_latest_episode": LATEST_NOT_VOID_TEST_IN_LATEST_EPISODE,
        "earliest_not_void_test_in_latest_episode": EARLIEST_NOT_VOID_TEST_IN_LATEST_EPISODE,
        "earlier_test_in_latest_episode": EARLIER_TEST_IN_LATEST_EPISODE,
        "later_test_in_latest_episode": LATER_TEST_IN_LATEST_EPISODE,
    }

    @classmethod
    def from_description(cls, description: str) -> str:
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

    def _add_join_to_diagnostic_tests(self) -> None:
        try:
            which = WhichDiagnosticTest.from_description(self.criteria_value)
            idx = getattr(self, "criteria_index", 0)
            xt = f"xt{idx}"
            xtp = f"xt{idx - 1}"

            self.sql_from.append(
                f"INNER JOIN external_tests_t {xt} ON {xt}.screening_subject_id = ss.screening_subject_id"
            )

            if which == WhichDiagnosticTest.ANY_TEST_IN_ANY_EPISODE:
                return

            self._add_join_to_latest_episode()

            handlers = {
                WhichDiagnosticTest.ANY_TEST_IN_LATEST_EPISODE: self._handle_any_test_in_latest_episode,
                WhichDiagnosticTest.ONLY_TEST_IN_LATEST_EPISODE: self._handle_only_test_in_latest_episode,
                WhichDiagnosticTest.ONLY_NOT_VOID_TEST_IN_LATEST_EPISODE: self._handle_only_test_in_latest_episode,
                WhichDiagnosticTest.LATEST_TEST_IN_LATEST_EPISODE: self._handle_latest_test_in_latest_episode,
                WhichDiagnosticTest.LATEST_NOT_VOID_TEST_IN_LATEST_EPISODE: self._handle_latest_test_in_latest_episode,
                WhichDiagnosticTest.EARLIEST_NOT_VOID_TEST_IN_LATEST_EPISODE: self._handle_earliest_test_in_latest_episode,
                WhichDiagnosticTest.EARLIER_TEST_IN_LATEST_EPISODE: self._handle_earlier_or_later_test,
                WhichDiagnosticTest.LATER_TEST_IN_LATEST_EPISODE: self._handle_earlier_or_later_test,
            }

            if which in handlers:
                handlers[which](which, xt, xtp)
            else:
                raise ValueError(f"Unsupported diagnostic test type: {which}")

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    def _handle_any_test_in_latest_episode(self, which, xt, _):
        self.sql_from.append(f"AND {xt}.subject_epis_id = ep.subject_epis_id")

    def _handle_only_test_in_latest_episode(self, which, xt, _):
        self.sql_from.append(f"AND {xt}.subject_epis_id = ep.subject_epis_id")
        if which == WhichDiagnosticTest.ONLY_NOT_VOID_TEST_IN_LATEST_EPISODE:
            self.sql_from.append(f"AND {xt}.void = 'N'")
        self.sql_from.append(
            f"""AND NOT EXISTS (
        SELECT 'xto' FROM external_tests_t xto
        WHERE xto.screening_subject_id = ss.screening_subject_id
        {'AND xto.void = \'N\'' if which == WhichDiagnosticTest.ONLY_NOT_VOID_TEST_IN_LATEST_EPISODE else ''}
        AND xto.subject_epis_id = ep.subject_epis_id
        AND xto.ext_test_id != {xt}.ext_test_id )"""
        )

    def _handle_latest_test_in_latest_episode(self, which, xt, _):
        self.sql_from.append(
            f"""AND {xt}.ext_test_id = (
        SELECT MAX(xtx.ext_test_id) FROM external_tests_t xtx
        WHERE xtx.screening_subject_id = ss.screening_subject_id
        {'AND xtx.void = \'N\'' if which == WhichDiagnosticTest.LATEST_NOT_VOID_TEST_IN_LATEST_EPISODE else ''}
        AND xtx.subject_epis_id = ep.subject_epis_id )"""
        )

    def _handle_earliest_test_in_latest_episode(self, which, xt, _):
        self.sql_from.append(
            f"""AND {xt}.ext_test_id = (
        SELECT MIN(xtn.ext_test_id) FROM external_tests_t xtn
        WHERE xtn.screening_subject_id = ss.screening_subject_id
        AND xtn.void = 'N'
        AND xtn.subject_epis_id = ep.subject_epis_id )"""
        )

    def _handle_earlier_or_later_test(self, which, xt, xtp):
        if getattr(self, "criteria_index", 0) == 0:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)
        comparator = (
            "<" if which == WhichDiagnosticTest.EARLIER_TEST_IN_LATEST_EPISODE else ">"
        )
        self.sql_from.append(f"AND {xt}.ext_test_id {comparator} {xtp}.ext_test_id")
