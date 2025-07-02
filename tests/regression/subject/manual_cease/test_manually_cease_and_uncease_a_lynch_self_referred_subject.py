# Feature: Manually cease and uncease a Lynch Self Referred subject

# 	These scenarios just check that manually ceasing a Lynch self-referred subject (either immediately or via a disclaimer letter) and then unceasing them correctly sets their screening status and status reason.

# 	Scenario Outline: [BCSS-15393] User "<user role to cease>" can manually cease and user "<user role to uncease>" can manually uncease an above-age Lynch self referred subject for cease reason "<Cease reason>"

# 	These scenarios test the cases where an over aged subject who already has a Lynch diagnosis before they are manually ceased and unceased by different user roles.

# 		Given I log in to BCSS "England" as user role "Hub Manager"
# 		When I receive Lynch diagnosis "MSH6" for a new subject in my hub aged "<Subject age>" with diagnosis date "3 years ago" and last colonoscopy date "3 years ago"
# 		And I pause for "5" seconds to let the process complete
# 		Then Comment: NHS number
# 		When I self refer the subject
# 		And I press OK on my confirmation prompt
# 		And I pause for "5" seconds to let the process complete
# 		Then my subject has been updated as follows:
# 			| Calculated FOBT due date             | Null                |
# 			| Calculated lynch due date            | 1 year ago          |
# 			| Calculated surveillance due date     | Null                |
# 			| Lynch due date                       | 1 year ago          |
# 			| Lynch due date date of change        | Null                |
# 			| Lynch due date reason                | Self-referral       |
# 			| Previous screening status            | Lynch Surveillance  |
# 			| Screening due date                   | Null                |
# 			| Screening due date date of change    | Null                |
# 			| Screening due date reason            | Null                |
# 			| Subject has lynch diagnosis          | Yes                 |
# 			| Subject lower FOBT age               | Default             |
# 			| Subject lower lynch age              | 35                  |
# 			| Screening status                     | Lynch Self-referral |
# 			| Screening status date of change      | Today               |
# 			| Screening status reason              | Self-referral       |
# 			| Subject age                          | <Subject age>       |
# 			| Surveillance due date                | Null                |
# 			| Surveillance due date date of change | Null                |
# 			| Surveillance due date reason         | Null                |

# 		When Comment: NHS number - "Scenario: <Scenario>"
# 		When I view the subject
# 		And I manually cease the subject with reason "<Cease reason>"
# 		And I pause for "5" seconds to let the process complete
# 		Then my subject has been updated as follows:
# 			| Calculated FOBT due date             | Null                                            |
# 			| Calculated lynch due date            | Unchanged                                       |
# 			| Calculated surveillance due date     | Null                                            |
# 			| Ceased confirmation date             | Today                                           |
# 			| Ceased confirmation details          | AUTO TESTING: confirm <Cease type> manual cease |
# 			| Ceased confirmation user ID          | User's ID                                       |
# 			| Clinical reason for cease            | Null                                            |
# 			| Lynch due date                       | Null                                            |
# 			| Lynch due date date of change        | Today                                           |
# 			| Lynch due date reason                | Ceased                                          |
# 			| Screening due date                   | Null                                            |
# 			| Screening due date date of change    | Unchanged                                       |
# 			| Screening due date reason            | Unchanged                                       |
# 			| Screening status                     | Ceased                                          |
# 			| Screening status date of change      | Today                                           |
# 			| Screening status reason              | <Cease reason>                                  |
# 			| Surveillance due date                | Null                                            |
# 			| Surveillance due date date of change | Unchanged                                       |
# 			| Surveillance due date reason         | Unchanged                                       |

# 		When I switch users to BCSS "England" as user role "<user role to uncease>"
# 		When I uncease my over age Lynch subject
# 		And I pause for "5" seconds to let the process complete
# 		Then my subject has been updated as follows:
# 			| Calculated FOBT due date             | Null                                    |
# 			| Calculated lynch due date            | Unchanged                               |
# 			| Calculated surveillance due date     | Null                                    |
# 			| Ceased confirmation date             | Today                                   |
# 			| Ceased confirmation details          | Outside screening population at recall. |
# 			| Ceased confirmation user ID          | User's ID                               |
# 			| Clinical reason for cease            | Null                                    |
# 			| Lynch due date                       | Null                                    |
# 			| Lynch due date date of change        | Unchanged                               |
# 			| Lynch due date reason                | Ceased                                  |
# 			| Screening due date                   | Null                                    |
# 			| Screening due date date of change    | Unchanged                               |
# 			| Screening due date reason            | Unchanged                               |
# 			| Screening status                     | Ceased                                  |
# 			| Screening status date of change      | Unchanged                               |
# 			| Screening status reason              | Outside Screening Population            |
# 			| Surveillance due date                | Null                                    |
# 			| Surveillance due date date of change | Unchanged                               |
# 			| Surveillance due date reason         | Unchanged                               |

# 		Examples:
# 			| user role to cease             | user role to uncease           | Subject age | Cease reason                   | Cease type    |
# 			| HubDirectorStateRegistered     | Hub Manager                    | 75          | Informed Dissent               | not-immediate |
# 			| Hub Manager                    | BCSS Support - Hub             | 76          | No Colon (subject request)     | not-immediate |
# 			| Hub Manager - State Registered | Hub Manager                    | 77          | Informed Dissent (verbal only) | immediate     |
# 			| BCSS Support - Hub             | HubDirectorStateRegistered     | 78          | No Colon (programme assessed)  | immediate     |
# 			| HubDirectorStateRegistered     | Hub Manager - State Registered | 79          | Informal Death                 | immediate     |
