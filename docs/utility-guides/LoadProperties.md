# Utility Guide: Load Properties

The Load Properties Utility can be used to retrieve values from a properties file.

## Table of Contents

- [Utility Guide: Load Properties](#utility-guide-load-properties)
  - [Table of Contents](#table-of-contents)
  - [How This Works](#how-this-works)
  - [Example Usage - Properties files use key value pairs and the reason for using it is to avoid hard coded values in our tests](#example-usage---properties-files-use-key-value-pairs-and-the-reason-for-using-it-is-to-avoid-hard-coded-values-in-our-tests)
  - [Using the Load Properties Utility](#using-the-load-properties-utility)
  - [Example usage](#example-usage)

## How This Works

This utility uses the `jproperties` package to load the properties files.<br>
There is a class `PropertiesFile`, containing the locations of both files:

1. `self.smokescreen_properties_file`: tests/smokescreen/bcss_smokescreen_tests.properties
2. `self.general_properties_file`: tests/bcss_tests.properties

The method `get_properties()` will load either one of these based on the input provided.<br>
To ensure that there are no mistakes when providing this input there are two additional methods to call that will do this for you:

1. `get_smokescreen_properties()`: Which will load `self.smokescreen_properties_file`
2. `get_general_properties()`: Which will load `self.general_properties_file`

To add values to the properties file follow the format:

## Example Usage - Properties files use key value pairs and the reason for using it is to avoid hard coded values in our tests

```python
from utils.load_properties import PropertiesFile
# Create an instance of the PropertiesFile class
    properties = PropertiesFile()

# Load smokescreen properties
    smokescreen_props = properties.get_smokescreen_properties()
    print(smokescreen_props["example_value_1"])

# Load general properties
    general_props = properties.get_general_properties()
    print(general_props["example_value_2"])
```

## Using the Load Properties Utility

To use this utility in a test reference the pytest fixture in `conftest.py`.<br>
There is no need to import anything as any fixtures in `conftest.py` will be automatically discovered by pytest.
Here there are two fixtures:

1. `smokescreen_properties` - which is used to load the file: tests/smokescreen/bcss_smokescreen_tests.properties
2. `get_general_properties` - which is used to load the file: tests/bcss_tests.properties

## Example usage

```python
    def test_example_1(page: Page, general_properties: dict) -> None:
        print(
            general_properties["example_value_1"]
        )
```
