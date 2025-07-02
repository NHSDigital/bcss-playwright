# @BCSSAdditionalTests @LettersTests
# Feature: Letter Library

# Narrative Description: As a user of BCSS I am able to view national letter definitions, 
# and create local versions

# # Notes: In the Letter Library Index, when you click on a LETTER code, this takes you to the Version History
# # screen.  When you click on a CSV code, this takes you to the CSV File Format screen.

# #-------------------------------------------------------------------------------------------------
# # S83f : FIT self-referral letters:
# # 	S83f-ATT = pre-invitation letter
# # 	S83f = invitation letter
# # 	S83f-CSV = test kit details 

# Scenario: All three parts of the S83f letter exist
# Given I log in to BCSS "England" as user role "HubManager"
# When I view the letter library index
# And I filter the letter library index list to view the "Invitation Letters" letters group
# Then the "S83f" letter is listed in the letter library index
# And the "S83f-CSV" letter is listed in the letter library index
# And the "S83f-ATT" letter is listed in the letter library index

# Scenario: A current S83f FIT self-referral invitation and test kit letter exists and has the correct settings
# Given I log in to BCSS "England" as user role "HubManager"
# When I view the letter library index
# And I view the "S83f" letter definition
# And I pause to admire the view for "0" seconds
# Then the letter definition setting "Description" is "Invitation & Test Kit (Self-referral) (FIT)"
# And the letter definition setting "Letter Code" is "S83f"
# And the letter definition setting "Letter Group" is "Invitation Letters"
# And the letter definition setting "Letter Format" is "PDF-A4-V03"
# And the letter definition setting "Priority" is "High"
# And the letter definition setting "Destination" is "Patient"
# And the letter definition setting "Event Status" is "S83"
# And there "is" a current version of the selected letter definition

# Scenario: A current S83f-ATT FIT self-referral pre-invitation letter exists and has the correct settings
# Given I log in to BCSS "England" as user role "HubManager"
# When I view the letter library index
# And I view the "S83f-ATT" letter definition
# And I pause to admire the view for "0" seconds
# Then the letter definition setting "Description" is "Pre-invitation (Self-referral) (FIT)"
# And the letter definition setting "Letter Code" is "S83f-ATT"
# And the letter definition setting "Letter Group" is "Invitation Letters"
# And the letter definition setting "Letter Format" is "PDF-A4-V03"
# And the letter definition setting "Priority" is "High"
# And the letter definition setting "Destination" is "Patient"
# And the letter definition setting "Event Status" is "S83"
# And there "is" a current version of the selected letter definition


# Scenario: As a hub manager, I can define a local version of the S83f FIT self-referral invitation & test kit letter
# Given I log in to BCSS "England" as user role "HubManager"
# When I view the letter library index
# And I view the "S83f" letter definition
# And I pause to admire the view for "0" seconds
# Given there "is not" a local version of the selected letter definition
# Then I can define a local version of the selected letter definition

# Scenario: As a hub manager, I can define a local version of the S83f-ATT FIT self-referral pre-invitation letter
# Given I log in to BCSS "England" as user role "HubManager"
# When I view the letter library index
# And I view the "S83f-ATT" letter definition
# And I pause to admire the view for "0" seconds
# Given there "is not" a local version of the selected letter definition
# Then I can define a local version of the selected letter definition

# # Manual Scenario: I set up a local version for S83f-ATT pre-invitation letter
# # Given I log in to BCSS England as user role Hub Manager
# # When I view the letter library index
# # And I view the S83f-ATT pre-invitation letter definition
# # Then I define a local version 

# #-------------------------------------------------------------------------------------------------
# # A183 : 1st Positive Appointment Requested letter

# Scenario: A current A183 letter exists and has the correct settings
# Given I log in to BCSS "England" as user role "HubManager"
# When I view the letter library index
# And I view the "A183" letter definition
# And I pause to admire the view for "0" seconds
# Then the letter definition setting "Description" is "Practitioner Clinic 1st Appointment"
# And the letter definition setting "Letter Code" is "A183"
# And the letter definition setting "Letter Group" is "Practitioner Clinic Letters"
# And the letter definition setting "Letter Format" is "PDF-A4-V03"
# And the letter definition setting "Priority" is "Urgent"
# And the letter definition setting "Destination" is "Patient"
# And the letter definition setting "Event Status" is "A183"
# And there "is" a current version of the selected letter definition
