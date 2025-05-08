# Utility Guide: fit_kit_generation

The fit_kit_generation Utility provides methods to generate and manage FIT test kits for testing purposes.

## Table of Contents

- [Utility Guide: fit\_kit\_generation](#utility-guide-fit_kit_generation)
  - [Table of Contents](#table-of-contents)
  - [Using the fit\_kit\_generation Utility](#using-the-fit_kit_generation-utility)
  - [Required Arguments](#required-arguments)
  - [fit\_kit\_generation Specific Functions](#fit_kit_generation-specific-functions)
  - [fit\_kit\_generation Specific Functions](#fit_kit_generation-specific-functions-1)
  - [Example Usage](#example-usage)

## Using the fit_kit_generation Utility

To use the fit_kit_generation Utility, import the `fit_kit_generation` module, from the `utils` directory, into your test file and call its methods from within your tests, as required.

## Required Arguments

The methods in this utility require specific arguments. Below is a summary of the required arguments for key methods:
- `generate_kit`: Requires `batch_id` (int) and `kit_type` (str).
## fit_kit_generation Specific Functions

The fit_kit_generation Utility includes methods for generating, validating, and managing FIT test kits. These methods are designed to streamline the process of creating test kits for various scenarios. Below are some key functions:

1. **`create_fit_id_df(tk_type_id: int, hub_id: int, no_of_kits: int) -> DataFrame`**  
   Creates a DataFrame containing FIT kit IDs based on the provided parameters.  
   - **Arguments**:
     - `tk_type_id` (int): The type ID of the test kit.
     - `hub_id` (int): The hub ID associated with the kits.
     - `no_of_kits` (int): The number of kits to retrieve.
   - **Returns**: A pandas DataFrame with the FIT kit IDs.

2. **`calculate_check_digit(kit_id: str) -> str`**  
   Calculates and appends a check digit to the given kit ID.  
   - **Arguments**:
     - `kit_id` (str): The kit ID to process.
   - **Returns**: The kit ID with the appended check digit.

3. **`convert_kit_id_to_fit_device_id(kit_id: str) -> str`**  
   Converts a kit ID into a FIT Device ID.  
   - **Arguments**:
     - `kit_id` (str): The kit ID to convert.
   - **Returns**: The corresponding FIT Device ID.

## fit_kit_generation Specific Functions

The fit_kit_generation Utility includes methods for generating, validating, and managing FIT test kits. These methods are designed to streamline the process of creating test kits for various scenarios. Below are some key functions:

1. **`generate_kit(batch_id: int, kit_type: str) -> dict`**  
   Generates a FIT test kit with the specified batch ID and kit type.  
   - **Arguments**:
     - `batch_id` (int): The ID of the batch to which the kit belongs.
     - `kit_type` (str): The type of kit to generate (e.g., "Standard", "Advanced").
   - **Returns**: A dictionary containing the details of the generated kit.

2. **`validate_kit(kit_id: int) -> bool`**  
   Validates a FIT test kit by its ID.  
   - **Arguments**:
     - `kit_id` (int): The ID of the kit to validate.
   - **Returns**: `True` if the kit is valid, `False` otherwise.

3. **`manage_kits(action: str, kit_ids: list[int]) -> None`**  
   Performs bulk actions on a list of FIT test kits.  
   - **Arguments**:
     - `action` (str): The action to perform (e.g., "activate", "deactivate").
     - `kit_ids` (list[int]): A list of kit IDs to apply the action to.

## Example Usage

```python
from utils.fit_kit_generation import create_fit_id_df, calculate_check_digit, convert_kit_id_to_fit_device_id

def example_usage() -> None:
    # Example inputs
    tk_type_id = 1
    hub_id = 101
    no_of_kits_to_retrieve = 2

    # Step 1: Retrieve and process FIT kit data
    fit_kit_df = create_fit_id_df(tk_type_id, hub_id, no_of_kits_to_retrieve)
    print("Processed FIT Kit DataFrame:")
    print(fit_kit_df)

    # Step 2: Calculate a check digit for a single kit ID
    kit_id = "ABC123"
    kit_with_check_digit = calculate_check_digit(kit_id)
    print(f"Kit ID with Check Digit: {kit_with_check_digit}")

    # Step 3: Convert a kit ID to a FIT Device ID
    fit_device_id = convert_kit_id_to_fit_device_id(kit_with_check_digit)
    print(f"FIT Device ID: {fit_device_id}")

example_usage()
