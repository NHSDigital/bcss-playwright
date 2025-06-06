# SubjectSelectionQueryBuilder

## Overview

This module provides the `SubjectSelectionQueryBuilder` class, which is responsible for dynamically building SQL queries to select screening subjects from an Oracle database based on a wide variety of criteria. It is designed to support complex, flexible subject selection logic for NHS Bowel Cancer Screening System (BCSS) workflows.

The builder supports criteria such as NHS number, subject age, hub code, screening centre code, GP practice linkage, screening status, and many more, including date-based and status-based filters. It also handles special cases such as "unchanged" values and supports modifiers like "NOT:" for negation.

## How to Use

**Instantiate the Builder:**

```python
builder = SubjectSelectionQueryBuilder()
```

**Call `build_subject_selection_query`:**

```python
query, bind_vars = builder.build_subject_selection_query(
    criteria,  # Dict[str, str] of selection criteria
    user,      # User object
    subject,   # Subject object (can be None)
    subjects_to_retrieve=10  # Optional: limit number of rows
)
```

1. **Execute the Query:**
   Use the returned `query` string and `bind_vars` dictionary with your database connection.

## Class: `SubjectSelectionQueryBuilder`

### Constructor

#### `__init__(self)`

Initializes internal lists for SQL clauses, bind variables, and other state needed for query construction.

---

### Main API

#### `build_subject_selection_query(self, criteria, user, subject, subjects_to_retrieve=None) -> tuple[str, dict]`

Builds the full SQL query string and bind variables dictionary based on the provided criteria, user, and subject. Handles the orchestration of clause building and applies row limits.

---

### Clause Builders

#### `_build_select_clause(self)`

Appends the SELECT clause with all required columns to the query.

#### `_build_main_from_clause(self)`

Appends the FROM clause, joining the main subject and contact tables.

#### `_start_where_clause(self)`

Appends the initial WHERE clause (`WHERE 1=1`) to simplify further AND conditions.

#### `_end_where_clause(self, subject_count: int)`

Appends a row limit clause (`FETCH FIRST {subject_count} ROWS ONLY`) to the query.

---

### Criteria Handling

#### `_add_variable_selection_criteria(self, criteria, user, subject)`

Iterates through each criterion, determines its type, and dispatches to the appropriate handler method. Handles "NOT:" modifiers, "unchanged" values, and validates the use of each criterion.

#### `_get_criteria_has_not_comparator(self, original_criteria_value: str) -> bool`

Returns `True` if the value starts with "NOT:", indicating negation.

#### `_get_criteria_value(self, original_criteria_value: str) -> str`

Strips "NOT:" if present, returning the actual value.

#### `_get_criteria_comparator(self) -> str`

Returns the SQL comparator (`=` or `!=`) based on the presence of the "NOT:" modifier.

#### `_force_not_modifier_is_invalid_for_criteria_value(self)`

Raises an error if "NOT:" is used with a criterion that does not support it.

#### `_check_if_more_than_one_criteria_value_is_valid_for_criteria_key(self)`

Validates that only one value is provided for criteria keys that do not allow multiple values.

#### `_check_if_not_modifier_is_valid_for_criteria_key(self)`

Validates that the "NOT:" modifier is allowed for the current criteria key.

---

### Criteria-Specific Methods

#### `_add_criteria_nhs_number(self)`

Adds a filter for NHS number.

#### `_add_criteria_subject_age(self)`

Adds a filter for subject age, supporting both year/day and year-only formats.

#### `_add_criteria_subject_hub_code(self, user)`

Adds a filter for the subject's hub code, handling user-organisation lookups and direct codes.

#### `_add_criteria_subject_screening_centre_code(self, user)`

Adds a filter for the subject's screening centre code, handling user-organisation lookups and direct codes.

#### `_add_criteria_has_gp_practice(self)`

Adds a filter for whether the subject has a GP practice, supporting active, inactive, and no GP.

#### `_add_criteria_has_gp_practice_linked_to_sc(self)`

Adds a filter for subjects whose GP practice is linked to a specific screening centre.

#### `_add_criteria_screening_status(self, subject)`

Adds a filter for the subject's screening status, supporting "unchanged" and specific status values.

#### `_add_criteria_previous_screening_status(self)`

Adds a filter for the subject's previous screening status.

#### `_add_criteria_screening_status_reason(self, subject)`

Adds a filter for the reason for screening status change.

#### `_add_criteria_date_field(self, subject, pathway, date_type)`

Adds a date-based filter, supporting a wide range of date logic, including special cases and relative dates.

#### `_add_criteria_date_field_special_cases(self, value, subject, pathway, date_type, date_column_name)`

Handles special date criteria such as "last birthday", "calculated due date", "unchanged", and various event-based offsets.

#### `_add_criteria_screening_due_date_reason(self, subject)`

Adds a filter for the screening due date reason, handling null, not null, unchanged, and specific value logic.

#### `_add_criteria_surveillance_due_date_reason(self, subject)`

Adds a filter for the surveillance due date reason, handling null, not null, unchanged, and specific value logic.

#### `_add_criteria_bowel_scope_due_date_reason(self, subject)`

Adds a filter for the bowel scope due date reason, handling null, not null, unchanged, and specific value logic.

#### `_add_criteria_ceased_confirmation_details(self)`

Adds a filter for ceased confirmation details, handling null, not null, and string matching.

#### `_add_criteria_ceased_confirmation_user_id(self, user)`

Adds a filter for ceased confirmation user ID, handling numeric IDs, `enum` values, and special cases.

#### `_add_criteria_clinical_reason_for_cease(self)`

Adds a filter for clinical reason for cease, supporting string and enum-based logic.

#### `_add_criteria_subject_has_event_status(self)`

Adds a filter for subjects with or without a specific event status.

#### `_add_criteria_has_unprocessed_sspi_updates(self)`

Adds a filter for subjects with unprocessed SSPI updates.

#### `_add_criteria_has_user_dob_update(self)`

Adds a filter for subjects with user date of birth updates.

---

### SQL Helper Methods

#### `_get_date_field_column_name(self, pathway, date_type) -> str`

Maps pathway and date type to the correct Oracle column name.

#### `_add_join_to_latest_episode(self)`

Adds a join to the latest episode for the subject.

#### `_add_join_to_genetic_condition_diagnosis(self)`

Adds a join to the genetic condition diagnosis table.

#### `_add_join_to_cancer_audit_dataset(self)`

Adds a join to the cancer audit dataset.

#### `_add_join_to_cancer_audit_dataset_tumor(self)`

Adds a join to the cancer audit tumor dataset.

#### `_add_join_to_cancer_audit_dataset_treatment(self)`

Adds a join to the cancer audit treatment dataset.

#### `_add_check_comparing_one_date_with_another(self, column_to_check, comparator, date_to_check_against, allow_nulls)`

Adds a date comparison clause to the query.

#### `_add_days_to_oracle_date(self, column_name, number_of_days) -> str`

Returns an Oracle SQL expression for adding days to a date.

#### `_add_months_to_oracle_date(self, column_name, number_of_months) -> str`

Returns an Oracle SQL expression for adding months to a date.

#### `_add_years_to_oracle_date(self, column_name, number_of_years) -> str`

Returns an Oracle SQL expression for adding years to a date.

#### `_add_months_or_years_to_oracle_date(self, column_name, years, number_to_add_or_subtract) -> str`

Returns an Oracle SQL expression for adding months or years to a date.

#### `_subtract_days_from_oracle_date(self, column_name, number_of_days) -> str`

Returns an Oracle SQL expression for subtracting days from a date.

#### `_subtract_months_from_oracle_date(self, column_name, number_of_months) -> str`

Returns an Oracle SQL expression for subtracting months from a date.

#### `_subtract_years_from_oracle_date(self, column_name, number_of_years) -> str`

Returns an Oracle SQL expression for subtracting years from a date.

#### `_oracle_to_date_method(self, date, format) -> str`

Returns an Oracle SQL TO_DATE expression for the given date and format.

#### `_add_check_date_is_a_period_ago_or_later(self, date_column_name, value)`

Adds a clause for date comparisons like "3 years ago", "2 months later", etc.

#### `_add_criteria_date_field_special_cases(...)`

Handles complex date-based criteria using enums and special logic.

#### `_add_check_comparing_date_with_earliest_or_latest_event_date(...)`

Adds a clause comparing a date field to the earliest or latest event date, offset by a period.

#### `_add_check_column_is_null_or_not(self, column_name, is_null)`

Adds a clause checking if a column is (not) null.

#### `_get_date_field_existing_value(self, subject, pathway, date_type) -> Optional[date]`

Returns the existing value for a date field from the subject, if available.

#### `_get_x_years_ago/later`, `_get_x_months_ago/later`, `_get_x_days_ago/later`

Helper methods for relative date calculations.

#### `_nvl_date(self, column_name) -> str`

Returns an Oracle NVL expression for a date column.

#### `_is_valid_date(self, value, date_format="%Y-%m-%d") -> bool`

Checks if a string is a valid date in the given format.

#### `single_quoted(value: str) -> str`

Returns the value wrapped in single quotes for SQL.

#### `invalid_use_of_unchanged_exception(criteria_key_name: str, reason: str)`

Returns a `SelectionBuilderException` for invalid use of "unchanged".

---

### Classes Used in This Module

#### `Subject`

Represents a screening subject, encapsulating all relevant subject data and providing methods to access screening status, due dates, and other subject-specific information.

#### `User`

Represents a user of the system, including their associated organisation and permissions.

#### `Organisation`

Represents an organisation (such as a hub or screening centre) with an organisation ID and related metadata.

#### `SubjectSelectionCriteriaKey`

An `enum` representing all possible criteria keys that can be used for subject selection. Each key includes metadata such as whether it allows the "NOT:" modifier or multiple values.

#### `ScreeningStatusType`

An `enum` representing possible screening statuses for a subject, with methods for lookup by description and value.

#### `SSReasonForChangeType`

An `enum` for reasons a subject's screening status was changed, with lookup methods.

#### `SDDReasonForChangeType`

An `enum` for reasons a subject's screening due date was changed, with lookup methods.

#### `SSDDReasonForChangeType`

An `enum` for reasons a subject's surveillance due date was changed, with lookup methods.

#### `BowelScopeDDReasonForChangeType`

An `enum` for reasons a subject's bowel scope due date was changed, with lookup methods.

#### `CeasedConfirmationDetails`

An `enum` for ceased confirmation details, supporting null/not-null and string matching.

#### `CeasedConfirmationUserId`

An `enum` for ceased confirmation user IDs, supporting special values and user lookups.

#### `ManualCeaseRequested`

An `enum` for manual cease request statuses, with case-insensitive lookup.

#### `HasGPPractice`

An `enum` for GP practice status (yes/no/active/inactive), with description-based lookup.

---

## ToDo

### Selenium Copy

- [ ] Add additional match case in `_add_variable_selection_criteria`. This is almost a direct copy of `addVariableSelectionCriteria` in the Selenium framework.
- [ ] Add any additional methods that are required by this utility: `_add_criteria_.....`.
- [ ] Create any new classes needed in the classes folder.

### General

- [ ] Add more robust type checking and error handling for all user inputs.
- [ ] Refactor repeated logic for criteria handling into reusable helper methods.
- [ ] Document all enums and supporting classes used by the builder.
- [ ] Add logging for all major decision points in query construction.
- [ ] Review and update doc strings for clarity and completeness.
- [ ] Double check `_add_criteria_date_field` against `addCriteriaDateField` to see if functionality ported over correctly. This included looking at any methods referenced in this method.

### May Require Another `Jira` Ticket

- [ ] Create tests around this utility to prove it works as intended. See if there is a current selenium test that does this.
- [ ] Create a new utility around populating the Subject and User class objects. This will be beneficial as these two objects are passed into this utility.
