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
from classes.episode_type import EpisodeType  # Add this for the third test

# === Example usage ===
# Replace the examples below with the method you want to test

# === Test: LATEST_EPISODE_HAS_REFERRAL_DATE — yes ===
builder = MockSelectionBuilder(
    SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_REFERRAL_DATE, "yes"
)
builder._add_criteria_has_referral_date()
print("=== LATEST_EPISODE_HAS_REFERRAL_DATE — yes ===")
print(builder.dump_sql(), end="\n\n")

# === Test: LATEST_EPISODE_HAS_REFERRAL_DATE — no ===
builder = MockSelectionBuilder(
    SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_REFERRAL_DATE, "no"
)
builder._add_criteria_has_referral_date()
print("=== LATEST_EPISODE_HAS_REFERRAL_DATE — no ===")
print(builder.dump_sql(), end="\n\n")

# === Test: LATEST_EPISODE_HAS_REFERRAL_DATE — past ===
builder = MockSelectionBuilder(
    SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_REFERRAL_DATE, "past"
)
builder._add_criteria_has_referral_date()
print("=== LATEST_EPISODE_HAS_REFERRAL_DATE — past ===")
print(builder.dump_sql(), end="\n\n")

# === Test: LATEST_EPISODE_HAS_REFERRAL_DATE — more_than_28_days_ago ===
builder = MockSelectionBuilder(
    SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_REFERRAL_DATE,
    "more_than_28_days_ago",
)
builder._add_criteria_has_referral_date()
print("=== LATEST_EPISODE_HAS_REFERRAL_DATE — more_than_28_days_ago ===")
print(builder.dump_sql(), end="\n\n")

# === Test: LATEST_EPISODE_HAS_REFERRAL_DATE — within_the_last_28_days ===
builder = MockSelectionBuilder(
    SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_REFERRAL_DATE,
    "within_the_last_28_days",
)
builder._add_criteria_has_referral_date()
print("=== LATEST_EPISODE_HAS_REFERRAL_DATE — within_the_last_28_days ===")
print(builder.dump_sql(), end="\n\n")
