import pytest
from playwright.sync_api import Page
from utils.user_tools import UserTools
from classes.user import User
from classes.subject import Subject
from pages.base_page import BasePage
from pages.screening_subject_search.subject_demographic_page import (
    SubjectDemographicPage,
)
from pages.logout.log_out_page import LogoutPage
from utils.screening_subject_page_searcher import (
    search_subject_demographics_by_nhs_number,
)
from utils.oracle.oracle import OracleDB
from utils.oracle.oracle_specific_functions import (
    check_if_subject_has_temporary_address,
)
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
import logging
from faker import Faker
from datetime import datetime, timedelta

# Further Reading
# --------
# The references used within this feature are outlined in detail in the following directory:
# Q:\DEV\Services\BCSS\System Specification\Screening Subject
# The spreadsheet itself is called: Screening Subject Data Items (Use the latest version)

# @BCSSAdditionalTests
# Feature: Manual UI Unceasing Checks - Existing Kit Present

# A manually ceased subject with unlogged kits can be unceased as part of the late response "log an existing kit" process.

# Background: I log in as a hub manager for BCSS England for all tests
# Given I log in to BCSS "England" as user role "Hub Manager"
@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page) -> str:
    """
    Before every test is executed, this fixture:
    - Logs into BCSS as a Screening Centre Manager at BCS001
    - Navigates to the screening subject search page
    """
    nhs_no = obtain_test_data_nhs_no()
    logging.info(f"Selected NHS Number: {nhs_no}")
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_demographics_by_nhs_number(page, nhs_no)
    return nhs_no


# Scenario: Subject is within eligible age range, is next due to be screened in the past and has an outstanding kit > SSUN9.8 Opt-in log a kit
# Given there is a subject who meets the following criteria:
# 	| Latest Episode Type       | FOBT                 |
# 	| Latest Episode Status     | Closed               |
# 	| Has GP Practice           | Yes - Active         |
# 	| Screening Status          | Recall               |
# 	| Subject Age               | Between 60 and 73    |
# 	| Screening Due Date        | < today              |
# 	| Subject has Unlogged Kits | Yes - latest episode |
# 	| Subject Lower FOBT Age    | default              |
# 	| Note count                | < 200                |
# 	And I manually cease the subject with reason "Informed Dissent"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Ceased confirmation date    | Today            |
# 	| Ceased confirmation details | Not null         |
# 	| Ceased confirmation user ID | Not null         |
# 	| Clinical reason for cease   | Null             |
# 	| Screening Status            | Ceased           |
# 	| Screening Status Reason     | Informed Dissent |
# When I manually uncease the subject to "log an existing kit"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date             | Unchanged                           |
# 	| Calculated surveillance due date     | Unchanged                           |
# 	| Ceased confirmation date             | Null                                |
# 	| Ceased confirmation details          | Null                                |
# 	| Ceased confirmation user ID          | Null                                |
# 	| Clinical reason for cease            | Null                                |
# 	| Previous Screening Status            | Ceased                              |
# 	| Screening Due Date                   | Today                               |
# 	| Screening Due Date Reason            | Opt (back) into Screening Programme |
# 	| Screening Due Date Date Of Change    | Today                               |
# 	| Screening Status                     | Opt-in                              |
# 	| Screening Status Date of Change      | Today                               |
# 	| Screening Status Reason              | Opt (back) into Screening Programme |
# 	| Subject Lower FOBT Age               | Default                             |
# 	| Surveillance Due Date                | Null                                |
# 	| Surveillance due date reason         | Null                                |
# 	| Surveillance due date date of change | Unchanged                           |


# Scenario: Subject eligible for uncease under late response rules and is within eligible age range  > SSUN9.8 Opt-in log a kit
# Given there is a subject who meets the following criteria:
# 	| Latest Episode Type                       | FOBT                 |
# 	| Latest Episode Status                     | Closed               |
# 	| Has GP Practice                           | Yes - Active         |
# 	| Latest Episode ended                      | > 6 months ago       |
# 	| Latest Episode has Significant Kit Result | No                   |
# 	| Screening Status                          | Recall               |
# 	| Subject Age                               | Between 60 and 73    |
# 	| Subject has Unlogged Kits                 | Yes - latest episode |
# 	| Subject Lower FOBT Age                    | default              |
# 	| Note count                                | < 200                |
# 	And I manually cease the subject with reason "Informed Dissent"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Ceased confirmation date    | Today            |
# 	| Ceased confirmation details | Not null         |
# 	| Ceased confirmation user ID | Not null         |
# 	| Clinical reason for cease   | Null             |
# 	| Screening Status            | Ceased           |
# 	| Screening Status Reason     | Informed Dissent |
# When I manually uncease the subject to "log an existing kit"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date             | Unchanged                           |
# 	| Calculated surveillance due date     | Unchanged                           |
# 	| Ceased confirmation date             | Null                                |
# 	| Ceased confirmation details          | Null                                |
# 	| Ceased confirmation user ID          | Null                                |
# 	| Clinical reason for cease            | Null                                |
# 	| Previous Screening Status            | Ceased                              |
# 	| Screening Due Date                   | Today                               |
# 	| Screening Due Date Reason            | Opt (back) into Screening Programme |
# 	| Screening Due Date Date Of Change    | Today                               |
# 	| Screening Status                     | Opt-in                              |
# 	| Screening Status Date of Change      | Today                               |
# 	| Screening Status Reason              | Opt (back) into Screening Programme |
# 	| Subject Lower FOBT Age               | Default                             |
# 	| Surveillance Due Date                | Null                                |
# 	| Surveillance due date reason         | Null                                |
# 	| Surveillance due date date of change | Unchanged                           |

# @ignore
# Scenario Outline: Subject (<Age>) is below eligible age range with history > SSUN9.13 Opt-in (Awaiting failsafe)
# # THIS SCENARIO DOESN'T TEST UNCEASING BY LOGGING A KIT SO IS PROBABLY JUST A DUPLICATE OF OTHER MANUAL UNCEASE SCENARIOS
# Given there is a subject who meets the following criteria:
# 	| Latest Episode Type                  | FOBT                 |
# 	| Latest Episode Status                | Closed               |
# 	| Has GP Practice                      | Yes - Active         |
# 	| Screening Status                     | Recall               |
# 	| Subject Age                          | < 73                 |
# 	| Screening Due Date                   | < today              |
# 	| Subject has Unlogged Kits            | Yes - latest episode |
# 	| Subject Lower FOBT Age               | default              |
# 	| Note count                           | < 200                |
# 	| Subject has unprocessed SSPI updates | No                   |
# 	| Subject has user dob updates         | No                   |

# 	And I receive an SSPI update to change their date of birth to "<Age>" years old
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Subject Age | <Age> |
# 	And I manually cease the subject with reason "Informed Dissent"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Ceased confirmation date    | Today            |
# 	| Ceased confirmation details | Not null         |
# 	| Ceased confirmation user ID | Not null         |
# 	| Clinical reason for cease   | Null             |
# 	| Screening Status            | Ceased           |
# 	| Screening Status Reason     | Informed Dissent |
# Then I "cannot" log an existing kit for the subject
# When I manually uncease the subject to "opt them into the screening programme"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date             | Unchanged                           |
# 	| Calculated surveillance due date     | Unchanged                           |
# 	| Ceased confirmation date             | Null                                |
# 	| Ceased confirmation details          | Null                                |
# 	| Ceased confirmation user ID          | Null                                |
# 	| Clinical reason for cease            | Null                                |
# 	| Previous Screening Status            | Ceased                              |
# 	| Screening Due Date                   | Null                                |
# 	| Screening Due Date Reason            | Awaiting Failsafe                   |
# 	| Screening Due Date Date Of Change    | Today                               |
# 	| Screening Status                     | Opt-in                              |
# 	| Screening Status Date of Change      | Today                               |
# 	| Screening Status Reason              | Opt (back) into Screening Programme |
# 	| Subject Lower FOBT Age               | Default                             |
# 	| Surveillance Due Date                | Null                                |
# 	| Surveillance due date reason         | Null                                |
# 	| Surveillance due date date of change | Unchanged                           |
# 	And I remove the age extension age <Age> start date from my subject's screening centre

# Examples:
# 	| Age |
# 	| 57  |
# 	| 59  |
# 	| 55  |
# 	| 53  |
# 	| 51  |


def obtain_test_data_nhs_no() -> str:
    """
    Obtain a test subject's NHS number that matches the following criteria:
    | Subject age                   | <= 80 |
        | Subject has temporary address | No    |

    This is obtained using the Subject Selection Query Builder.

    Returns:
        str: The NHS number of the subject that matches the criteria.
    """
    criteria = {
        "subject age": "<= 80",
        "subject has temporary address": "no",
    }
    user = User()
    subject = Subject()

    builder = SubjectSelectionQueryBuilder()

    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=1
    )

    df = OracleDB().execute_query(query, bind_vars)
    nhs_no = df.iloc[0]["subject_nhs_number"]
    return nhs_no
