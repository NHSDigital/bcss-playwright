import pytest
import logging
import pandas as pd
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from utils.oracle.oracle_specific_functions import SubjectSelector
from utils.oracle.oracle import OracleDB
from pages.base_page import BasePage
from pages.manual_cease.manual_cease_page import ManualCeasePage
from utils import screening_subject_page_searcher
from utils.user_tools import UserTools
from utils.manual_cease import EXPECT
from utils.manual_cease import (
    ScreeningStatus,
    ScreeningStatusReason,
    ScreeningDueDateReason,
    SurveillanceDueDateReason,
)
from utils.manual_cease import ManualCeaseTools
from datetime import datetime
from typing import Any


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the active batch list page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager at BCS01")

    # Go to screening subject search page
    base_page = BasePage(page)
    base_page.click_main_menu_link()
    base_page.go_to_screening_subject_search_page()


# Feature: Manually cease and uncease a Lynch subject

# These scenarios just check that manually ceasing a subject (either immediately or via a disclaimer letter) and then unceasing them correctly sets their screening status and status reason.
# Lynch due date reason is always set to "Ceased" during a manual cease, even if the LSDD is not changing.
# Set the subject's age as required for the scenario while the subject is ceased, to prevent DOB change rules from being run.  Make sure the subject has no unprocessed SSPI updates, so the DOB change is not put on one side awaiting user confirmation.


# Scenario Outline: Cease and uncease a below/in-age Lynch subject
# This scenario is for a subject who already had a Lynch diagnosis before they are manually ceased.
# Not checking the Lynch due date date of change as part of the cease, as not specifying if the Lynch due date has a value prior to that.

# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Calculated lynch due date            | <LCSDD>            |
# 	| subject has an open episode          | No                 |
# 	| Subject has episodes                 | <Has episodes>     |
# 	| Subject has lynch diagnosis          | Yes                |
# 	| Screening status                     | Lynch Surveillance |
# 	| Subject has unprocessed SSPI updates | No                 |
# When Comment: NHS number - "Scenario: <Scenario>"
# When I view the subject
# 	And I manually cease the subject with reason "<Cease reason>"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Null                                             |
# 	| Calculated lynch due date                | Unchanged                                        |
# 	| Calculated surveillance due date         | Null                                             |
# 	| Ceased confirmation date                 | Today                                            |
# 	| Ceased confirmation details              | AUTO TESTING: confirm <Cease type> manual cease  |
# 	| Ceased confirmation user ID              | User's ID                                        |
# 	| Clinical reason for cease                | Null                                             |
# 	| Lynch due date                           | Null                                             |
# #	| Lynch due date date of change            | Today                                            | (*) Not checked, see above
# 	| Lynch due date reason                    | Ceased                                           |
# 	| Screening due date                       | Null                                             |
# 	| Screening due date date of change        | Unchanged                                        |
# 	| Screening due date reason                | Unchanged                                        |
# 	| Screening status                         | Ceased                                           |
# 	| Screening status date of change          | Today                                            |
# 	| Screening status reason                  | <Cease reason>                                   |
# 	| Surveillance due date                    | Null                                             |
# 	| Surveillance due date date of change     | Unchanged                                        |
# 	| Surveillance due date reason             | Unchanged                                        |
# When I receive an SSPI update to change their date of birth to "<Subject age>" years old
#       And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Subject age | <Subject age> |
# When I uncease and opt my subject into the Lynch Surveillance programme
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Null                        |
# 	| Calculated lynch due date                | Unchanged                   |
# 	| Calculated surveillance due date         | Null                        |
# 	| Ceased confirmation date                 | Null                        |
# 	| Ceased confirmation details              | Null                        |
# 	| Ceased confirmation user ID              | Null                        |
# 	| Clinical reason for cease                | Null                        |
# 	| Lynch due date                           | <Unceased LSDD>             |
# 	| Lynch due date date of change            | <Unceased LSDD change date> |
# 	| Lynch due date reason                    | Opt-in                      |
# 	| Screening due date                       | Null                        |
# 	| Screening due date date of change        | Unchanged                   |
# 	| Screening due date reason                | Unchanged                   |
# 	| Screening status                         | Lynch Surveillance          |
# 	| Screening status date of change          | Today                       |
# 	| Screening status reason                  | Opt-in                      |
# 	| Surveillance due date                    | Null                        |
# 	| Surveillance due date date of change     | Unchanged                   |
# 	| Surveillance due date reason             | Unchanged                   |

# Examples:
# 	| Scenario                                                        | Has episodes | LCSDD        | Subject age | Cease reason                   | Cease type    | Unceased LSDD             | Unceased LSDD change date |
# 	| 1 Below-age subject with no history and future LCSDD (SSUN21.3) | No           | After today  | 20          | Informed Dissent               | not-immediate | Null                      | Unchanged                 |
# 	| 2 Below-age subject with no history and past LCSDD (SSUN21.3)   | No           | Before today | 21          | Informed Dissent (verbal only) | immediate     | Null                      | Unchanged                 |
# 	| 3 Below-age subject with history and future LCSDD (SSUN21.3)    | Yes          | After today  | 19          | No Colon (subject request)     | not-immediate | Null                      | Unchanged                 |
# 	| 4 Below-age subject with history and past LCSDD (SSUN21.3)      | Yes          | Before today | 22          | No Colon (programme assessed)  | immediate     | Null                      | Unchanged                 |
# 	| 5 Below-age subject with no history and null LCSDD (SSUN21.3)   | No           | Null         | 21          | Informed Dissent (verbal only) | immediate     | Null                      | Unchanged                 |
# 	| 6 Below-age subject with history and null LCSDD (SSUN21.3)      | Yes          | Null         | 19          | No Colon (subject request)     | not-immediate | Null                      | Unchanged                 |
# 	| 7 In-age subject with no history and future LCSDD (SSUN21.2)    | No           | After today  | 45          | Informed Dissent               | not-immediate | Null                      | Unchanged                 |
# 	| 8 In-age subject with no history and past LCSDD (SSUN21.1)      | No           | Before today | 60          | Informal Death                 | immediate     | Calculated lynch due date | Today                     |
# 	| 9 In-age subject with history and future LCSDD (SSUN21.2)       | Yes          | After today  | 71          | No Colon (subject request)     | not-immediate | Null                      | Unchanged                 |
# 	| 10 In-age subject with history and past LCSDD (SSUN21.1)        | Yes          | Before today | 40          | No Colon (programme assessed)  | immediate     | Calculated lynch due date | Today                     |
# 	| 11 In-age subject with no history and null LCSDD (SSUN21.2)     | No           | Null         | 60          | Informal Death                 | immediate     | Null                      | Unchanged                 |
# 	| 12 In-age subject with history and null LCSDD (SSUN21.2)        | Yes          | Null         | 71          | No Colon (subject request)     | not-immediate | Null                      | Unchanged                 |







# Scenario Outline: Cease and uncease an above-age Lynch subject

# These scenarios test the case where a subject who already has a Lynch diagnosis before they are manually ceased is over age today (and maybe also at their LCSDD).
# Not checking the Lynch due date date of change as part of the cease, as not specifying if the Lynch due date has a value prior to that.

# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Calculated lynch due date            | <LCSDD>            |
# 	| subject has an open episode          | No                 |
# 	| Subject has episodes                 | <Has episodes>     |
# 	| Subject has lynch diagnosis          | Yes                |
# 	| Screening status                     | Lynch Surveillance |
# 	| Subject has unprocessed SSPI updates | No                 |
# When Comment: NHS number - "Scenario: <Scenario>"
# When I view the subject
# 	And I manually cease the subject with reason "<Cease reason>"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Null                                             |
# 	| Calculated lynch due date                | Unchanged                                        |
# 	| Calculated surveillance due date         | Null                                             |
# 	| Ceased confirmation date                 | Today                                            |
# 	| Ceased confirmation details              | AUTO TESTING: confirm <Cease type> manual cease  |
# 	| Ceased confirmation user ID              | User's ID                                        |
# 	| Clinical reason for cease                | Null                                             |
# 	| Lynch due date                           | Null                                             |
# #	| Lynch due date date of change            | Today                                            | (*) Not checked, see above
# 	| Lynch due date reason                    | Ceased                                           |
# 	| Screening due date                       | Null                                             |
# 	| Screening due date date of change        | Unchanged                                        |
# 	| Screening due date reason                | Unchanged                                        |
# 	| Screening status                         | Ceased                                           |
# 	| Screening status date of change          | Today                                            |
# 	| Screening status reason                  | <Cease reason>                                   |
# 	| Surveillance due date                    | Null                                             |
# 	| Surveillance due date date of change     | Unchanged                                        |
# 	| Surveillance due date reason             | Unchanged                                        |
# When I receive an SSPI update to change their date of birth to "<Subject age>" years old
#       And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Subject age | <Subject age> |
# When I uncease my over age Lynch subject
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Null                                    |
# 	| Calculated lynch due date                | Unchanged                               |
# 	| Calculated surveillance due date         | Null                                    |
# 	| Ceased confirmation date                 | Today                                   |
# 	| Ceased confirmation details              | Outside screening population at recall. |
# 	| Ceased confirmation user ID              | User's ID                               |
# 	| Clinical reason for cease                | Null                                    |
# 	| Lynch due date                           | Null                                    |
# 	| Lynch due date date of change            | Unchanged                               |
# 	| Lynch due date reason                    | Ceased                                  |
# 	| Screening due date                       | Null                                    |
# 	| Screening due date date of change        | Unchanged                               |
# 	| Screening due date reason                | Unchanged                               |
# 	| Screening status                         | Ceased                                  |
# 	| Screening status date of change          | Unchanged                               |
# 	| Screening status reason                  | Outside Screening Population            |
# 	| Surveillance due date                    | Null                                    |
# 	| Surveillance due date date of change     | Unchanged                               |
# 	| Surveillance due date reason             | Unchanged                               |

# Examples:
# 	| Scenario                                                        | Has episodes | LCSDD        | Subject age | Cease reason                   | Cease type    |
# 	| 13 Above-age subject with no history and future LCSDD (SSUN1.4) | No           | After today  | 75          | Informed Dissent               | not-immediate |
# 	| 14 Above-age subject with no history and past LCSDD (SSUN1.4)   | No           | Before today | 76          | Informed Dissent (verbal only) | immediate     |
# 	| 15 Above-age subject with history and future LCSDD (SSUN1.4)    | Yes          | After today  | 77          | No Colon (subject request)     | not-immediate |
# 	| 16 Above-age subject with history and past LCSDD (SSUN1.4)      | Yes          | Before today | 78          | No Colon (programme assessed)  | immediate     |
# 	| 17 Above-age subject with no history and null LCSDD (SSUN1.4)   | Yes          | Null         | 75          | Informed Dissent               | not-immediate |
# 	| 18 Above-age subject with history and null LCSDD (SSUN1.4)      | Yes          | Null         | 81          | Informal Death                 | immediate     |







# Scenario: Cease and uncease a Lynch subject who is over-age at their LCSDD but in-age today - manual cease from Lynch Surveillance

# This scenario tests the case where a subject who already has a Lynch diagnosis before they are manually ceased is in age today but will become over age at their next LCSDD when their DOB is changed while they are ceased.

# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Latest episode status                | Open               |
# 	| Latest episode type                  | Lynch Surveillance |
# 	| Latest event status                  | G1                 |
# 	| Subject age                          | Between 35 and 72  |
# 	| Subject has lynch diagnosis          | Yes                |
# 	| Screening status                     | Lynch Surveillance |
# 	| Subject has unprocessed SSPI updates | No                 |
# When Comment: NHS number
# When I view the subject
# 	And I close the subject's episode for "Opt out of current episode"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date                 | Null                                 |
# 	| Calculated Lynch Due Date                | 2 years from episode end             |
# 	| Calculated Surveillance Due Date         | Null                                 |
# 	| Ceased confirmation date                 | Null                                 |
# 	| Ceased confirmation details              | Null                                 |
# 	| Ceased confirmation user ID              | Null                                 |
# 	| Clinical reason for cease                | Null                                 |
# 	| Latest episode accumulated result        | Lynch non-participation              |
# 	| Latest episode recall calculation method | G92 Interrupt Close Date             |
# 	| Latest episode recall episode type       | Lynch Surveillance                   |
# 	| Latest episode status                    | Closed                               |
# 	| Latest episode status reason             | Opt out of current episode           |
# 	| Latest event status                      | G92                                  |
# 	| Lynch due date                           | Calculated Lynch Due Date            |
# 	| Lynch due date date of change            | Today                                |
# 	| Lynch due date reason                    | Lynch Surveillance                   |
# 	| Pre-interrupt event status               | G1                                   |
# 	| Screening Due Date                       | Null                                 |
# 	| Screening Due Date Date of change        | Unchanged                            |
# 	| Screening Due Date Reason                | Unchanged                            |
# 	| Screening Status                         | Lynch Surveillance                   |
# 	| Screening status date of change          | Unchanged                            |
# 	| Screening status reason                  | Lynch Surveillance                   |
# 	| Surveillance Due Date                    | Null                                 |
# 	| Surveillance due date date of change     | Unchanged                            |
# 	| Surveillance due date reason             | Unchanged                            |
# When I view the subject
# 	And I manually cease the subject with reason "Informed Dissent (verbal only)"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Null                                         |
# 	| Calculated lynch due date                | Unchanged                                    |
# 	| Calculated surveillance due date         | Null                                         |
# 	| Ceased confirmation date                 | Today                                        |
# 	| Ceased confirmation details              | AUTO TESTING: confirm immediate manual cease |
# 	| Ceased confirmation user ID              | User's ID                                    |
# 	| Clinical reason for cease                | Null                                         |
# 	| Lynch due date                           | Null                                         |
# 	| Lynch due date date of change            | Today                                        |
# 	| Lynch due date reason                    | Ceased                                       |
# 	| Screening due date                       | Null                                         |
# 	| Screening due date date of change        | Unchanged                                    |
# 	| Screening due date reason                | Unchanged                                    |
# 	| Screening status                         | Ceased                                       |
# 	| Screening status date of change          | Today                                        |
# 	| Screening status reason                  | Informed Dissent (verbal only)               |
# 	| Surveillance due date                    | Null                                         |
# 	| Surveillance due date date of change     | Unchanged                                    |
# 	| Surveillance due date reason             | Unchanged                                    |
# When I receive an SSPI update to change their date of birth to "73" years old
#       And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Subject age | 73 |
# When I uncease my over age Lynch subject
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Null                                    |
# 	| Calculated lynch due date                | Unchanged                               |
# 	| Calculated surveillance due date         | Null                                    |
# 	| Ceased confirmation date                 | Today                                   |
# 	| Ceased confirmation details              | Outside screening population at recall. |
# 	| Ceased confirmation user ID              | User's ID                               |
# 	| Clinical reason for cease                | Null                                    |
# 	| Lynch due date                           | Null                                    |
# 	| Lynch due date date of change            | Unchanged                               |
# 	| Lynch due date reason                    | Ceased                                  |
# 	| Screening due date                       | Null                                    |
# 	| Screening due date date of change        | Unchanged                               |
# 	| Screening due date reason                | Unchanged                               |
# 	| Screening status                         | Ceased                                  |
# 	| Screening status date of change          | Unchanged                               |
# 	| Screening status reason                  | Outside Screening Population            |
# 	| Surveillance due date                    | Null                                    |
# 	| Surveillance due date date of change     | Unchanged                               |
# 	| Surveillance due date reason             | Unchanged                               |







# Scenario: Cease and uncease a Lynch subject who is over-age at their LCSDD but in-age today - manual cease from Ceased for age
# This scenario tests the case where a subject who already has a Lynch diagnosis is already ceased for age before they are manually ceased.
# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Latest episode status                | Open               |
# 	| Latest episode type                  | Lynch Surveillance |
# 	| Latest event status                  | G1                 |
# 	| Subject has lynch diagnosis          | Yes                |
# 	| Screening status                     | Lynch Surveillance |
# 	| Subject has unprocessed SSPI updates | No                 |
# When Comment: NHS number
# When I receive an SSPI update to change their date of birth to "74" years old
#       And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Subject age | 74 |
# When I view the subject
# 	And I close the subject's episode for "Opt out of current episode"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date                 | Null                                    |
# 	| Calculated Lynch Due Date                | 2 years from episode end                |
# 	| Calculated Surveillance Due Date         | Null                                    |
# 	| Ceased confirmation date                 | Today                                   |
# 	| Ceased confirmation details              | Outside screening population at recall. |
# 	| Ceased confirmation user ID              | User's ID                               |
# 	| Clinical reason for cease                | Null                                    |
# 	| Latest episode accumulated result        | Lynch non-participation                 |
# 	| Latest episode recall calculation method | G92 Interrupt Close Date                |
# 	| Latest episode recall episode type       | Lynch Surveillance                      |
# 	| Latest episode status                    | Closed                                  |
# 	| Latest episode status reason             | Opt out of current episode              |
# 	| Latest event status                      | G92                                     |
# 	| Lynch due date                           | Null                                    |
# 	| Lynch due date date of change            | Today                                   |
# 	| Lynch due date reason                    | Ceased                                  |
# 	| Pre-interrupt event status               | G1                                      |
# 	| Screening Due Date                       | Null                                    |
# 	| Screening Due Date Date of change        | Unchanged                               |
# 	| Screening Due Date Reason                | Unchanged                               |
# 	| Screening Status                         | Ceased                                  |
# 	| Screening status date of change          | Today                                   |
# 	| Screening status reason                  | Outside Screening Population            |
# 	| Surveillance Due Date                    | Null                                    |
# 	| Surveillance due date date of change     | Unchanged                               |
# 	| Surveillance due date reason             | Unchanged                               |
# When I view the subject
# 	And I manually cease the subject with reason "Informed Dissent (verbal only)"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Null                                         |
# 	| Calculated lynch due date                | Unchanged                                    |
# 	| Calculated surveillance due date         | Null                                         |
# 	| Ceased confirmation date                 | Today                                        |
# 	| Ceased confirmation details              | AUTO TESTING: confirm immediate manual cease |
# 	| Ceased confirmation user ID              | User's ID                                    |
# 	| Clinical reason for cease                | Null                                         |
# 	| Latest episode accumulated result        | Lynch non-participation                      |
# 	| Latest episode recall calculation method | G92 Interrupt Close Date                     |
# 	| Latest episode recall episode type       | Lynch Surveillance                           |
# 	| Latest episode status                    | Closed                                       |
# 	| Latest episode status reason             | Opt out of current episode                   |
# 	| Latest event status                      | G92                                          |
# 	| Lynch due date                           | Null                                         |
# 	| Lynch due date date of change            | Today                                        |
# 	| Lynch due date reason                    | Ceased                                       |
# 	| Screening due date                       | Null                                         |
# 	| Screening due date date of change        | Unchanged                                    |
# 	| Screening due date reason                | Unchanged                                    |
# 	| Screening status                         | Ceased                                       |
# 	| Screening status date of change          | Today                                        |
# 	| Screening status reason                  | Informed Dissent (verbal only)               |
# 	| Surveillance due date                    | Null                                         |
# 	| Surveillance due date date of change     | Unchanged                                    |
# 	| Surveillance due date reason             | Unchanged                                    |
# When I uncease my over age Lynch subject
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Null                                    |
# 	| Calculated lynch due date                | Unchanged                               |
# 	| Calculated surveillance due date         | Null                                    |
# 	| Ceased confirmation date                 | Today                                   |
# 	| Ceased confirmation details              | Outside screening population at recall. |
# 	| Ceased confirmation user ID              | User's ID                               |
# 	| Clinical reason for cease                | Null                                    |
# 	| Latest episode accumulated result        | Lynch non-participation                 |
# 	| Latest episode recall calculation method | G92 Interrupt Close Date                |
# 	| Latest episode recall episode type       | Lynch Surveillance                      |
# 	| Latest episode status                    | Closed                                  |
# 	| Latest episode status reason             | Opt out of current episode              |
# 	| Latest event status                      | G92                                     |
# 	| Lynch due date                           | Null                                    |
# 	| Lynch due date date of change            | Unchanged                               |
# 	| Lynch due date reason                    | Ceased                                  |
# 	| Screening due date                       | Null                                    |
# 	| Screening due date date of change        | Unchanged                               |
# 	| Screening due date reason                | Unchanged                               |
# 	| Screening status                         | Ceased                                  |
# 	| Screening status date of change          | Unchanged                               |
# 	| Screening status reason                  | Outside Screening Population            |
# 	| Surveillance due date                    | Null                                    |
# 	| Surveillance due date date of change     | Unchanged                               |
# 	| Surveillance due date reason             | Unchanged                               |
