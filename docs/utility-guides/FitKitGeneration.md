# Utility Guide: fit_kit_generation

The FitKitGeneration Utility provides methods to generate and manage FIT test kits for testing purposes.

## Table of Contents

- [Utility Guide: fit\_kit\_generation](#utility-guide-fit_kit_generation)
  - [Table of Contents](#table-of-contents)
  - [Using the FitKitGeneration Utility](#using-the-fitkitgeneration-utility)
  - [Required Arguments](#required-arguments)
  - [FitKitGeneration Specific Functions](#fitkitgeneration-specific-functions)
  - [Example Usage](#example-usage)
- [Call the example usage function](#call-the-example-usage-function)

## Using the FitKitGeneration Utility

To use the fit_kit_generation Utility, import the `fit_kit_generation` module, from the `utils` directory, into your test file and call it's methods from within your tests, as required.

## Required Arguments

The methods in this utility require specific arguments. Refer to the docstrings in the `fit_kit_generation.py` file for details on required and optional arguments.

## FitKitGeneration Specific Functions

The FitKitGeneration Utility includes methods for generating, validating, and managing FIT test kits. These methods are designed to streamline the process of creating test kits for various scenarios. Below are some key functions:

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

# Call the example usage function
example_usage()
