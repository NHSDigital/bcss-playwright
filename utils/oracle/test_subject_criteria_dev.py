"""
test_subject_criteria_dev.py

This is a development-only script used to manually test and debug individual
criteria methods from the SubjectSelectionQueryBuilder or MockSelectionBuilder.

It allows developers to:
    - Pass in a specific SubjectSelectionCriteriaKey and value
    - Invoke selection logic (e.g. _add_criteria_* methods)
    - Inspect the resulting SQL fragments using `dump_sql()`

Note:
    This script is intended for local use only and should NOT be committed with
    test content. Add it to your .gitignore after cloning or copying the template.

See Also:
    - mock_selection_builder.py: Test harness for isolated builder method evaluation
    - subject_selection_query_builder.py: The production SQL builder implementation
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
print("PYTHONPATH set to:", sys.path[0])
from mock_selection_builder import MockSelectionBuilder
from classes.subject_selection_criteria_key import SubjectSelectionCriteriaKey

# === Example usage ===
# Replace the examples below with your tests for the method you want to test


# Helper for mock sequencing
def make_builder(key, value, index=0):
    b = MockSelectionBuilder(key, value)
    b.criteria_index = index
    return b


# === Test: ANY_TEST_IN_ANY_EPISODE ===
b = make_builder(
    SubjectSelectionCriteriaKey.WHICH_DIAGNOSTIC_TEST, "any_test_in_any_episode"
)
b._add_join_to_diagnostic_tests()
print("=== ANY_TEST_IN_ANY_EPISODE ===")
print(b.dump_sql(), end="\n\n")

# === Test: EARLIER_TEST_IN_LATEST_EPISODE ===
b = make_builder(
    SubjectSelectionCriteriaKey.WHICH_DIAGNOSTIC_TEST,
    "earlier_test_in_latest_episode",
    index=1,
)
b._add_join_to_diagnostic_tests()
print("=== EARLIER_TEST_IN_LATEST_EPISODE ===")
print(b.dump_sql(), end="\n\n")

# === Test: ONLY_NOT_VOID_TEST_IN_LATEST_EPISODE ===
b = make_builder(
    SubjectSelectionCriteriaKey.WHICH_DIAGNOSTIC_TEST,
    "only_not_void_test_in_latest_episode",
)
b._add_join_to_diagnostic_tests()
print("=== ONLY_NOT_VOID_TEST_IN_LATEST_EPISODE ===")
print(b.dump_sql(), end="\n\n")

# Add more as needed for full coverage
