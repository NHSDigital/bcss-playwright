# @LettersTests
# Feature: Basic Manage Active Batch functionality


# Scenario: I can prepare, retrieve and confirm a letter batch of any number of files
# The first open batch will be picked up for processing, regardless of letter type

# Given I log in to BCSS "England" as user role "HubManagerStateRegistered"
# When I view the active batch list
# And There are open letter batches to process in the active batch list
# Then I view the "Original" type "Open" status active letter batch for "" ""
# And I prepare the letter batch
# And I retrieve and confirm the letters
