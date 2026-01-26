import logging
import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page
from pages.datasets.colonoscopy_dataset_page import (
    ColonoscopyDatasetsPage,
    FitForColonoscopySspOptions,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.logout.log_out_page import LogoutPage
from pages.organisations.organisations_page import OrganisationSwitchPage
from pages.screening_subject_search.advance_surveillance_episode_page import (
    AdvanceSurveillanceEpisodePage,
)
from pages.screening_subject_search.postpone_surveillance_episode_page import (
    PostponeSurveillanceEpisodePage,
)
from pages.screening_subject_search.reopen_surveillance_episode_page import (
    ReopenSurveillanceEpisodePage,
)
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils import screening_subject_page_searcher
from utils.generate_health_check_forms_util import GenerateHealthCheckFormsUtil
from utils.sspi_change_steps import SSPIChangeSteps
from utils.subject_assertion import subject_assertion
from utils.user_tools import UserTools


@pytest.mark.skip(
    reason="Requires manual setup to create suitable subjects for surveillance postponement."
)
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.surveillance_regression_tests
def test_surveillance_scenario_7a(page: Page, general_properties: dict) -> None:
    """
    Scenario: 7a: Postpone from X500

    X500-X92-C203 [SSCL30] X900-A99

    This scenario does work, but only if you manage to invite a subject with a Surveillance due date that is in the past but less than a year ago, so we don't trip over the validation for the future date.  These are not immediately available in a cloud dev/test database, so before it can be run, Surveillance invitations must be manually run to a date within the last year.  Because this somewhat limits the usefulness of this scenario, it is flagged to be ignored by default.

    Note that for a postpone, the calculated Surveillance due date and its reason for change are set to the values entered by the user.

    Scenario summary:

    > Run surveillance invitations for 1 subject > X500 (3.1)
    > SSPI update changes subject to in-age at recall
    > Postpone the episode > X92
    > Check recall [SSCL30]
    > Reopen the episode > X900 (3.1)
    > Complete the colonoscopy assessment dataset - fit for colonoscopy
    > Suitable for colonoscopy > A99 (3.1)
    """
    # Given I log in to BCSS "England" as user role "Specialist Screening Practitioner"
    user_role = UserTools.user_login(
        page, "Specialist Screening Practitioner at BCS009 & BCS001", True
    )

    OrganisationSwitchPage(page).select_organisation_by_id("BCS001")
    OrganisationSwitchPage(page).click_continue()
    if user_role is None:
        raise ValueError("User role is none")

    # When I run surveillance invitations for 1 subject
    org_id = general_properties["eng_screening_centre_id"]
    nhs_no = GenerateHealthCheckFormsUtil(page).invite_surveillance_subjects_early(
        org_id
    )
    logging.info(f"[SUBJECT RETRIEVAL] Subject's NHS Number: {nhs_no}")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode status": "Open",
            "latest episode type": "Surveillance",
            "latest event status": "X500 Selected For Surveillance",
            "responsible screening centre code": "User's screening centre",
            "subject has unprocessed SSPI updates": "No",
            "subject has user DOB updates": "No",
        },
        user_role,
    )

    # And I receive an SSPI update to change their date of birth to "72" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 72)

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"subject age": "72"})

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I postpone the episode:
    SubjectScreeningSummaryPage(page).click_postpone_surveillance_episode_button()
    PostponeSurveillanceEpisodePage(page).postpone_surveillance_episode(
        {
            "reason": "Clinical Reason",
            "clinical reason": "Unfit for further investigation",
            "notes": "AUTO TEST: A Sufficiently long episode closure note, added by datatable.",
            "change surveillance due date": datetime.today() + timedelta(days=1),
            "reason for date change": "Patient Request",
        }
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "calculated fobt due date": "Unchanged",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "Tomorrow",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "(Any) Surveillance non-participation",
            "latest episode recall calculation method": "X92 Interrupt User Date",
            "latest episode recall episode type": "Surveillance - High-risk findings",
            "latest episode recall surveillance type": "High-risk findings",
            "latest episode status": "Closed",
            "latest episode status reason": "Clinical Reason",
            "latest event status": "X92 Close Surveillance Episode via interrupt",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "pre-interrupt event status": "X500 Selected For Surveillance",
            "screening due date": "Null",
            "screening due date date of change": "Unchanged",
            "screening due date reason": "Unchanged",
            "screening status": "Surveillance",
            "screening status date of change": "Unchanged",
            "screening status reason": "Unchanged",
            "surveillance due date": "Calculated Surveillance due date",
            "surveillance due date date of change": "Today",
            "surveillance due date reason": "Patient Request",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I reopen the subject's episode for "Reopen episode for correction"
    SubjectScreeningSummaryPage(page).click_reopen_surveillance_episode_button()
    ReopenSurveillanceEpisodePage(page).click_reopen_episode_for_correction_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "calculated fobt due date": "Null",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "As at episode start",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "Null",
            "latest episode includes event code": "E63 Reopen episode for correction",
            "latest episode recall calculation method": "X92 Interrupt User Date",
            "latest episode recall episode type": "Null",
            "latest episode recall surveillance type": "High-risk findings",
            "latest episode status": "Open",
            "latest episode status reason": "Null",
            "latest event status": "X900 Surveillance Episode reopened",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Unchanged",
            "screening due date reason": "Unchanged",
            "screening status": "Surveillance",
            "screening status date of change": "Unchanged",
            "screening status reason": "Unchanged",
            "surveillance due date": "Calculated surveillance due date",
            "surveillance due date date of change": "Today",
            "surveillance due date reason": "Reopened episode",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I edit the Colonoscopy Assessment Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_colonoscopy_show_datasets()

    # And I update the Colonoscopy Assessment Dataset with the following values:
    ColonoscopyDatasetsPage(page).select_fit_for_colonoscopy_option(
        FitForColonoscopySspOptions.YES
    )
    ColonoscopyDatasetsPage(page).click_dataset_complete_radio_button_yes()

    # And I save the Colonoscopy Assessment Dataset
    ColonoscopyDatasetsPage(page).save_dataset()

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I advance the subject's episode for "Suitable for Endoscopic Test"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_suitable_for_endoscopic_test_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A99 Suitable for Endoscopic Test",
        },
    )

    LogoutPage(page).log_out()
