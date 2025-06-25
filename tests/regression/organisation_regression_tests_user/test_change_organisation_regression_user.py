import pytest
from utils.user_tools import UserTools
from playwright.sync_api import Page, expect
from pages.organisations.organisations_page import OrganisationSwitchPage


@pytest.mark.regression
@pytest.mark.organisation_switch
def test_user_can_switch_between_organisations(page: Page):
    """
    Feature: Change Organisation

    Scenario: Check an English user, that has multiple organisations is able to switch between them
    Given I log in to BCSS "England" as user role "MultiOrgUser"
    When I change organisation
    Then I will be logged in as the alternative organisation.
    """

    # Log in as MultiOrgUser
    UserTools.user_login(page, "Specialist Screening Practitioner at BCS009")

    org_switch_page = OrganisationSwitchPage(page)

    # Switch between all available organisations by their ids (no hardcoded values)
    org_switch_page.switch_between_organisations()



