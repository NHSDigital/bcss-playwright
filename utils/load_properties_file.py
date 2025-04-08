from jproperties import Properties
import os


class PropertiesFile():
    def __init__(self):
        self.compartment_properties_file = "tests/smokescreen/bcss_smokescreen_tests.properties"
        self.smokescreen_properties_file = "tests/bcss_tests.properties"


    def smokescreen_properties(self, type_of_properties_file: str) -> dict:
        """
        Reads the 'bcss_smokescreen_tests.properties' file or 'bcss_tests.properties' and populates a 'Properties' object depending on whether "compartment" is given
        Returns a dictionary of properties for use in tests.

        Returns:
            dict: A dictionary containing the values loaded from the 'bcss_smokescreen_tests.properties' file.
        """
        configs = Properties()
        path =  f"{os.getcwd()}/{self.compartment_properties_file if type_of_properties_file == "compartment" else self.smokescreen_properties_file}"
        with open(
            path, "rb"
            ) as read_prop:
            configs.load(read_prop)
        return configs.properties
