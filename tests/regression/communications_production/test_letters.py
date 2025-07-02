# Feature: Letters

# Manual Scenario: I have a letter for a subject with a long name
# Given I log in to BCSS England as user role Hub Manager
# When I have a subject with a long name
# And I view a letter for the subject
# Then the subject title, forename and surname is not split over multiple lines unnecessarily

# Manual Scenario: I have a letter that might go over 2 pages
# Given I log in to BCSS England as user role Hub Manager
# When I have conditions which might affect the letter length e.g. subject with a long name, GP Endorsement, GP long name, line breaks
# And I view a letter for the subject
# Then the letter does not spread over two pages
