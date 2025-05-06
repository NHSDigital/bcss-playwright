# Utility Guide: Table Util

The Table Utilities module provides helper functions to interact with and validate HTML tables in Playwright-based UI tests.

## Table of Contents

- [Utility Guide: Table Util](#utility-guide-table-util)
  - [Table of Contents](#table-of-contents)
  - [Functions Overview](#functions-overview)
    - [Get Column Index](#get-column-index)
      - [Required Arguments](#required-arguments)
      - [How This Function Works](#how-this-function-works)

## Functions Overview

For this utility we have the following functions:

- `get_column_index`
- `click_first_link_in_column`
- `click_first_input_in_column`

### Get Column Index

This function returns the index (1-based) of a specified column name.

#### Required Arguments

-'column_name':
 -Type: 'str'
 -The visible header text of the column to locate.

#### How This Function Works

1. Attempts to identify table headers from <thead> or <tbody>.
2. Iterates through header cells and matches text with column_name.
3. Returns the index if found, otherwise raises an error.
