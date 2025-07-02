# Utility Guide: Note Test Utilities

The **Note Test Utility** module provides reusable helper functions for verifying and comparing note data during test automation of screening subjects in BCSS.  
It includes helpers for:

1. Searching for a subject by NHS number.
2. Fetching supporting notes from the database.
3. Verifying that a note matches expected values from the DB or UI.
4. Confirming that a removed note is archived properly as obsolete.

## Table of Contents

- [Utility Guide: Note Test Utilities](#utility-guide-note-test-utilities)
  - [Table of Contents](#table-of-contents)
  - [Using These Utilities](#using-these-utilities)

---

## Using These Utilities

You can import functions into your test files like so:

```python
from utils.note_test_util import (
    search_subject_by_nhs,
    fetch_supporting_notes_from_db,
    verify_note_content_matches_expected,
    verify_note_content_ui_vs_db,
    verify_note_removal_and_obsolete_transition,
)
