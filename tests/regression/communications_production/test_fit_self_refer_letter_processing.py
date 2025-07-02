# @BCSSAdditionalTests
# Feature: FIT Self Refer - letter processing

# Narrative Description: When a self-referral subject is invited for FOBT screening, they are entered into
# an S83f letter batch.  This batch comprises the S83f and S83f-ATT letters, and the S83f-CSV (test kit) file.
# When the batch is prepared and confirmed, the subject is progressed to status S84, and links to both the S83f 
# and S83f-ATT letters are displayed in their event history, in the S84 event.

# # NOTES
# # This feature file assumes that the default kit type for all SC invitations is FIT, so all self-referrals will be sent a FIT kit.
# # Because the smokescreen tests also generate invitations, this feature file was consistently failing due to the invitations for
# # hub BCS01 being right up to date, i.e. no more invitations were allowed to be generated.  To fix this, this feature file has
# # been changed to use hub BCS02 instead.

# Scenario: Self-refer a subject in my hub for FIT
# Given I log in to BCSS "England" as user role "HubManagerAtBCS02"
# And there are "currently" "no" self-refer subjects ready to invite
# And I have a subject with no screening history who is eligible to self refer
# When I view the subject 
# And I self refer the subject
# And I send a new kit to the subject
# And the FOBT invitations shortlist is refreshed
# Then there are "now" "some" self-refer subjects ready to invite
# And I pause to admire the view for "0" seconds

# Scenario: Invite a self-refer subject for FIT creates or updates an S83f letter batch
# Given I log in to BCSS "England" as user role "HubManagerAtBCS02"
# And there are "currently" "some" self-refer subjects ready to invite
# When I generate invitations
# And I view the active batch list
# And I filter the active batch list to view only "Original" type batches
# And I filter the active batch list to view only "Open" status batches
# And I pause to admire the view for "0" seconds
# Then There is "now" a letter batch for "S83" "Invitation & Test Kit (Self-referral) (FIT)"

# # Note that this "When I view ..." includes 3 steps from above (view active batch list, and filter by type and status), and clicks the batch ID link
# Scenario: There are 3 components in the S83f letter batch
# Given I log in to BCSS "England" as user role "HubManagerAtBCS02"
# When I view the active batch list
# And I view the "Original" type "Open" status active letter batch for "S83" "Invitation & Test Kit (Self-referral) (FIT)"
# And I pause to admire the view for "0" seconds
# Then letter type "Invitation & Test Kit (Self-referral) (FIT)" with file format "PDF-A4-V03" is listed
# And letter type "Pre-invitation (Self-referral) (FIT)" with file format "PDF-A4-V03" is listed
# And letter type "Invitation & Test Kit (Self-referral) (FIT)" with file format "FIT-KIT-CSV" is listed

# Scenario: Before confirming the S83f letter batch the self-referred subject's latest event status is S83
# Given I log in to BCSS "England" as user role "HubManagerAtBCS02"
# When I view the active batch list
# And I view the "Original" type "Open" status active letter batch for "S83" "Invitation & Test Kit (Self-referral) (FIT)"
# And I identify a subject who is in the letter batch
# And I view the subject
# And I pause to admire the view for "0" seconds
# Then the subject is at latest event status "S83 - Selected for Screening (Self-referral)"

# # Manual scenario: I can process the letter batch
# # Given I log in to BCSS England as user role Hub Manager
# # When I view an active S83f letter batch
# # Then I can prepare the batch
# # And I can retrieve and confirm each of the 3 components
# # And I can tell which is the pre-invitation letter and which is the invitation letter

# Scenario: When the S83f batch has been confirmed the self-referred subject has a self-referral invitation and test kit sent
# Given I log in to BCSS "England" as user role "HubManagerAtBCS02"
# When I view the active batch list
# And I view the "Original" type "Open" status active letter batch for "S83" "Invitation & Test Kit (Self-referral) (FIT)"
# And I identify a subject who is in the letter batch
# And I prepare the letter batch
# And I retrieve and confirm the letters
# And I view the subject
# And I pause to admire the view for "0" seconds
# Then the subject is at latest event status "S84 - Invitation and Test Kit Sent (Self-referral)"
# And the latest "S84 - Invitation and Test Kit Sent (Self-referral)" event shows "2" "View Letter" links

# # Manual scenario: The letters can be accessed via the subject episode history
# # Given I log in to BCSS England as user role Hub Manager
# # When I view the latest episode history of a FIT self-referral subject
# # And I view both letters
# # And I can see that one is a pre-invitation letter and one is an invitation letter
# # And the text of each is as expected
