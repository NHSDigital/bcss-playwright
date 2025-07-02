# @LettersTests
# Feature: Basic Manage Archived Batch functionality


# Scenario: I can take an archived batch, reprint it, then archive that new batch
# Given I log in to BCSS "England" as user role "HubManagerStateRegistered"
# When I view the archived batch list
# And I view the "Original" type archived letter batch for "S1" "Pre"
# And I reprint the archived letter batch
# And I prepare the letter batch
# And I retrieve and confirm the letters
# And my batch is now archived


# Scenario: Check that S1 has supplementary batches
# Given I log in to BCSS "England" as user role "HubManagerStateRegistered"
# When I view the letter library index
# And I filter the letter library index list to view the "Supplementary Letters" letters group
# And I ensure that I can create "S1" supplementary batches
# And I view the archived batch list
# And I view the "Original" type archived letter batch for "S1" "Pre"
# And I create a supplementary batch
# And I prepare the letter batch
# And I retrieve and confirm the letters
# And my batch is now archived
