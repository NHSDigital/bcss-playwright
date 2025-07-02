# @BCSSAdditionalTests @LettersTests
# Feature: Basic Archived Batch List functionality

# Scenario: Check headings on Archived Batch List Screen
# Given I log in to BCSS "England" as user role "HubManager"
# When I view the archived batch list
# Then the table contains a sortable and filterable column for "ID"
# And the table contains a sortable and filterable column for "Type"
# And the table contains a sortable and filterable column for "Original"
# And the table contains a sortable and filterable column for "Letter Group"
# And the table contains a sortable and filterable column for "Event Code"
# And the table contains a sortable and filterable column for "Description"
# And the table contains a sortable and filterable column for "Batch Split By"
# And the table contains a sortable and filterable column for "Screening Centre"
# And the table contains a sortable and filterable column for "Status"
# And the table contains a sortable and filterable column for "Priority"
# And the table contains a sortable and filterable column for "Date On Letter"
# And the table contains a sortable and filterable column for "Date Archived"
# And the table contains a sortable and filterable column for "Count"


# Scenario: Check navigation from Archived Batch List Screen to Manage Archived Batch Screen
# Given I log in to BCSS "England" as user role "HubManager"
# When I view the archived batch list
# And I select an archived batch
# Then I view the details of an archived batch
