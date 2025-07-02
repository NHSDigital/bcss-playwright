# @BCSSAdditionalTests @AgeExtensionTests @AgeExtensionTests2
# Feature: Manual UI Unceasing Checks

# Confirm that manually 'ceasing' then 'unceasing' an age extended subject results in the correct outcome.

# These tests would be valid for all age extension ages, i.e. standard agex ages 50, 52, 54, 56 and 58, and also the "unscreened bowel scope cohort" age 51.

# Glossary
# --------
# Completed Satisfactorily - Achieved a result and was not interrupted or non-responded.
# CSDD - Calculated Screening Due Date.
# SDD - Screening Due Date.
# Significant Result - Normal, weak positive or abnormal FOBT result (not spoilt or technical failure result).
# AgeX - Age Extended.

# Further Reading
# --------
# The references used within this feature are outlined in detail in the following directory:
# Q:\DEV\Services\BCSS\System Specification\Screening Subject
# The spreadsheet itself is called: Screening Subject Data Items (Use the latest version)


# Background: I always log into England as the Hub Manager
# Given I log in to BCSS "England" as user role "Hub Manager"

# @RemoveSubject
# Scenario Outline: Below-age agex-<AgeX-Age> subject  has no episode history > SSUN9.13 Opt-in awaiting failsafe
# Given I create a subject that meets the following criteria:
# 	| NHS Number  | 9999999999    |
# 	| Age         | <Subject-Age> |
# 	| GP Practice | C81014        |
# When I update the age extension age <AgeX-Age> start date for my subject's screening centre to 400 days in the "past"
# When I manually cease the subject with reason "Informed Dissent"
# 	And I view the subject
# Then my subject has been updated as follows:
# 	| Ceased confirmation date    | Today            |
# 	| Ceased confirmation details | Not null         |
# 	| Ceased confirmation user ID | Not null         |
# 	| Clinical reason for cease   | Null             |
# 	| Screening Status            | Ceased           |
# 	| Screening Status Reason     | Informed Dissent |
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
# And I remove the age extension age <AgeX-Age> start date from my subject's screening centre

# Examples:
# 	| Subject-Age | AgeX-Age |
# 	| 49          | 50       |
# 	| 51          | 52       |
# 	| 53          | 54       |
# 	| 55          | 56       |
# 	| 57          | 58       |


# @RemoveSubject
# Scenario: Within default age range subject has no episode history > SSUN9.6 Opt-in (send a kit) today
# # THIS SCENARIO DOESN'T ADD ANY AGEX-SPECIFIC TESTING; SUSPECT IT IS JUST A DUPLICATE OF OTHER MANUAL UNCEASE SCENARIOS
# Given I create a subject that meets the following criteria:
# 	| NHS Number  | 9999999999 |
# 	| Age         | 65         |
# 	| GP Practice | C81014     |
# When I manually cease the subject with reason "Informal Death"
# 	And I pause for "5" seconds to let the process complete
# 	And I view the subject
# Then my subject has been updated as follows:
# 	| Ceased confirmation date    | Today          |
# 	| Ceased confirmation details | Not null       |
# 	| Ceased confirmation user ID | Not null       |
# 	| Clinical reason for cease   | Null           |
# 	| Screening Status            | Ceased         |
# 	| Screening Status Reason     | Informal Death |
# When I manually uncease the subject to "send a new kit"
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


# Scenario: Above-age subject has no episode history > SSUN9.9 Over age Opt-in (send a kit) today
# # THIS SCENARIO DOESN'T ADD ANY AGEX-SPECIFIC TESTING; SUSPECT IT IS JUST A DUPLICATE OF OTHER SELF-REFER TO SEND A KIT SCENARIOS
# Given there is a subject who meets the following criteria:
# 	| Has GP practice  | Yes - active |
# 	| Screening status | Inactive     |
# 	| Subject age      | >=75         |
# 	| Note count       | < 200        |
# When I manually cease the subject with reason "Informal Death"
# 	And I pause for "5" seconds to let the process complete
# 	And I view the subject
# Then my subject has been updated as follows:
# 	| Ceased confirmation date    | Today          |
# 	| Ceased confirmation details | Not null       |
# 	| Ceased confirmation user ID | Not null       |
# 	| Clinical reason for cease   | Null           |
# 	| Screening Status            | Ceased         |
# 	| Screening Status Reason     | Informal Death |
# When I manually uncease the subject to "send a new kit"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date             | Unchanged     |
# 	| Calculated surveillance due date     | Unchanged     |
# 	| Ceased confirmation date             | Null          |
# 	| Ceased confirmation details          | Null          |
# 	| Ceased confirmation user ID          | Null          |
# 	| Clinical reason for cease            | Null          |
# 	| Previous Screening Status            | Ceased        |
# 	| Screening Due Date                   | Today         |
# 	| Screening Due Date Reason            | Self-Referral |
# 	| Screening Due Date Date Of Change    | Today         |
# 	| Screening Status                     | Self-Referral |
# 	| Screening Status Date of Change      | Today         |
# 	| Screening Status Reason              | Self-Referral |
# 	| Subject Lower FOBT Age               | Default       |
# 	| Surveillance Due Date                | Null          |
# 	| Surveillance due date reason         | Null          |
# 	| Surveillance due date date of change | Unchanged     |

# @RemoveSubject
# Scenario Outline: AgeX <Age> subject with no history is ceased before they are invited so revert to below-age and not AgeX > SSUN9.13 Opt-in awaiting failsafe
# Given I create a subject that meets the following criteria:
# 	| NHS Number  | 9999999999 |
# 	| Age         | <Age>      |
# 	| GP Practice | C81014     |
# When I update the age extension age <Age> start date for my subject's screening centre to 400 days in the "past"
# 	And I run the overnight failsafe job for my subject
# 	And I view the subject
# Then my subject has been updated as follows:
# 	| Calculated FOBT due date          | Null                   |
# 	| Screening Status                  | Call                   |
# 	| Screening Status Reason           | Eligible for Screening |
# 	| Screening Status Date of Change   | Today                  |
# 	| Screening Due Date (birthday)     | <Age>                  |
# 	| Screening Due Date Date of Change | Today                  |
# 	| Subject Lower FOBT Age            | <Age>                  |
# 	And I manually cease the subject with reason "Informed Dissent"
# 	And I view the subject
# Then my subject has been updated as follows:
# 	| Ceased confirmation date    | Today            |
# 	| Ceased confirmation details | Not null         |
# 	| Ceased confirmation user ID | Not null         |
# 	| Clinical reason for cease   | Null             |
# 	| Screening Status            | Ceased           |
# 	| Screening Status Reason     | Informed Dissent |
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
# 	| 50  |
# 	| 52  |
# 	| 54  |
# 	| 56  |
# 	| 58  |


# Scenario Outline: Not-agex subject is next due to be screened in the past with a date of birth change making them lower than the default FOBT age > SSUN9.13 Opt-in awaiting failsafe
# # THIS SCENARIO DOESN'T ADD ANY AGEX-SPECIFIC TESTING; SUSPECT IT IS JUST A DUPLICATE OF OTHER DOB CHANGE / MANUAL UNCEASE SCENARIOS
# Given there is a subject who meets the following criteria:
# 	| Calculated FOBT Due Date                  | < today      |
# 	| Has GP Practice                           | Yes - Active |
# 	| Latest Episode has Significant Kit Result | Yes          |
# 	| Latest Episode Status                     | Closed       |
# 	| Screening status                          | Recall       |
# 	| Subject Lower FOBT Age                    | Default      |
# 	| Note count                                | < 200        |
# 	And I remove the age extension age <Age> start date from my subject's screening centre
# 	And I manually cease the subject with reason "Informed Dissent"
# Then my subject has been updated as follows:
# 	| Ceased confirmation date    | Today            |
# 	| Ceased confirmation details | Not null         |
# 	| Ceased confirmation user ID | Not null         |
# 	| Clinical reason for cease   | Null             |
# 	| Screening Status            | Ceased           |
# 	| Screening Status Reason     | Informed Dissent |
# When I receive an SSPI update to change their date of birth to "<Age>" years old
# 	And I pause for "5" seconds to let the process complete
# 	And I manually uncease the subject to "opt them into the screening programme"
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

# Examples:
# 	| Age |
# 	| 50  |
# 	| 52  |
# 	| 54  |
# 	| 56  |
# 	| 58  |

# @ignore
# Scenario Outline: Subject aged <Age> formally eligible for uncease under late response rules is set to awaiting failsafe due to being under the default FOBT age. > SSUN9.13 Opt-in awaiting failsafe
# # THIS SCENARIO DOESN'T ADD ANY AGEX-SPECIFIC TESTING; SUSPECT IT IS JUST A DUPLICATE OF OTHER DOB CHANGE / MANUAL UNCEASE SCENARIOS 
# # (PLUS IT'S ESSENTIALLY A DUPLICATE OF THE SCENARIO ABOVE)
# Given there is a subject who meets the following criteria:
# 	| Calculated FOBT Due Date                  | < today        |
# 	| Has GP Practice                           | Yes - Active   |
# 	| Latest Episode ended                      | > 6 months ago |
# 	| Latest Episode has Significant Kit Result | No             |
# 	| Latest Episode Status                     | Closed         |
# 	| Latest Episode Type                       | FOBT           |
# 	| Screening status                          | Recall         |
# 	| Subject Lower FOBT Age                    | Default        |
# 	| Note count                                | < 200          |
# 	And I remove the age extension age <Age> start date from my subject's screening centre
# 	And I manually cease the subject with reason "Informed Dissent"
# Then my subject has been updated as follows:
# 	| Ceased confirmation date    | Today            |
# 	| Ceased confirmation details | Not null         |
# 	| Ceased confirmation user ID | Not null         |
# 	| Clinical reason for cease   | Null             |
# 	| Screening Status            | Ceased           |
# 	| Screening Status Reason     | Informed Dissent |
# When I receive an SSPI update to change their date of birth to "<Age>" years old
# 	And I manually uncease the subject to "opt them into the screening programme"
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

# Examples:
# 	| Age |
# 	| 50  |
# 	| 52  |
# 	| 54  |
# 	| 56  |
# 	| 58  |


# Scenario: Subject just below default FOBT age whose last FOBT episode has "Completed Satisfactorily" will be eligible when next due to be screened. > SSUN9.13 Opt-in awaiting failsafe
# # THIS SCENARIO DOESN'T ADD ANY AGEX-SPECIFIC TESTING; SUSPECT IT IS JUST A DUPLICATE OF OTHER MANUAL UNCEASE SCENARIOS 
# Given there is a subject who meets the following criteria:
# 	| Calculated FOBT Due Date                  | > today      |
# 	| Has GP Practice                           | Yes - Active |
# 	| Latest Episode Completed Satisfactorily   | Yes          |
# 	| Latest Episode has Significant Kit Result | Yes          |
# 	| Latest Episode Status                     | Closed       |
# 	| Latest Episode Type                       | FOBT         |
# 	| Screening status                          | Recall       |
# 	| Subject Lower FOBT Age                    | Default      |
# 	| Note count                                | < 200        |
# 	And I remove the age extension age 50 start date from my subject's screening centre
# 	And I remove the age extension age 52 start date from my subject's screening centre
# 	And I remove the age extension age 54 start date from my subject's screening centre
# 	And I remove the age extension age 56 start date from my subject's screening centre
# 	And I remove the age extension age 58 start date from my subject's screening centre
# When I manually cease the subject with reason "Informed Dissent"
# Then my subject has been updated as follows:
# 	| Ceased confirmation date    | Today            |
# 	| Ceased confirmation details | Not null         |
# 	| Ceased confirmation user ID | Not null         |
# 	| Clinical reason for cease   | Null             |
# 	| Screening Status            | Ceased           |
# 	| Screening Status Reason     | Informed Dissent |
# When I receive an SSPI update to change their date of birth to "60" years old "minus" "1" days
# 	And I manually uncease the subject to "opt them into the screening programme"
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

# @ignore
# Scenario Outline: Subject who <Scenario-Type> an AgeX attribute is manually unceased after a DOB change whilst ceased making them below eligible age > SSUN9.13 Opt-in awaiting failsafe
# Note that if the subject has not been invited since they were age extended their FOBT lower age is removed during the cease; even if they have been invited since then it is removed during the DOB change.
# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Has GP Practice                  | Yes - Active         |
# # Exclude episodes with referral date, as they require extra steps to enter a diagnosis date
# 	| Latest episode has referral date | No                   |
# 	| Latest episode status            | Open                 |
# 	| Latest episode type              | FOBT                 |
# # Make sure the subject is young enough that they don't get re-ceased for age, instead of opt-in
# 	| Subject age                      | < 73                 |
# 	| Subject Lower FOBT Age           | <Lower-FOBT-Age>     |
# 	| Note count                       | < 200                |
# # Make sure the subject has been invited since they were age extended, otherwise their agex lower age is removed during the Cease (this is just ignored for not-agex subject)
# 	| Invited since age extension      | <Invited-since-agex> |
# When I view the subject
# 	And I close the subject's episode for "Cease Request"
# 	And I manually cease the subject with reason "Informed Dissent"
# Then my subject has been updated as follows:
# 	| Ceased confirmation date          | Today                        |
# 	| Clinical reason for cease         | Null                         |
# 	| Screening Due Date                | Null                         |
# 	| Screening Due Date Reason         | Ceased                       |
# 	| Screening Due Date Date of change | Today                        |
# 	| Screening Status                  | Ceased                       |
# 	| Screening Status Reason           | Informed Dissent             |
# 	| Subject Lower FOBT Age            | <Lower-FOBT-Age-after-cease> |
# 	| Surveillance Due Date             | Null                         |
# When I view the subject
# 	And I receive an SSPI update to change their date of birth to "45" years old
# 	And I pause for "5" seconds to let the process complete
# 	And I manually uncease the subject to "opt them into the screening programme"
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

# Examples:
# 	| Scenario-Type | Lower-FOBT-Age | Invited-since-agex | Lower-FOBT-Age-after-cease |
# 	| has           | NOT: default   | Yes                | NOT: default               |
# 	| has           | NOT: default   | No                 | Default                    |
# 	| does not have | default        | No                 | Default                    |
