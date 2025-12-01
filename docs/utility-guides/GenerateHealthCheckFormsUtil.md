# Utility Guide: Generate Health Check Forms

The **Generate Health Check Forms utility** provides helper methods for generating health check forms and inviting surveillance subjects early in BCSS.<br>
This utility interacts with the UI and database to automate the process of producing health check forms for eligible subjects.

## Table of Contents

- [Utility Guide: Generate Health Check Forms](#utility-guide-generate-health-check-forms)
  - [Table of Contents](#table-of-contents)
  - [Summary of Utility Methods](#summary-of-utility-methods)
  - [Main Methods](#main-methods)
    - [`invite_surveillance_subjects_early`](#invite_surveillance_subjects_early)
    - [`find_early_invite_subjects`](#find_early_invite_subjects)
  - [Prerequisites](#prerequisites)
  - [Supporting Classes](#supporting-classes)
  - [Example Usage](#example-usage)

---

## Summary of Utility Methods

| Method                              | Purpose                                                                 | Key Arguments                | Expected Behaviour |
|--------------------------------------|-------------------------------------------------------------------------|------------------------------|--------------------|
| `invite_surveillance_subjects_early` | Generates health check forms and invites a surveillance subject early.   | `screening_centre_id` (`str`)| Navigates UI, recalculates due count, finds subject, generates forms, returns NHS number. |
| `find_early_invite_subjects`         | Finds an eligible subject for early surveillance invitation.             | `screening_centre_id` (`str`), `surveillance_due_count_date` (`str`) | Returns NHS number of eligible subject. |

---

## Main Methods

### `invite_surveillance_subjects_early`

Generates health check forms and invites a surveillance subject early by automating the relevant UI steps.

**Arguments:**

- `screening_centre_id` (`str`): The screening centre ID for which to generate forms and invite a subject.

**How it works:**

1. Navigates to the Surveillance page and then to the Produce Health Check Forms page.
2. Sets the "Surveillance Due Count Volume" to 1.
3. Clicks the "Recalculate" button to update the due count.
4. Retrieves the current "Surveillance Due Count Date" from the UI.
5. Finds an eligible subject for early invitation using the due count date and centre ID.
6. Clicks the "Generate Health Check Forms" button.
7. Returns the NHS number of the invited subject.

**Returns:**

- `str`: The NHS number of the early-invite subject.

---

### `find_early_invite_subjects`

Finds an eligible subject for early surveillance invitation based on the due count date and screening centre.

**Arguments:**

- `screening_centre_id` (`str`): The screening centre ID.
- `surveillance_due_count_date` (`str`): The due count date as a string.

**How it works:**

1. Uses the `SubjectRepository` to query the database for a subject eligible for early surveillance invitation.
2. Returns the NHS number of the found subject.

**Returns:**

- `str`: The NHS number of the eligible subject.

---

## Prerequisites

Before using the Generate Health Check Forms utility, ensure that the following prerequisites are met:

1. **UI Access**: The utility requires access to the BCSS UI and a valid Playwright `Page` object.
2. **Database Access**: The utility uses the `SubjectRepository` to query the database for eligible subjects.
3. **Screening Centre ID**: You must provide a valid screening centre ID for which to generate forms and invite subjects.

---

## Supporting Classes

These classes are required by the utility:

- `BasePage` — Provides navigation and common UI actions.
- `SurveillancePage` — Handles navigation to the surveillance section.
- `ProduceHealthCheckFormsPage` — Interacts with the health check forms UI.
- `SubjectRepository` — Queries the database for eligible subjects.

---

## Example Usage

```python
from utils.generate_health_check_forms_util import GenerateHealthCheckFormsUtil

# Assume you have a Playwright page object and a valid screening centre ID
page = ...  # Playwright Page object
screening_centre_id = "12345"

# Create the utility
health_check_util = GenerateHealthCheckFormsUtil(page)

# Invite a surveillance subject early and generate health check forms
nhs_no = health_check_util.invite_surveillance_subjects_early(screening_centre_id)

print(f"Invited subject NHS number: {nhs_no}")
```
