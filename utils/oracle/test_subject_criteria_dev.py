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

# === Test: SUBJECT_HAS_KIT_NOTES — yes ===
builder = MockSelectionBuilder(SubjectSelectionCriteriaKey.SUBJECT_HAS_KIT_NOTES, "yes")
builder._add_criteria_subject_has_kit_notes()
print("=== SUBJECT_HAS_KIT_NOTES — yes ===")
print(builder.dump_sql(), end="\n\n")

# === Test: SUBJECT_HAS_KIT_NOTES — no ===
builder = MockSelectionBuilder(SubjectSelectionCriteriaKey.SUBJECT_HAS_KIT_NOTES, "no")
builder._add_criteria_subject_has_kit_notes()
print("=== SUBJECT_HAS_KIT_NOTES — no ===")
print(builder.dump_sql(), end="\n\n")
