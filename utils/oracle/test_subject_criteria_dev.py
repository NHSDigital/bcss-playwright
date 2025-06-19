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


# === Test: DIAGNOSTIC_TEST_INTENDED_EXTENT (null) ===
b = make_builder(SubjectSelectionCriteriaKey.DIAGNOSTIC_TEST_INTENDED_EXTENT, "null")
b._add_criteria_diagnostic_test_intended_extent()
print("=== DIAGNOSTIC_TEST_INTENDED_EXTENT (null) ===")
print(b.dump_sql(), end="\n\n")

# === Test: DIAGNOSTIC_TEST_INTENDED_EXTENT (not null) ===
b = make_builder(
    SubjectSelectionCriteriaKey.DIAGNOSTIC_TEST_INTENDED_EXTENT, "not null", index=1
)
b._add_criteria_diagnostic_test_intended_extent()
print("=== DIAGNOSTIC_TEST_INTENDED_EXTENT (not null) ===")
print(b.dump_sql(), end="\n\n")

# === Test: DIAGNOSTIC_TEST_INTENDED_EXTENT (partial) ===
b = make_builder(
    SubjectSelectionCriteriaKey.DIAGNOSTIC_TEST_INTENDED_EXTENT, "partial", index=2
)
b._add_criteria_diagnostic_test_intended_extent()
print("=== DIAGNOSTIC_TEST_INTENDED_EXTENT (partial) ===")
print(b.dump_sql(), end="\n\n")
