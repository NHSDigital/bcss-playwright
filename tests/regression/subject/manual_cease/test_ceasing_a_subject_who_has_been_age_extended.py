# Feature: Scenarios ceasing a subject who has been age extended

# Scenario numbering is gappy because the original 'age extension' feature was split into two, for manual/SSPI ceases

# Scenario: Test 2 - Subject has agex attribute set, no episode started since agex attribute was set, immediate manual cease - agex attribute removed

# This scenario includes a test that the overnight failsafe will age extend a subject if their "agex birthday" is later than their SC's "agex start date".  As part of age extension, an inactive subject's due date is set, but not their calculated due date (which is only set based on episode history).

# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Calculated FOBT Due Date             | null         |
# 	| Has GP Practice                      | Yes - Active |
# 	| Manual cease requested               | No           |
# 	| Screening Due Date                   | null         |           
# 	| Screening Status                     | Inactive     |
# 	| Subject Age                          | 56           |           
# 	| Subject Has Episodes                 | No           |
# 	| Subject Has FOBT Episodes            | No           |
# 	| Subject has unprocessed SSPI updates | No           |
# 	| Subject has user DOB updates         | No           |
# 	| Subject Lower FOBT Age               | Default      |      
# When I update the age extension age 56 start date for my subject's screening centre to 400 days in the "past"
# 	And I pause for "5" seconds to let the process complete
# 	And I run the overnight failsafe job for my subject
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date          | null                   |
# 	| Screening Due Date                | last birthday          |
# 	| Screening Due Date Date of Change | today                  |
# 	| Screening Due Date Reason         | Eligible for Screening |
# 	| Screening Status                  | Call                   |
# 	| Subject Lower FOBT Age            | 56                     |
# When I manually cease the subject with reason "Informed Dissent (verbal only)"
# 	And I pause for "5" seconds to let the process complete
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date          | Unchanged                      |
# 	| Calculated Surveillance Due Date  | Unchanged                      |
# 	| Ceased confirmation date          | Today                          |
# 	| Clinical reason for cease         | Null                           |
# 	| Screening Due Date                | Null                           |
# 	| Screening Due Date Reason         | Ceased                         |
# 	| Screening Due Date Date of change | Today                          |
# 	| Screening Status                  | Ceased                         |
# 	| Screening Status Reason           | Informed Dissent (verbal only) |
# 	| Subject Lower FOBT Age            | Default                        |
# 	| Surveillance Due Date             | Null                           |
# And I remove the age extension age 56 start date from my subject's screening centre


# Scenario: Test 2a - Subject has agex attribute set, no episode started since agex attribute was set, immediate manual cease - agex attribute removed
# This is the same as test 2, but with immediate cease reason "No Colon (programme assessed)"
# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Has GP Practice           | Yes - Active |
# 	| Manual cease requested    | No           |
# 	| Screening Status          | Call         |                 
# 	| Subject Has Episodes      | No           |
# 	| Subject Has FOBT Episodes | No           |
# 	| Subject Lower FOBT Age    | NOT: default |	
# When I manually cease the subject with reason "No Colon (programme assessed)"
# 	And I pause for "5" seconds to let the process complete
# 	And I view the subject
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date          | Unchanged                     |
# 	| Calculated Surveillance Due Date  | Unchanged                     |
# 	| Ceased confirmation date          | Today                         |
# 	| Clinical reason for cease         | Null                          |
# 	| Screening Due Date                | Null                          |
# 	| Screening Due Date Reason         | Ceased                        |
# 	| Screening Due Date Date of change | Today                         |
# 	| Screening Status                  | Ceased                        |
# 	| Screening Status Reason           | No Colon (programme assessed) |
# 	| Subject Lower FOBT Age            | Default                       | 		
# 	| Surveillance Due Date             | Null                          |


# Scenario: Test 2b - Subject has agex attribute set, no episode started since agex attribute was set, immediate manual cease - agex attribute removed
# # This is the same as test 2, but with immediate cease reason "Informal Death"
# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Has GP Practice           | Yes - Active |
# 	| Manual cease requested    | No           |
# 	| Screening Status          | Call         |                 
# 	| Subject Has Episodes      | No           |
# 	| Subject Has FOBT Episodes | No           |
# 	| Subject Lower FOBT Age    | NOT: default |	
# When I manually cease the subject with reason "Informal Death"
# 	And I pause for "5" seconds to let the process complete
# 	And I view the subject
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date          | Unchanged      |
# 	| Calculated Surveillance Due Date  | Unchanged      |
# 	| Ceased confirmation date          | Today          |
# 	| Clinical reason for cease         | Null           |
# 	| Screening Due Date                | Null           |
# 	| Screening Due Date Reason         | Ceased         |
# 	| Screening Due Date Date of change | Today          |
# 	| Screening Status                  | Ceased         |
# 	| Screening Status Reason           | Informal Death |
# 	| Subject Lower FOBT Age            | Default        |
# 	| Surveillance Due Date             | Null           |


# Scenario: Setup 3 - Subject has agex attribute set, no episode started since agex attribute was set
# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there are no subjects who meet the following criteria:
# 	| Has GP Practice           | Yes - Active |
# 	| Manual cease requested    | No           |
# 	| Screening Status          | Call         |
# 	| Subject Has FOBT Episodes | No           |
# 	| Subject Lower FOBT Age    | NOT: default |
# 	And there is a subject who meets the following criteria:
# 	| Calculated FOBT Due Date             | null         |
# 	| Has GP Practice                      | Yes - Active |
# 	| Manual cease requested               | No           |
# 	| Screening Due Date                   | null         |           
# 	| Screening Status                     | Inactive     |
# 	| Subject Age                          | 56           |
# 	| Subject Has FOBT Episodes            | No           |
# 	| Subject Lower FOBT Age               | Default      |      
# When I update the age extension age 56 start date for my subject's screening centre to 400 days in the "past"
# 	And I view the subject
# 	And I run the overnight failsafe job for my subject
# 	And I pause for "5" seconds to let the process complete
# 	And I view the subject
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date          | null                   |
# 	| Has GP Practice                   | Yes - Active           |           
# 	| Screening Due Date                | last birthday          |
# 	| Screening Due Date Date of Change | today                  |
# 	| Screening Due Date Reason         | Eligible for Screening |
# 	| Screening Status                  | Call                   |
# 	| Subject Has FOBT Episodes         | No                     |           
# 	| Subject Lower FOBT Age            | 56                     |
# And I remove the age extension age 56 start date from my subject's screening centre


# Scenario: Test 3 - Subject has agex attribute set, no episode started since agex attribute was set, manual cease with confirmation (disclaimer) - agex attribute removed
# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Has GP Practice           | Yes - Active |
# 	| Manual cease requested    | No           |
# 	| Screening Status          | Call         |
# 	| Subject Has FOBT Episodes | No           |
# 	| Subject Lower FOBT Age    | NOT: default |	
# When I manually cease the subject with reason "Informed Dissent"
# 	And I view the subject
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date          | Unchanged        |
# 	| Calculated Surveillance Due Date  | Unchanged        |
# 	| Ceased confirmation date          | Today            |
# 	| Clinical reason for cease         | Null             |
# 	| Screening Due Date                | Null             |
# 	| Screening Due Date Reason         | Ceased           |
# 	| Screening Due Date Date of change | Today            |
# 	| Screening Status                  | Ceased           |
# 	| Screening Status Reason           | Informed Dissent |
# 	| Subject Lower FOBT Age            | Default          |
# 	| Surveillance Due Date             | Null             |


# Scenario: Test 3a - Subject has agex attribute set, no episode started since agex attribute was set, manual cease with confirmation (disclaimer) - agex attribute removed
# # This is the same as test 2, but with immediate cease reason "No Colon (subject request)"
# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Has GP Practice           | Yes - Active |
# 	| Manual cease requested    | No           |
# 	| Screening Status          | Call         |
# 	| Subject Has FOBT Episodes | No           |
# 	| Subject Lower FOBT Age    | NOT: default |	
# When I manually cease the subject with reason "No Colon (subject request)"
# 	And I view the subject
# Then my subject has been updated as follows:
# 	| Calculated FOBT Due Date          | Unchanged                  |
# 	| Calculated Surveillance Due Date  | Unchanged                  |
# 	| Ceased confirmation date          | Today                      |
# 	| Clinical reason for cease         | Null                       |
# 	| Screening Due Date                | Null                       |
# 	| Screening Due Date Reason         | Ceased                     |
# 	| Screening Due Date Date of change | Today                      |
# 	| Screening Status                  | Ceased                     |
# 	| Screening Status Reason           | No Colon (subject request) |
# 	| Subject Lower FOBT Age            | Default                    |
# 	| Surveillance Due Date             | Null                       |


# Scenario: Test 5 - Subject has agex attribute set, has episode started since agex attribute was set, immediate manual cease - agex attribute remains set
# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Has GP Practice           | Yes - Active |
# 	| Latest episode status     | Open         |
# 	| Screening Status          | Call         |                 
# 	| Subject Has FOBT Episodes | Yes          |
# 	| Subject Lower FOBT Age    | NOT: default |	
# When I view the subject
# 	And I close the subject's episode for "Cease Request"
# 	And I manually cease the subject with reason "Informed Dissent (verbal only)"
# 	And I view the subject
# Then my subject has been updated as follows:
# 	| Ceased confirmation date          | Today                          |
# 	| Clinical reason for cease         | Null                           |
# 	| Screening Due Date                | Null                           |
# 	| Screening Due Date Reason         | Ceased                         |
# 	| Screening Due Date Date of change | Today                          |
# 	| Screening Status                  | Ceased                         |
# 	| Screening Status Reason           | Informed Dissent (verbal only) |
# 	| Subject Lower FOBT Age            | NOT: default                   |
# 	| Surveillance Due Date             | Null                           |


# Scenario: Test 6 - Subject has agex attribute set, has episode started since agex attribute was set, manual cease with confirmation (disclaimer) - agex attribute remains set
# Given I log in to BCSS "England" as user role "Hub Manager"
# 	And there is a subject who meets the following criteria:
# 	| Has GP Practice           | Yes - Active |
# 	| Latest episode status     | Open         |
# 	| Screening Status          | Call         |
# 	| Subject Has FOBT Episodes | Yes          |
# 	| Subject Lower FOBT Age    | NOT: default |	
# When I view the subject
# 	And I close the subject's episode for "Cease Request"
# 	And I manually cease the subject with reason "Informed Dissent"
# 	And I view the subject
# Then my subject has been updated as follows:
# 	| Ceased confirmation date          | Today            |
# 	| Clinical reason for cease         | Null             |
# 	| Screening Due Date                | Null             |
# 	| Screening Due Date Reason         | Ceased           |
# 	| Screening Due Date Date of change | Today            |
# 	| Screening Status                  | Ceased           |
# 	| Screening Status Reason           | Informed Dissent |
# 	| Subject Lower FOBT Age            | NOT: default     |
# 	| Surveillance Due Date             | Null             |
