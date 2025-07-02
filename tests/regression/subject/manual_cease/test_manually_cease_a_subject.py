# Feature: Manually cease a subject

# These scenarios just check that manually ceasing a subject (either immediately or via a disclaimer letter) from different statuses correctly sets their screening status and status reason.

# Screening due date reason is always set to "Ceased" during a manual cease, even if the SDD is not changing.


# Scenario: Subject is at status Inactive, cease for Informed Dissent

# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Screening status                         | Inactive |

# When Comment: NHS number

# When I view the subject
# 	And I manually cease the subject with reason "Informed Dissent"
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
# 	| Screening due date reason                | Ceased                                           |
# 	| Screening status                         | Ceased                                           |
# 	| Screening status reason                  | Informed Dissent                                 |
# 	| Screening status date of change          | Today                                            |
# 	| Surveillance due date                    | Null                                             |
# 	| Surveillance due date reason             | Unchanged                                        |
# 	| Surveillance due date date of change     | Unchanged                                        |


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
