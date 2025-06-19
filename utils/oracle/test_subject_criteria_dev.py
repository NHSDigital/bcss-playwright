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

# === Test: KIT_HAS_ANALYSER_RESULT_CODE — yes ===
builder = MockSelectionBuilder(
    SubjectSelectionCriteriaKey.KIT_HAS_ANALYSER_RESULT_CODE, "yes"
)
builder._add_criteria_kit_has_analyser_result_code()
print("=== KIT_HAS_ANALYSER_RESULT_CODE — yes ===")
print(builder.dump_sql(), end="\n\n")

# === Test: KIT_HAS_ANALYSER_RESULT_CODE — no ===
builder = MockSelectionBuilder(
    SubjectSelectionCriteriaKey.KIT_HAS_ANALYSER_RESULT_CODE, "no"
)
builder._add_criteria_kit_has_analyser_result_code()
print("=== KIT_HAS_ANALYSER_RESULT_CODE — no ===")
print(builder.dump_sql(), end="\n\n")
