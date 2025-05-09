from playwright.sync_api import Page
from pages.base_page import BasePage
from enum import Enum


class InvestigationDatasetsPage(BasePage):
    """Investigation Datasets Page locators, and methods for interacting with the page"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Colonoscopy datasets page locators
        self.site_lookup_link = self.page.locator("#UI_SITE_SELECT_LINK")
        self.select_options = self.page.locator('[id^="UI_RESULTS_"]')
        self.pracitioner_link = self.page.locator("#UI_SSP_PIO_SELECT_LINK")
        self.testing_clinician_link = self.page.locator(
            "#UI_CONSULTANT_PIO_SELECT_LINK"
        )
        self.aspirant_endoscopist_link = self.page.locator(
            "#UI_ASPIRANT_ENDOSCOPIST_PIO_SELECT_LINK"
        )
        self.show_drug_informations_detail = self.page.locator("#anchorDrug")
        self.drug_type_option1 = self.page.locator("#UI_BOWEL_PREP_DRUG1")
        self.drug_type_dose1 = self.page.locator("#UI_BOWEL_PREP_DRUG1")
        self.show_enscopy_information_details = self.page.locator("#anchorColonoscopy")
        self.enscope_inserted_yes = self.page.locator("#radScopeInsertedYes")
        self.theraputic_procedure_type = self.page.get_by_role(
            "radio", name="Therapeutic"
        )
        self.bowel_preparation_quality_option = self.page.get_by_label(
            "Bowel preparation quality"
        )
        self.comfort_during_examination_option = self.page.get_by_label(
            "Comfort during examination"
        )
        self.comfort_during_recovery_option = self.page.get_by_label(
            "Comfort during recovery"
        )

    def select_site_lookup_option(self, option: str) -> None:
        """
        This method is designed to select a site from the site lookup options.
        It clicks on the site lookup link and selects the given option.

        Args:
            option (str): The option to select from the aspirant endoscopist options.
        """
        self.click(self.site_lookup_link)
        self.select_options.select_option(option)

    def select_practitioner_option(self, option: str) -> None:
        """
        This method is designed to select a practitioner from the practitioner options.
        It clicks on the practitioner link and selects the given option.

        Args:
            option (str): The option to select from the aspirant endoscopist options.
        """
        self.click(self.pracitioner_link)
        self.select_options.select_option(option)

    def select_testing_clinician_option(self, option: str) -> None:
        """
        This method is designed to select a testing clinician from the testing clinician options.
        It clicks on the testing clinician link and selects the given option.

        Args:
            option (str): The option to select from the aspirant endoscopist options.
        """
        self.click(self.testing_clinician_link)
        self.select_options.select_option(option)

    def select_aspirant_endoscopist_option(self, option: str) -> None:
        """
        This method is designed to select an aspirant endoscopist from the aspirant endoscopist options.
        It clicks on the aspirant endoscopist link and selects the given option.

        Args:
            option (str): The option to select from the aspirant endoscopist options.
        """
        self.click(self.testing_clinician_link)
        self.select_options.select_option(option)

    def click_show_drug_information(self) -> None:
        """
        This method is designed to click on the show drug information link.
        It clicks on the show drug information link.
        """
        self.click(self.show_drug_informations_detail)

    def select_drug_type_option1(self, option: str) -> None:
        """
        This method is designed to select a drug type from the first drug type options.
        It clicks on the drug type option and selects the given option.

        Args:
            option (str): The option to select from the aspirant endoscopist options.
        """
        self.drug_type_option1.select_option(option)

    def fill_dtrug_type_dose1(self, dose: str) -> None:
        """
        This method is designed to fill in the drug type dose for the first drug type options.
        It fills in the given dose.

        Args:
            dose (str): The dose to fill in for the drug type.
        """
        self.click(self.drug_type_dose1)
        self.drug_type_dose1.fill(dose)

    def click_show_enscopy_information(self) -> None:
        """
        This method is designed to click on the show endoscopy information link.
        It clicks on the show endoscopy information link.
        """
        self.click(self.show_enscopy_information_details)

    def check_enscope_inserted_yes(self) -> None:
        """
        This method is designed to check the endoscope inserted yes option.
        It checks the endoscope inserted yes option.
        """
        self.enscope_inserted_yes.check()

    def select_theraputic_procedure_type(self) -> None:
        """
        This method is designed to select the therapeutic procedure type.
        It selects the therapeutic procedure type.
        """
        self.theraputic_procedure_type.check()

    def select_bowel_preparation_quality_option(self, option: str) -> None:
        """
        This method is designed to select a bowel preparation quality option.
        It selects the given option.

        Args:
            option (str): The option to select from the bowel preparation quality options.
        """
        self.bowel_preparation_quality_option.select_option(option)

    def select_comfort_during_examination_option(self, option: str) -> None:
        """
        This method is designed to select a comfort during examination option.
        It selects the given option.

        Args:
            option (str): The option to select from the comfort during examination options.
        """
        self.comfort_during_examination_option.select_option(option)

    def select_comfort_during_recovery_option(self, option: str) -> None:
        """
        This method is designed to select a comfort during recovery option.
        It selects the given option.

        Args:
            option (str): The option to select from the comfort during recovery options.
        """
        self.comfort_during_recovery_option.select_option(option)


class SiteLookupOptions(Enum):
    """Enum for site lookup options"""

    RL401 = "35317"
    RL402 = "42805"
    RL403 = "42804"
    RL404 = "42807"
    RL405 = "42808"


class PractitionerOptions(Enum):
    """Enum for practitioner options"""

    AMID_SNORING = "1251"
    ASTONISH_ETHANOL = "82"
    DEEP_POLL_DERBY = "2033"
    DOORFRAME_THIRSTY = "2034"


class TestingClinicianOptions(Enum):
    """Enum for testing clinician options"""

    BORROWING_PROPERTY = "886"
    CLAUSE_CHARTING = "918"
    CLUTTER_PUMMEL = "916"
    CONSONANT_TRACTOR = "101"


class AspirantEndoscopistOptions(Enum):
    """Enum for aspirant endoscopist options"""

    ITALICISE_AMNESTY = "1832"


class DrugTypeOptions(Enum):
    """Enum for drug type options"""

    BISACODYL = "200537~Tablet(s)"
    KLEAN_PREP = "200533~Sachet(s)"
    PICOLAX = "200534~Sachet(s)"
    SENNA_LIQUID = "203067~5ml Bottle(s)"
    SENNA = "200535~Tablet(s)"
    MOVIPREP = "200536~Sachet(s)"
    CITRAMAG = "200538~Sachet(s)"
    MANNITOL = "200539~Litre(s)"
    GASTROGRAFIN = "200540~Mls Solution"
    PHOSPHATE_ENEMA = "200528~Sachet(s)"
    MICROLAX_ENEMA = "200529~Sachet(s)"
    OSMOSPREP = "203063~Tablet(s)"
    FLEET_PHOSPHO_SODA = "203064~Mls Solution"
    CITRAFLEET = "203065~Sachet(s)"
    PLENVU = "305487~Sachet(s)"
    OTHER = "203066"


class BowelPreparationQualityOptions(Enum):
    """Enum for bowel preparation quality options"""

    EXCELLENT = "305579"
    GOOD = "17016"
    FAIR = "17017"
    POOR = "17995~Enema down scope~305582"
    INADEQUATE = "305581~~305582"


class ComfortOptions(Enum):
    """Enum for comfort during examination / recovery options"""

    NO_DISCOMFORT = "18505"
    MINIMAL_DISCOMFORT = "17273"
    MILD_DISCOMFORT = "17274"
    MODERATE_DISCOMFORT = "17275"
    SEVERE_DISCOMFORT = "17276"
