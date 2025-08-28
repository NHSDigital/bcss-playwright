import pytest
import logging
import datetime
from playwright.sync_api import Page
from utils.oracle.subject_creation_util import CreateSubjectSteps
from utils.user_tools import UserTools
from utils.subject_assertion import subject_assertion
from pages.base_page import BasePage

@pytest.mark.fobt_regression_tests
def test_scenario_2(page: Page) -> None:
    """
    Scenario: 2: Normal kit reading

    S1-S9-S10-S43-S2-S158-S159-C203 [SSCL4a]

    This scenario tests the basic scenario where a subject returns their initial test kit which gives a normal result.

    Scenario summary:

    > Create a new subject in the FOBT age range > Inactive
    > Run the FOBT failsafe trawl > Call
    > Run the database transition to invite them for FOBT screening > S1(1.1)
    > Process S1 letter batch > S9 (1.1)
    > Run timed events > creates S9 letter (1.1)
    > Process S9 letter batch > S10 (1.1)
    > Log kit > S43 (1.2)
    > Read kit with NORMAL result > S2 (1.3)
    > Process S2 letter batch > S158 (1.3)
    > Process S158 letter batch > S159 (1.3) > C203 (1.13)
    > Check recall [SSCL4a]
    """

    # Given I log in to BCSS "England" as user role "Hub Manager"
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")

    # Go to screening subject search page
    base_page = BasePage(page)
    base_page.click_main_menu_link()
    base_page.go_to_screening_subject_search_page()

    # And I create a subject that meets the following criteria:
    # Age (y/d)                   	66/130
    # Active GP practice in hub/SC	BCS01/BCS001
    requirements = {
        "age (y/d)": "66/130",
        "active gp practice in hub/sc": "BCS01/BCS001",
    }
    nhs_no = CreateSubjectSteps().create_custom_subject(requirements)
    if nhs_no is None:
        pytest.fail("Failed to create subject: NHS number not returned.")

    # Then Comment: NHS number
    logging.info(f"Created subject's NHS number: {nhs_no}")

    # And my subject has been updated as follows:
    # Subject age         	66
    # Subject has episodes	No
    # Screening status     	Inactive
    subject_assertion(
        nhs_no,
        {
            "age (y/d)": "66/130",
            "subject has episodes": "No",
            "screening status": "Inactive",
        },
    )

    # When I run the FOBT failsafe trawl for my subject

    # Then my subject has been updated as follows:
    # Subject has episodes             	No
    # Screening due date               	Last birthday
    # Screening due date date of change	Today
    # Screening due date reason         	Failsafe Trawl
    # Screening status                 	Call
    # Screening status date of change   	Today
    # Screening status reason           	Failsafe Trawl
    today = datetime.datetime.now().strftime("%d/%m/%Y")

    subject_assertion(
        nhs_no,
        {
            "subject has episodes": "No",
            "Screening Due Date": "Last Birthday",
            "Screening due date date of change": today,
            "Screening Due Date Reason": "Failsafe Trawl",
            "screening status": "Call",
            "Screening Status Date of Change": today,
            "Screening Status Reason": "Failsafe Trawl",
        },
    )

    # When I invite my subject for FOBT screening
    
    # Then my subject has been updated as follows:
    # Latest event status     	S1 Selected for Screening
    # Latest episode kit class	FIT
    # Latest episode type     	FOBT
    subject_assertion(
        nhs_no,
        {
            "latest event status": "S1 Selected for Screening",
            "latest episode kit class": "FIT",
            "latest episode type": "FOBT",
        },
    )
    # Then there is a "S1" letter batch for my subject with the exact title "Pre-invitation (FIT)"

    # When I process the open "S1" letter batch for my subject

    # Then my subject has been updated as follows:
    # Latest event status	S9 Pre-invitation Sent
    subject_assertion(
        nhs_no,
        {
            "latest event status": "S9 Pre-invitation Sent",
        },
    )

    # When I run Timed Events for my subject
    # Then there is a "S9" letter batch for my subject with the exact title "Invitation & Test Kit (FIT)"

    # When I process the open "S9" letter batch for my subject

    # Then my subject has been updated as follows:
    # Latest event status	S10 Invitation & Test Kit Sent
    subject_assertion(
        nhs_no,
        {
            "latest event status": "S10 Invitation & Test Kit Sent",
        },
    )
    # When I log my subject's latest unlogged FIT kit

    # Then my subject has been updated as follows:
    # Latest event status	S43 Kit Returned and Logged (Initial Test)
    subject_assertion(
        nhs_no,
        {
            "latest event status": "S43 Kit Returned and Logged (Initial Test)",
        },
    )

    # When I read my subject's latest logged FIT kit as "NORMAL"

    # Then my subject has been updated as follows:
    # Latest event status	S2 Normal
    subject_assertion(
        nhs_no,
        {
            "latest event status": "S2 Normal",
        },
    )
    # And there is a "S2" letter batch for my subject with the exact title "Subject Result (Normal)"

    # When I process the open "S2" letter batch for my subject

    # Then my subject has been updated as follows:
    # Latest event status	S158 Subject Discharge Sent (Normal)
    subject_assertion(
        nhs_no,
        {
            "latest event status": "S158 Subject Discharge Sent (Normal)",
        },
    )
    # And there is a "S158" letter batch for my subject with the exact title "GP Result (Normal)"

    # When I process the open "S158" letter batch for my subject

    # Then my subject has been updated as follows:
    # Calculated screening due date           	2 years from latest S158 event
    # Calculated Lynch due date               	Null
    # Calculated Surveillance due date         	Null
    # Ceased confirmation date                 	Null
    # Ceased confirmation details             	Null
    # Ceased confirmation user ID             	Null
    # Clinical reason for cease               	Null
    # Latest episode accumulated result       	Definitive normal FOBt outcome
    # Latest episode recall calculation method	Date of last patient letter
    # Latest episode recall episode type       	FOBT screening
    # Latest episode recall surveillance type 	Null
    # Latest episode status                   	Closed
    # Latest episode status reason             	Episode Complete
    # Latest event status                     	S159 GP Discharge Sent (Normal)
    # Lynch due date                           	Null
    # Lynch due date date of change           	Null
    # Lynch due date reason                   	Null
    # Screening status                         	Recall
    # Screening status date of change
    # Not checking as status may or may not have changed
    # Screening status reason                 	Recall
    # Screening due date                       	Calculated screening due date
    # Screening due date date of change       	Today
    # Screening due date reason               	Recall
    # Surveillance due date                   	Null
    # Surveillance due date date of change     	Unchanged
    # Surveillance due date reason             	Unchanged
    subject_assertion(
        nhs_no,
        {
            "calculated screening due date": "2 years from latest S158 event",
            "calculated lynch due date": None,
            "calculated surveillance due date": None,
            "ceased confirmation date": None,
            "ceased confirmation details": None,
            "ceased confirmation user ID": None,
            "clinical reason for cease": None,
            "latest episode accumulated result": "Definitive normal FOBt outcome",
            "latest episode recall calculation method": "Date of last patient letter",
            "latest episode recall episode type": "FOBT screening",
            "latest episode recall surveillance type": None,
            "latest episode status": "Closed",
            "latest episode status reason": "Episode Complete",
            "latest event status": "S159 GP Discharge Sent (Normal)",
            "lynch due date": None,
            "lynch due date date of change": None,
            "lynch due date reason": None,
            "screening status": "Recall",
            # Screening status date of change intentionally omitted
            "screening status reason": "Recall",
            "screening due date": "Calculated screening due date",
            "screening due date date of change": "Today",
            "screening due date reason": "Recall",
            "surveillance due date": None,
            "surveillance due date date of change": "Unchanged",
            "surveillance due date reason": "Unchanged",
        },
    )
