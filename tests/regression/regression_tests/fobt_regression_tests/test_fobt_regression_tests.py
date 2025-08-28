import pytest
from playwright.sync_api import Page
from utils.user_tools import UserTools


@pytest.mark.fobt_regression_tests
def test_scenario_1(page: Page) -> None:
    """
    Scenario: 1: Non-response to test kits
    This scenario tests two of the episode closures for non-response to test kits: from the initial kit and from a retest kit.  It includes an episode reopen.

    Scenario summary:
    > Create a new subject in the FOBT age range > Inactive
    > Run the FOBT failsafe trawl > Call
    > Run the database transition to invite them for FOBT screening > S1(1.1)
    > Process S1 letter batch > S9 (1.1)
    > Run timed events > creates S9 letter (1.1)
    > Process S9 letter batch > S10 (1.1)
    > Run timed events > S19 (1.2)
    > Process S19 letter batch > S44 > C203 (1.2)
    > Check recall [SSCL1]
    > Reopen to log a kit > S10 (1.1) > S43 (1.2)
    > Read kit with SPOILT result > S3 (1.4)
    > Process S3 letter batch > S11 (1.4)
    > Run timed events > creates S11 letter batch (1.4)
    > Process S11 letter batch > S20 (1.4)
    > Run timed events > creates S20 letter batch (1.4)
    > Process S20 letter batch > S47 (1.4) > C203 (1.13)
    > Check recall [SSCL1]
    """
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")
