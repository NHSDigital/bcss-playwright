# Utility Guide: FitKitGeneration

The FitKitGeneration Utility provides methods to generate and manage FIT test kits for screening purposes.

## Table of Contents

- [Utility Guide: FitKitGeneration](#utility-guide-fitkitgeneration)
  - [Table of Contents](#table-of-contents)
  - [Using the FitKitGeneration Utility](#using-the-fitkitgeneration-utility)
  - [Required Arguments](#required-arguments)
  - [Example Usage](#example-usage)
  - [FitKitGeneration Specific Functions](#fitkitgeneration-specific-functions)

## Using the FitKitGeneration Utility

To use the fit_kit_generation Utility, import the `fit_kit_generation` module into your test file and call it's methods from within your tests, as required

## Required Arguments

The methods in this utility require specific arguments. Refer to the docstrings in the `fit_kit_generation.py` file for details on required and optional arguments.

## Example Usage

from utils.fit_kit_generation import FitKitGenerator

def test_generate_fit_kit() -> None:
    fit_kit = FitKitGenerator().generate_kit(batch_id=12345, kit_type="Standard")
    assert fit_kit is not None

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

    from utils.fit_kit_generation import FitKitGenerator

    def test_fit_kit_functions() -> None:
        # Generate a new FIT kit
        fit_kit = FitKitGenerator().generate_kit(batch_id=12345, kit_type="Standard")
        assert fit_kit["kit_type"] == "Standard"

        # Validate the generated kit
        is_valid = FitKitGenerator().validate_kit(kit_id=fit_kit["kit_id"])
        assert is_valid

        # Manage multiple kits
        FitKitGenerator().manage_kits(action="activate", kit_ids=[fit_kit["kit_id"]])
        