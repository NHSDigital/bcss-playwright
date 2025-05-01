from playwright.sync_api import Page
from pages.base_page import BasePage
from enum import Enum


class ColonoscopyDatasetsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Colonoscopy datasets page locators
        self.show_dataset_button = self.page.get_by_role("link", name="Show Dataset")

        self.save_dataset_button = self.page.locator(
            "#UI_DIV_BUTTON_SAVE1"
        ).get_by_role("button", name="Save Dataset")

        self.select_asa_grade_dropdown = self.page.get_by_label("ASA Grade")

        self.select_fit_for_colonoscopy_dropdown = self.page.get_by_label(
            "Fit for Colonoscopy (SSP)"
        )

        self.dataset_complete_radio_button_yes = self.page.get_by_role(
            "radio", name="Yes"
        )

        self.dataset_complete_radio_button_no = self.page.get_by_role(
            "radio", name="No"
        )

    def click_show_datasets(self) -> None:
        self.click(self.show_dataset_button)

    def save_dataset(self) -> None:
        self.click(self.save_dataset_button)

    def select_asa_grade_option(self, option: str) -> None:
        self.select_asa_grade_dropdowen.select_option(option)

    def select_fit_for_colonoscopy_option(self, option: str) -> None:
        self.select_fit_for_colonoscopy_dropdown.select_option(option)

    def click_dataset_complete_radio_button_yes(self) -> None:
        self.dataset_complete_radio_button_yes.check()

    def click_dataset_complete_radio_button_no(self) -> None:
        self.dataset_complete_radio_button_no.check()


class AsaGradeOptions(Enum):
    FIT = "17009"
    RELEVANT_DISEASE = "17010"
    RESTRICTIVE_DISEASE = "17011"
    LIFE_THREATENING_DISEASE = "17012"
    MORIBUND = "17013"
    NOT_APPLICABLE = "17014"
    NOT_KNOWN = "17015"


class FitForColonoscopySspOptions(Enum):
    YES = "17058"
    NO = "17059"
    UNABLE_TO_ASSESS = "17954"
