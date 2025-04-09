from playwright.sync_api import Page
from pages.base_page import BasePage
from enum import Enum
from utils.calendar_picker import CalendarPicker


class SubjectScreeningPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Subject Search Criteria - page filters
        self.episodes_filter = self.page.get_by_role("radio", name="Episodes")
        self.demographics_filter = self.page.get_by_role("radio", name="Demographics")
        self.datasets_filter = self.page.get_by_role("radio", name="Datasets")
        self.nhs_number_filter = self.page.get_by_role("textbox", name="NHS Number")
        self.surname_filter = self.page.locator("#A_C_Surname")
        self.soundex_filter = self.page.get_by_role("checkbox", name="Use soundex")
        self.forename_filter = self.page.get_by_role("textbox", name="Forename")
        self.date_of_birth_filter = self.page.locator("#A_C_DOB_From")
        self.data_of_birth_range_filter = self.page.get_by_role(
            "textbox", name="(for a date range, enter a to"
        )
        self.postcode_filter = self.page.get_by_role("textbox", name="Postcode")
        self.episode_closed_date_filter = self.page.get_by_role(
            "textbox", name="Episode Closed Date"
        )
        self.kit_batch_number_filter = self.page.get_by_role(
            "textbox", name="Kit Batch Number"
        )
        self.kit_number_filter = self.page.get_by_role("textbox", name="Kit Number")
        self.fit_device_id_filter = self.page.get_by_role(
            "textbox", name="FIT Device ID"
        )
        self.laboratory_name_filter = self.page.get_by_role(
            "textbox", name="Laboratory Name"
        )
        self.laboratory_test_date_filter = self.page.get_by_role(
            "textbox", name="Laboratory Test Date"
        )
        self.diagnostic_test_actual_date_filter = self.page.get_by_role(
            "textbox", name="Diagnostic Test Actual Date"
        )
        self.search_button = self.page.get_by_role("button", name="Search")
        self.clear_filters_button = self.page.get_by_role(
            "button", name="Clear Filters"
        )
        self.appropriate_code_filter = self.page.get_by_label("Appropriate Code")
        self.gp_practice_in_ccg_filter = self.page.get_by_label("GP Practice in CCG")

        self.select_screening_status = self.page.locator("#A_C_ScreeningStatus")
        self.select_episode_status = self.page.locator("#A_C_EpisodeStatus")
        self.select_search_area = self.page.locator("#A_C_SEARCH_DOMAIN")

        self.dob_calendar_picker = self.page.locator("#A_C_DOB_From_LinkOrButton")

    def click_clear_filters_button(self) -> None:
        self.click(self.clear_filters_button)

    def click_search_button(self) -> None:
        self.click(self.search_button)

    def click_episodes_filter(self) -> None:
        self.episodes_filter.check()

    def click_demographics_filter(self) -> None:
        self.demographics_filter.check()

    def click_datasets_filter(self) -> None:
        self.datasets_filter.check()

    def click_nhs_number_filter(self) -> None:
        self.click(self.nhs_number_filter)

    def click_surname_filter(self) -> None:
        self.click(self.surname_filter)

    def click_soundex_filter(self) -> None:
        self.soundex_filter.check()

    def click_forename_filter(self) -> None:
        self.click(self.forename_filter)

    def click_date_of_birth_filter(self) -> None:
        self.click(self.date_of_birth_filter)

    def click_date_of_birth_range_filter(self) -> None:
        self.click(self.data_of_birth_range_filter)

    def click_postcode_filter(self) -> None:
        self.click(self.postcode_filter)

    def click_episodes_closed_date_filter(self) -> None:
        self.click(self.episode_closed_date_filter)

    def click_kit_batch_number_filter(self) -> None:
        self.click(self.kit_batch_number_filter)

    def click_kit_number_filter(self) -> None:
        self.click(self.kit_number_filter)

    def click_fit_device_id_filter(self) -> None:
        self.click(self.fit_device_id_filter)

    def click_laboratory_name_filter(self) -> None:
        self.click(self.laboratory_name_filter)

    def click_laboratory_test_date_filter(self) -> None:
        self.click(self.laboratory_test_date_filter)

    def click_diagnostic_test_actual_date_filter(self) -> None:
        self.click(self.diagnostic_test_actual_date_filter)

    def select_screening_status_options(self, option: str) -> None:
        self.select_screening_status.select_option(option)

    def select_episode_status_option(self, option: str) -> None:
        self.select_episode_status.select_option(option)

    def select_search_area_option(self, option: str) -> None:
        self.select_search_area.select_option(option)

    def select_dob_using_calendar_picker(self, date) -> None:
        self.click(self.dob_calendar_picker)
        CalendarPicker(self.page).v1_calender_picker(date)


class ScreeningStatusSearchOptions(Enum):
    CALL_STATUS = "4001"
    INACTIVE_STATUS = "4002"
    RECALL_STATUS = "4004"
    OPT_IN_STATUS = "4003"
    SELF_REFERRAL_STATUS = "4005"
    SURVEILLANCE_STATUS = "4006"
    SEEKING_FURTHER_DATA_STATUS = "4007"
    CEASED_STATUS = "4008"
    BOWEL_SCOPE_STATUS = "4009"
    LYNCH_SURVEILLANCE_STATUS = "306442"
    LYNCH_SELF_REFERRAL_STATUS = "307129"


class LatestEpisodeStatusSearchOptions(Enum):
    OPEN_PAUSED_STATUS = "1"
    CLOSED_STATUS = "2"
    NO_EPISODE_STATUS = "3"


class SearchAreaSearchOptions(Enum):
    SEARCH_AREA_HOME_HUB = "01"
    SEARCH_AREA_GP_PRACTICE = "02"
    SEARCH_AREA_CCG = "03"
    SEARCH_AREA_SCREENING_CENTRE = "05"
    SEARCH_AREA_OTHER_HUB = "06"
    SEARCH_AREA_WHOLE_DATABASE = "07"
