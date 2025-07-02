import pytest
from playwright.sync_api import Page
from utils.user_tools import UserTools
from pages.organisations.organisations_page import (
    OrganisationSwitchPage,
    NoOrganisationAvailableError,
    OrganisationNotSelectedError,
    ContinueButtonNotFoundError,
)

@pytest.mark.regression
@pytest.mark.organisation_switch
def test_user_can_switch_between_two_organisations_using_continue_button(page: Page):
    """
    Scenario:
    User switches from Org 1 → Continue → Home → 'Select Organisation' → Org 2 → Continue → Home → Return.
    Verifies switch success using aria role-based 'Continue' button logic.
    """
    UserTools.user_login(page, "Specialist Screening Practitioner at BCS009")
    org_page = OrganisationSwitchPage(page)

    try:
        org_ids = org_page.get_available_organisation_ids()
        org1, org2 = org_ids[:2]

        # Select Org 1 → Continue → Home
        org_page.select_organisation_by_id(org1)
        org_page.click_continue_button()
        selected_1 = org_page.get_selected_organisation_id()
        assert selected_1 == org1, f"Expected org '{org1}', got '{selected_1}'"

        # Return to Change Org screen
        org_page.return_to_change_org_page()

        # Select Org 2 → Continue → Home
        org_page.select_organisation_by_id(org2)
        org_page.click_continue_button()
        selected_2 = org_page.get_selected_organisation_id()
        assert selected_2 == org2, f"Expected org '{org2}', got '{selected_2}'"
        assert selected_1 != selected_2, "Organisation switch did not occur."

    except NoOrganisationAvailableError:
        pytest.skip("Skipping test — fewer than two organisations available.")
    except (ContinueButtonNotFoundError, OrganisationNotSelectedError) as e:
        page.screenshot(path="org_switch_failure.png")
        pytest.fail(f"Test failed: {e}")
    except Exception as e:
        page.screenshot(path="unexpected_error.png")
        pytest.fail(f"Unexpected error: {e}")
