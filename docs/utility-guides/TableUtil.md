# Utility Guide: Table Utility

The Table Utilities module provides helper functions to interact with and validate HTML tables in Playwright-based UI tests.

## Table of Contents

- [Utility Guide: Table Utility](#utility-guide-table-utility)
  - [Table of Contents](#table-of-contents)
    - [Get Column Index](#get-column-index)
      - [Required Arguments](#required-arguments)
      - [How This Function Works](#how-this-function-works)
    - [Click first link in Column](#click-first-link-in-column)
      - [Required Arguments](#required-arguments-1)
      - [How This Function Works](#how-this-function-works-1)
    - [Click first input in Column](#click-first-input-in-column)
      - [Required Arguments](#required-arguments-2)
      - [How This Function Works](#how-this-function-works-2)
    - [\_format\_inner\_text](#_format_inner_text)
      - [Required Arguments](#required-arguments-3)
      - [How This Function Works](#how-this-function-works-3)
    - [get\_table\_headers](#get_table_headers)
      - [Required Arguments](#required-arguments-4)
      - [How This Function Works](#how-this-function-works-4)
    - [get\_row\_count](#get_row_count)
      - [Required Arguments](#required-arguments-5)
      - [How This Function Works](#how-this-function-works-5)
    - [pick\_row](#pick_row)
      - [Required Arguments](#required-arguments-6)
      - [How This Function Works](#how-this-function-works-6)
    - [pick\_random\_row](#pick_random_row)
      - [Required Arguments](#required-arguments-7)
      - [How This Function Works](#how-this-function-works-7)
    - [pick\_random\_row\_number](#pick_random_row_number)
      - [Required Arguments](#required-arguments-8)
      - [How This Function Works](#how-this-function-works-8)
    - [get\_row\_data\_with\_headers](#get_row_data_with_headers)
      - [Required Arguments](#required-arguments-9)
      - [How This Function Works](#how-this-function-works-9)
    - [get\_full\_table\_with\_headers](#get_full_table_with_headers)
      - [Required Arguments](#required-arguments-10)
      - [How This Function Works](#how-this-function-works-10)

### Get Column Index

This function returns the index (1-based) of a specified column name.

#### Required Arguments

-`column_name`:
 -Type: `str`
 -The visible header text of the column to locate.

#### How This Function Works

1. Attempts to identify table headers from <thead> or <tbody>.
2. Iterates through header cells and matches text with `column_name`.
3. Returns the index if found, otherwise raises an error.

### Click first link in Column

Clicks on the first hyperlink present in a specified column.

#### Required Arguments

-`column_name`:
 -Type: `str`
 -The column in which the link needs to be found.

#### How This Function Works

1. Finds the index of the specified column.
2. Searches the first visible row in the column for an <a> tag.
3. Clicks the first available link found.

### Click first input in Column

Clicks on the first input element (e.g., checkbox/radio) in a specific column.

#### Required Arguments

-`column_name`:
 -Type: `str`
 -The name of the column containing the input element.

#### How This Function Works

1. Locates the index of the specified column.
2. Checks the first visible row for an <input> tag in that column.
3. Clicks the first input found.

### _format_inner_text

Formats inner text of a row string into a dictionary.

#### Required Arguments

-data:
 -Type: `str`
 -Raw inner text of a table row (tab-delimited).

#### How This Function Works

1. Splits the string by tab characters (\t).
2. Enumerates the result and maps index to cell value.
3. Returns a dictionary representing the row.

### get_table_headers

Extracts and returns table headers.

#### Required Arguments

-None

#### How This Function Works

1. Selects the first row inside <thead> (if available).
2. Captures the visible text of each <th>.
3. Returns a dictionary mapping index to header text.

### get_row_count

Returns the count of visible rows in the table.

#### Required Arguments

-None

#### How This Function Works

1. Locates all <tr> elements inside <tbody>.
2. Filters to include only visible rows.
3. Returns the total count.

### pick_row

Returns a locator for a specific row.

#### Required Arguments

-`row_number`:
 -Type: `int`
 -The row index to locate (1-based).

#### How This Function Works

1. Builds a locator for the nth <tr> inside <tbody>.
2. Returns the locator object.

### pick_random_row

Picks and returns a random row locator.

#### Required Arguments

None

#### How This Function Works

1. Gets all visible rows inside <tbody>.
2. Uses a secure random generator to pick one.
3. Returns the locator for that row.

### pick_random_row_number

Returns the number of a randomly selected row.

#### Required Arguments

None

#### How This Function Works

1. Retrieves visible rows from <tbody>.
2. Randomly selects an index using secrets.choice.
3. Returns the numeric index.

### get_row_data_with_headers

Returns a dictionary of header-value pairs for a given row.

#### Required Arguments

-`row_number`:
 -Type:int
 -Index of the target row (1-based).

#### How This Function Works

1. Extracts text from the specified row.
2. Retrieves headers using get_table_headers.
3. Maps each cell to its respective header.

### get_full_table_with_headers

Constructs a dictionary of the entire table content.

#### Required Arguments

-None

#### How This Function Works

1. Gets all visible rows.
2. Retrieves headers once.
3. Loops over each row and builds a dictionary using get_row_data_with_headers.
4. Returns a dictionary where each key is a row number.
