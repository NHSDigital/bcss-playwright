import pytest
import logging
import pandas as pd
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.oracle.oracle_specific_functions import SubjectSelector
from classes.subject import Subject
from utils.oracle.oracle import OracleDB
from pages.base_page import BasePage
from utils import screening_subject_page_searcher

# from utils.subject.subject_assertions import SubjectAssertions
# from utils.subject.subject_cease_utils import SubjectCeaseUtils

# Feature: Manually cease a subject


# These scenarios just check that manually ceasing a subject (either immediately or via a disclaimer letter) from different statuses correctly sets their screening status and status reason.
# Screening due date reason is always set to "Ceased" during a manual cease, even if the SDD is not changing.
@pytest.mark.wip
@pytest.mark.manual_cease
@pytest.mark.regression
def test_manual_cease_from_inactive_subject_for_informed_dissent(page: Page) -> None:
    """
    Scenario: Subject is at status Inactive, cease for Informed Dissent

        Given I log in to BCSS "England" as user role "Hub Manager"
        And there is a subject who meets the following criteria:
            | Screening status | Inactive |
        When I view the subject
        And I manually cease the subject with reason "Informed Dissent"
        And I pause for "5" seconds to let the process complete
        Then my subject has been updated as follows:
            | Screening Status                 | Ceased                                           |
            | Screening Status Reason          | Informed Dissent                                 |
            | Screening Status Date of Change  | Today                                            |
            | Screening Due Date Reason        | Ceased                                           |
            | Screening Due Date               | Null (unchanged)                                 |
            | Ceased Confirmation Details      | AUTO TESTING: confirm not-immediate manual cease |
            | Ceased Confirmation User ID      | User's ID                                        |
            | Lynch / Surveillance Due Dates   | Unchanged or Null                                |
            | Clinical Reason for Cease        | Null                                             |
    """
    logging.info("[TEST START] Manual cease from Inactive subject for Informed Dissent")

    # Retrieve NHS number for subject matching scenario criteria
    nhs_number = SubjectSelector.get_subject_for_manual_cease(
        {"screening status": "Inactive"}
    )
    logging.info(f"[SUBJECT SELECTOR] Retrieved NHS number: {nhs_number}")
    # TODO: Does a stored procedure need to be run? Subject is not being updated as specified in docstring
    # Create Oracle subject object and run timed events (optional but consistent with existing pattern)
    subject = Subject()
    nhs_df = pd.DataFrame({"subject_nhs_number": [nhs_number]})
    OracleDB().exec_bcss_timed_events(nhs_df)
    logging.info("[TIMED EVENTS] Executed for subject")

    # # Navigate to subject profile in UI
    # base_page = BasePage(page)
    # base_page.click_main_menu_link()
    # base_page.go_to_screening_subject_search_page()
    # screening_subject_page_searcher.search_subject_by_nhs_number(page, nhs_number)
    # logging.info("[SUBJECT VIEW] Subject loaded in UI")

    # # Manually cease subject with specified reason
    # SubjectCeaseUtils.trigger_manual_cease(page, reason="Informed Dissent")
    # logging.info("[CEASE ACTION] Manual cease triggered")

    # # Wait for updates to process
    # page.wait_for_timeout(5000)

    # # Perform field assertions
    # SubjectAssertions.assert_field("Screening Status", "Ceased")
    # SubjectAssertions.assert_field("Screening Status Reason", "Informed Dissent")
    # SubjectAssertions.assert_field_is_today("Screening Status Date of Change")
    # SubjectAssertions.assert_field("Screening Due Date Reason", "Ceased")
    # SubjectAssertions.assert_field_null("Screening Due Date")
    # SubjectAssertions.assert_field(
    #     "Ceased Confirmation Details",
    #     "AUTO TESTING: confirm not-immediate manual cease",
    # )
    # SubjectAssertions.assert_field_matches_user_id("Ceased Confirmation User ID")
    # SubjectAssertions.assert_field_null("Clinical Reason for Cease")
    # SubjectAssertions.assert_field_unchanged("Calculated FOBT Due Date")
    # SubjectAssertions.assert_field_null("Calculated Lynch Due Date")
    # SubjectAssertions.assert_field_unchanged("Calculated Surveillance Due Date")

    # logging.info("[ASSERTIONS COMPLETE] Manual cease scenario validated successfully")


# Scenario: Subject is at status Call, cease for Informed Dissent, verbal only

# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Screening status                         | Call |
# 	| Subject has episodes                     | No   |

# When Comment: NHS number

# When I view the subject
# 	And I manually cease the subject with reason "Informed Dissent (verbal only)"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Unchanged                                        |
# 	| Calculated lynch due date                | Null                                             |
# 	| Calculated surveillance due date         | Unchanged                                        |
# 	| Ceased confirmation date                 | Today                                            |
# 	| Ceased confirmation details              | AUTO TESTING: confirm immediate manual cease     |
# 	| Ceased confirmation user ID              | User's ID                                        |
# 	| Clinical reason for cease                | Null                                             |
# 	| Lynch due date                           | Null                                             |
# 	| Lynch due date reason                    | Unchanged                                        |
# 	| Lynch due date date of change            | Unchanged                                        |
# 	| Screening due date                       | Null                                             |
# 	| Screening due date date of change        | Today                                            |
# 	| Screening due date reason                | Ceased                                           |
# 	| Screening status                         | Ceased                                           |
# 	| Screening status reason                  | Informed Dissent (verbal only)                   |
# 	| Screening status date of change          | Today                                            |
# 	| Surveillance due date                    | Null                                             |
# 	| Surveillance due date reason             | Unchanged                                        |
# 	| Surveillance due date date of change     | Unchanged                                        |


# Scenario: Subject is at status Recall, cease for No Colon, subject request

# Look for subject's with a not-null due date so the check for the SDD change is not tripped up by dodgy test data.

# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Screening status                         | Recall   |
# 	| Screening due date                       | Not null |
# 	| Latest episode status                    | Closed   |

# When Comment: NHS number

# When I view the subject
# 	And I manually cease the subject with reason "No Colon (subject request)"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Unchanged                                        |
# 	| Calculated lynch due date                | Null                                             |
# 	| Calculated surveillance due date         | Unchanged                                        |
# 	| Ceased confirmation date                 | Today                                            |
# 	| Ceased confirmation details              | AUTO TESTING: confirm not-immediate manual cease |
# 	| Ceased confirmation user ID              | User's ID                                        |
# 	| Clinical reason for cease                | Null                                             |
# 	| Lynch due date                           | Null                                             |
# 	| Lynch due date reason                    | Unchanged                                        |
# 	| Lynch due date date of change            | Unchanged                                        |
# 	| Screening due date                       | Null                                             |
# 	| Screening due date date of change        | Today                                            |
# 	| Screening due date reason                | Ceased                                           |
# 	| Screening status                         | Ceased                                           |
# 	| Screening status reason                  | No Colon (subject request)                       |
# 	| Screening status date of change          | Today                                            |
# 	| Surveillance due date                    | Null                                             |
# 	| Surveillance due date reason             | Unchanged                                        |
# 	| Surveillance due date date of change     | Unchanged                                        |


# Scenario: Subject is at status Surveillance, cease for No Colon, programme assessed

# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Screening status                         | Surveillance |
# 	| Latest episode status                    | Closed       |

# When Comment: NHS number

# When I view the subject
# 	And I manually cease the subject with reason "No Colon (programme assessed)"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Unchanged                                        |
# 	| Calculated lynch due date                | Null                                             |
# 	| Calculated surveillance due date         | Unchanged                                        |
# 	| Ceased confirmation date                 | Today                                            |
# 	| Ceased confirmation details              | AUTO TESTING: confirm immediate manual cease     |
# 	| Ceased confirmation user ID              | User's ID                                        |
# 	| Clinical reason for cease                | Null                                             |
# 	| Lynch due date                           | Null                                             |
# 	| Lynch due date reason                    | Unchanged                                        |
# 	| Lynch due date date of change            | Unchanged                                        |
# 	| Screening due date                       | Null                                             |
# 	| Screening due date date of change        | Unchanged                                        |
# 	| Screening due date reason                | Ceased                                           |
# 	| Screening status                         | Ceased                                           |
# 	| Screening status reason                  | No Colon (programme assessed)                    |
# 	| Screening status date of change          | Today                                            |
# 	| Surveillance due date                    | Null                                             |
# 	| Surveillance due date reason             | Ceased                                           |
# 	| Surveillance due date date of change     | Today                                            |


# Scenario: Subject is at status Ceased, outside screening population, cease for Informal Death

# Screening status reason is set, but because the status itself is not changing the status date of change is not changed.

# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Screening status                         | Ceased                       |
# 	| Screening status reason                  | Outside screening population |

# When Comment: NHS number

# When I view the subject
# 	And I manually cease the subject with reason "Informal Death"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Unchanged                                        |
# 	| Calculated lynch due date                | Null                                             |
# 	| Calculated surveillance due date         | Unchanged                                        |
# 	| Ceased confirmation date                 | Today                                            |
# 	| Ceased confirmation details              | AUTO TESTING: confirm immediate manual cease     |
# 	| Ceased confirmation user ID              | User's ID                                        |
# 	| Clinical reason for cease                | Null                                             |
# 	| Lynch due date                           | Null                                             |
# 	| Lynch due date reason                    | Unchanged                                        |
# 	| Lynch due date date of change            | Unchanged                                        |
# 	| Screening due date                       | Null                                             |
# 	| Screening due date date of change        | Unchanged                                        |
# 	| Screening due date reason                | Unchanged                                        |
# 	| Screening status                         | Ceased                                           |
# 	| Screening status reason                  | Informal Death                                   |
# 	| Screening status date of change          | Unchanged                                        |
# 	| Surveillance due date                    | Null                                             |
# 	| Surveillance due date reason             | Unchanged                                        |
# 	| Surveillance due date date of change     | Unchanged                                        |


# Scenario: Subject is at status Ceased, outside screening population, cease for No Colon (subject request)

# Screening status reason is set, but because the status itself is not changing the status date of change is not changed.

# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Screening status                         | Ceased                       |
# 	| Screening status reason                  | Outside screening population |

# When Comment: NHS number

# When I view the subject
# 	And I manually cease the subject with reason "No Colon (subject request)"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date                 | Unchanged                                        |
# 	| Calculated lynch due date                | Null                                             |
# 	| Calculated surveillance due date         | Unchanged                                        |
# 	| Ceased confirmation date                 | Today                                            |
# 	| Ceased confirmation details              | AUTO TESTING: confirm not-immediate manual cease |
# 	| Ceased confirmation user ID              | User's ID                                        |
# 	| Clinical reason for cease                | Null                                             |
# 	| Lynch due date                           | Null                                             |
# 	| Lynch due date reason                    | Unchanged                                        |
# 	| Lynch due date date of change            | Unchanged                                        |
# 	| Screening due date                       | Null                                             |
# 	| Screening due date date of change        | Unchanged                                        |
# 	| Screening due date reason                | Unchanged                                        |
# 	| Screening status                         | Ceased                                           |
# 	| Screening status reason                  | No Colon (subject request)                       |
# 	| Screening status date of change          | Unchanged                                        |
# 	| Surveillance due date                    | Null                                             |
# 	| Surveillance due date reason             | Unchanged                                        |
# 	| Surveillance due date date of change     | Unchanged                                        |
