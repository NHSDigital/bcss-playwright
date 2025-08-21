import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from enum import Enum
from utils.calendar_picker import CalendarPicker


class SubjectSearchPage:
    def __init__(self, page: Page):
        self.page = page
        self.surname_field = self.page.locator("#A_C_Surname")
        self.forename_field = self.page.locator("#A_C_Forename")
        self.screening_status_dropdown = self.page.locator("#A_C_ScreeningStatus")
        self.episode_status_dropdown = self.page.locator("#A_C_EpisodeStatus")
        self.search_button = self.page.get_by_role("button", name="Search")
        self.back_link = self.page.get_by_role("link", name="Back", exact=True)

    def search_subject(self, surname: str, forename: str, screening_status: str, episode_status: str):
        self.surname_field.fill(surname)
        self.forename_field.fill(forename)
        self.screening_status_dropdown.select_option(screening_status)
        self.screening_status_dropdown.click()
        self.search_button.click()
        self.back_link.click()
        self.episode_status_dropdown.select_option(episode_status)
        self.search_button.click()
        self.back_link.click()
